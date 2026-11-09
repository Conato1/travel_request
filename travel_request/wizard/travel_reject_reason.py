# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TravelRejectReason(models.TransientModel):
    _name = 'travel.reject.reason'
    _description = 'Travel Rejection Reason Wizard'

    reason = fields.Text(string='Reason for Rejection', required=True)

    def action_confirm(self):
        """
        Dipanggil saat user klik tombol 'Confirm' di popup.
        """
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        if active_id:
            request = self.env['travel.request'].browse(active_id)
            request.action_reject_with_reason(self.reason)
        
        return {'type': 'ir.actions.act_window_close'}