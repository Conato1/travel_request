# -*- coding: utf-8 -*-
from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    travel_journal_id = fields.Many2one(
        'account.journal', 
        string='Default Travel Journal',
        help="Journal used for Travel Settlements (e.g. Miscellaneous Operations)."
    )

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    travel_journal_id = fields.Many2one(
        related='company_id.travel_journal_id',
        string='Travel Journal',
        readonly=False
    )