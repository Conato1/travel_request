# -*- coding: utf-8 -*-
{
    'name': "Corporate Travel & Expense Management",
    'summary': """
        End-to-End Travel Request, Department Budget Control, Multi-Level Approval, and Automated Accounting Settlement.
    """,
    'description': """
Corporate Travel & Expense Management System
=============================================
A comprehensive corporate travel governance module engineered for Odoo 18.0 (Community & Enterprise).
Streamlines employee trip applications, departmental budget reservations, multi-tiered management approvals, 
and automated financial journal settlements.

Key Capabilities:
-----------------
* **Strict Budget Validation**: Real-time departmental budget check preventing over-budget trip requests.
* **Multi-Tier Approval Pipeline**: Configurable workflow across Employee -> Manager -> HR -> Finance.
* **Product & Service Costing**: Standardized product catalogs for flights, hotels, and per-diem allowances mapped to General Ledger (GL) accounts.
* **Cash Advance & Reconciliations**: Cash advance disbursements and reconciliation with actual expense receipts.
* **Automated Accounting Entries**: Automatic creation and posting of Journal Entries with appropriate Analytic Accounts.
* **Official PDF Documentation**: Instant generation of official Travel Duty Orders (Surat Tugas) and expense settlement sheets.

100% Free and Open Source under LGPL-3 by XodetiStudio (https://xodetistudio.id).
    """,
    'author': "XodetiStudio",
    'website': "https://xodetistudio.id",
    'category': 'Human Resources/Expenses',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',

    'depends': ['base', 'hr', 'account', 'product'],

    'data': [
        'security/ir.model.access.csv',
        'security/travel_security.xml',
        'data/ir_sequence_data.xml',
        'wizard/travel_reject_reason_views.xml',
        'views/res_config_settings_views.xml',
        'views/travel_request_views.xml',
        'views/travel_budget_views.xml',
        'views/travel_report.xml',
        'views/travel_menu_views.xml',
    ],

    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
}
