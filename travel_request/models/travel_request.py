# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class TravelRequest(models.Model):
    _name = 'travel.request'
    _description = 'Travel Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    # --- Header Information ---
    name = fields.Char(string='Request Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=lambda self: self.env.user.employee_id, tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id', store=True, readonly=True)
    job_title = fields.Char(string='Job Title', related='employee_id.job_title', readonly=True)
    request_date = fields.Date(string='Request Date', default=fields.Date.context_today, required=True, readonly=True)

    # --- Trip Details ---
    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    destination = fields.Char(string='Destination', required=True, tracking=True)
    purpose = fields.Text(string='Business Purpose', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id, required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account / Project', tracking=True)

    # --- Financials ---
    estimated_cost = fields.Monetary(string='Total Estimated', currency_field='currency_id', compute='_compute_total_cost', store=True, tracking=True)
    line_ids = fields.One2many('travel.request.line', 'request_id', string='Planned Expenses')
    
    cash_advance = fields.Monetary(string='Cash Advance', currency_field='currency_id', tracking=True)
    
    settlement_ids = fields.One2many('travel.settlement.line', 'request_id', string='Actual Expenses')
    total_actual_cost = fields.Monetary(string='Total Actual Spent', currency_field='currency_id', compute='_compute_settlement', store=True)
    difference_amount = fields.Monetary(string='Difference', currency_field='currency_id', compute='_compute_settlement', store=True)

    # --- Accounting Link ---
    account_move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, copy=False)
    move_line_ids = fields.One2many(related='account_move_id.line_ids', string='Journal Items', readonly=True)

    # --- Status ---
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted to Manager'),
        ('approved_manager', 'Manager Approved'),
        ('approved_hr', 'HR Approved'),
        ('approved_finance', 'Finance Approved (Ready to Go)'),
        ('settlement', 'Settlement / Reporting'),
        ('done', 'Done'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True, copy=False)

    approval_log_ids = fields.One2many('travel.approval.log', 'request_id', string='Approval Logs', readonly=True)

    # --- Logic (Updated to Odoo 18 Batch Standard) ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('travel.request') or _('New')
        return super(TravelRequest, self).create(vals_list)

    @api.depends('line_ids.amount')
    def _compute_total_cost(self):
        for record in self:
            record.estimated_cost = sum(line.amount for line in record.line_ids)

    @api.depends('settlement_ids.amount', 'cash_advance')
    def _compute_settlement(self):
        for record in self:
            actual = sum(line.amount for line in record.settlement_ids)
            record.total_actual_cost = actual
            record.difference_amount = actual - record.cash_advance

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError(_("End Date cannot be earlier than Start Date."))

    def _log_approval(self, stage, comment=""):
        self.ensure_one()
        self.env['travel.approval.log'].create({
            'request_id': self.id,
            'user_id': self.env.user.id,
            'activity_type': stage,
            'log_date': fields.Datetime.now(),
            'comment': comment
        })

    def _update_related_budget(self):
        for req in self:
            budget = self.env['travel.budget'].search([
                ('department_id', '=', req.department_id.id),
                ('date_start', '<=', req.start_date),
                ('date_end', '>=', req.start_date),
                ('active', '=', True)
            ], limit=1)
            if budget:
                budget.recompute_budget_usage()

    def action_view_journal_entry(self):
        self.ensure_one()
        return {
            'name': _('Journal Entry'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.account_move_id.id,
            'target': 'current',
        }

    # --- Workflow Buttons ---

    def action_submit(self):
        if not self.line_ids:
            raise UserError(_("Please add at least one estimated expense line before submitting."))
        self.state = 'submitted'
        self._log_approval('Submission', 'Submitted for Manager Approval.')

    def action_approve_manager(self):
        self.state = 'approved_manager'
        self._log_approval('Manager Approval', 'Approved by Manager.')

    def action_approve_hr(self):
        self.state = 'approved_hr'
        self._log_approval('HR Approval', 'Approved by HR. Policy Checked.')

    def action_approve_finance(self):
        self.ensure_one()
        budget = self.env['travel.budget'].search([
            ('department_id', '=', self.department_id.id),
            ('date_start', '<=', self.start_date),
            ('date_end', '>=', self.start_date),
            ('active', '=', True)
        ], limit=1)
        
        if not budget:
            raise UserError(_("No active budget found for %s department in this period.") % self.department_id.name)
        
        remaining = budget.remaining_amount 
        if self.estimated_cost > remaining:
            raise ValidationError(_("Budget Exceeded! Request: %s, Remaining Budget: %s") % (self.estimated_cost, remaining))

        self.state = 'approved_finance'
        self._log_approval('Finance Approval', 'Approved by Finance. Budget Verified.')
        self._update_related_budget()

    def action_return_from_trip(self):
        self.state = 'settlement'
        self._log_approval('Trip Finished', 'User returned. Settlement started.')

    def action_done_settlement(self):
        self.ensure_one()
        if not self.analytic_account_id:
            raise UserError(_("Please select an Analytic Account / Project before finalizing settlement."))

        for line in self.settlement_ids:
            if line.amount <= 0:
                raise UserError(_("Actual Amount for '%s' cannot be 0.") % line.category)
            if not line.account_id:
                raise UserError(_("Missing Expense Account on line: %s. Please assign an account.") % line.category)
            if line.receipt_type == 'soft' and not line.attachment:
                raise UserError(_("Missing Attachment for '%s'. Please upload proof.") % line.category)

        partner = self.employee_id.user_id.partner_id or self.employee_id.work_contact_id
        if not partner:
            raise UserError(_("Cannot find a Contact/Partner for Employee %s.") % self.employee_id.name)

        journal = self.env.company.travel_journal_id
        if not journal:
            raise UserError(_(
                "Travel Journal is not configured!\n"
                "Please go to Corporate Travel -> Configuration -> Settings\n"
                "and select the Default Travel Journal."
            ))

        analytic_dist = {str(self.analytic_account_id.id): 100}
        move_lines = []
        
        payable_account = partner.property_account_payable_id
        if not payable_account:
            raise UserError(_("Partner '%s' has no Payable Account set.") % partner.name)

        for line in self.settlement_ids:
            move_lines.append((0, 0, {
                'name': f"{self.name} - {line.description}",
                'account_id': line.account_id.id,
                'debit': line.amount,
                'credit': 0.0,
                'partner_id': partner.id,
                'analytic_distribution': analytic_dist,
            }))
        
        move_lines.append((0, 0, {
            'name': f"Travel Settlement: {self.name}",
            'account_id': payable_account.id,
            'debit': 0.0,
            'credit': self.total_actual_cost,
            'partner_id': partner.id,
        }))

        move_vals = {
            'ref': self.name,
            'date': fields.Date.today(),
            'journal_id': journal.id,
            'line_ids': move_lines,
            'move_type': 'entry', 
        }
        move = self.env['account.move'].create(move_vals)
        move.action_post()
        
        self.account_move_id = move.id
        self.state = 'done'
        self._log_approval('Settlement Done', 'Settlement finalized. Journal Entry %s created.' % move.name)
        self._update_related_budget()

    # --- REJECTION LOGIC (Updated for Wizard) ---

    def action_reject(self):
        """ Membuka Popup Wizard """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Travel Request',
            'res_model': 'travel.reject.reason',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_reject_with_reason(self, reason):
        """ Dieksekusi oleh Wizard """
        self.state = 'rejected'
        self._log_approval('Rejection', reason)
        self._update_related_budget()

    def action_reset_draft(self):
        self.state = 'draft'
        self._log_approval('Reset', 'Reset to draft.')
        self._update_related_budget()


class TravelRequestLine(models.Model):
    _name = 'travel.request.line'
    _description = 'Travel Planned Expense'

    request_id = fields.Many2one('travel.request', string='Request', ondelete='cascade')
    
    product_id = fields.Many2one('product.product', string='Product', domain="[('type', '=', 'service')]")
    
    category = fields.Selection([
        ('hotel', 'Hotel'), ('flight', 'Flight'), ('train', 'Train'),
        ('bus', 'Bus'), ('allowance', 'Allowance'), ('other', 'Other')
    ], required=True)
    
    description = fields.Char(required=True)
    
    qty = fields.Float(string='Qty/Days', default=1.0, required=True)
    price_unit = fields.Float(string='Unit Price', required=True)
    
    amount = fields.Monetary(string='Total Amount', required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='request_id.currency_id')

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.description = self.product_id.name
            self.price_unit = self.product_id.standard_price
            self.amount = self.qty * self.price_unit

    @api.onchange('qty', 'price_unit')
    def _onchange_qty_price(self):
        self.amount = self.qty * self.price_unit


class TravelSettlementLine(models.Model):
    _name = 'travel.settlement.line'
    _description = 'Travel Actual Expense'

    request_id = fields.Many2one('travel.request', string='Request', ondelete='cascade')
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    
    product_id = fields.Many2one('product.product', string='Product', domain="[('type', '=', 'service')]")

    category = fields.Selection([
        ('hotel', 'Hotel'), ('flight', 'Flight'), ('train', 'Train'),
        ('bus', 'Bus'), ('allowance', 'Allowance'), ('other', 'Other')
    ], required=True)
    
    description = fields.Char(string='Description/Receipt Ref', required=True)
    
    qty = fields.Float(string='Qty/Days', default=1.0, required=True)
    price_unit = fields.Float(string='Unit Price', required=True)

    amount = fields.Monetary(string='Total Actual', required=True, currency_field='currency_id')
    
    account_id = fields.Many2one('account.account', string='Expense Account', domain="[('deprecated', '=', False), ('account_type', 'in', ('expense', 'income_other'))]")
    currency_id = fields.Many2one('res.currency', related='request_id.currency_id')
    
    receipt_type = fields.Selection([('soft', 'Soft File (Upload Required)'), ('hard', 'Hard File (Physical)')], string='Receipt Type', required=True, default='soft')
    attachment = fields.Binary(string='Attachment')
    attachment_name = fields.Char(string='File Name')

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.description = self.product_id.name
            self.price_unit = self.product_id.standard_price
            
            account = self.product_id.property_account_expense_id or self.product_id.categ_id.property_account_expense_categ_id
            if account:
                self.account_id = account.id
            
            self.amount = self.qty * self.price_unit

    @api.onchange('qty', 'price_unit')
    def _onchange_qty_price(self):
        self.amount = self.qty * self.price_unit


class TravelApprovalLog(models.Model):
    _name = 'travel.approval.log'
    _description = 'Travel Approval Log'
    _order = 'log_date desc'

    request_id = fields.Many2one('travel.request', string='Request', ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Approver', required=True)
    activity_type = fields.Char(string='Action', required=True)
    log_date = fields.Datetime(default=fields.Datetime.now, required=True)
    comment = fields.Text()