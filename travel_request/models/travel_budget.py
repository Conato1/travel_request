# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TravelBudget(models.Model):
    _name = 'travel.budget'
    _description = 'Travel Department Budget'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'

    name = fields.Char(
        string='Budget Title', 
        required=True, 
        tracking=True,
        help="E.g. IT Department Budget 2024"
    )

    department_id = fields.Many2one(
        'hr.department', 
        string='Department', 
        required=True, 
        tracking=True
    )

    date_start = fields.Date(
        string='Start Date', 
        required=True, 
        tracking=True
    )

    date_end = fields.Date(
        string='End Date', 
        required=True, 
        tracking=True
    )

    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency', 
        default=lambda self: self.env.company.currency_id, 
        required=True
    )

    budget_amount = fields.Monetary(
        string='Allocated Budget', 
        currency_field='currency_id', 
        required=True, 
        tracking=True
    )

    # --- Computed fields (STORED for Performance) ---
    total_spent = fields.Monetary(
        string='Total Spent', 
        currency_field='currency_id', 
        compute='_compute_budget_usage',
        store=True, # Fixed: Stored for high performance
        copy=False,
        tracking=True
    )

    remaining_amount = fields.Monetary(
        string='Remaining Budget', 
        currency_field='currency_id', 
        compute='_compute_budget_usage',
        store=True, # Fixed: Stored for high performance
        copy=False
    )

    active = fields.Boolean(
        string='Active', 
        default=True
    )

    @api.depends('budget_amount')
    def _compute_budget_usage(self):
        """
        Hitung penggunaan budget.
        Catatan: Karena store=True, method ini hanya jalan jika budget_amount berubah,
        ATAU dipanggil secara paksa oleh Travel Request (metode recompute_budget_usage).
        """
        for record in self:
            # Logic: Cari request yang approved/done di periode & dept ini
            domain = [
                ('department_id', '=', record.department_id.id),
                ('start_date', '>=', record.date_start), # Gunakan start_date trip
                ('end_date', '<=', record.date_end),
                ('state', 'in', ['approved_finance', 'settlement', 'done']) # Hanya hitung yang sudah cair
            ]
            
            # Sum cost dari request yang ditemukan
            requests = self.env['travel.request'].search(domain)
            spent = sum(req.total_actual_cost if req.total_actual_cost > 0 else req.estimated_cost for req in requests)
            
            record.total_spent = spent
            record.remaining_amount = record.budget_amount - spent

    def recompute_budget_usage(self):
        """
        Method publik untuk dipanggil dari model travel.request
        ketika ada request baru yang disetujui atau dibatalkan.
        """
        self._compute_budget_usage()

    @api.constrains('department_id', 'date_start', 'date_end')
    def _check_overlap(self):
        for record in self:
            domain = [
                ('id', '!=', record.id),
                ('department_id', '=', record.department_id.id),
                ('date_start', '<=', record.date_end),
                ('date_end', '>=', record.date_start),
                ('active', '=', True),
            ]
            if self.search_count(domain) > 0:
                raise ValidationError(_("You cannot have overlapping budgets for the same department (%s).") % record.department_id.name)