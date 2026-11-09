# Corporate Travel & Expense Management Suite for Odoo 18.0

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-714B67.svg?style=flat-square&logo=odoo&logoColor=white)](https://www.odoo.com)
[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg?style=flat-square)](https://www.gnu.org/licenses/lgpl-3.0)
[![Author: XodetiStudio](https://img.shields.io/badge/Author-XodetiStudio-06b6d4.svg?style=flat-square)](https://xodetistudio.id)
[![Category](https://img.shields.io/badge/Category-Human%20Resources%20%2F%20Expenses-orange.svg?style=flat-square)](https://xodetistudio.id)

A robust, enterprise-grade business trip governance and expense management module engineered for **Odoo 18.0 (Community and Enterprise Editions)**. Distributed **100% Free and Open Source** under the LGPL-3 license by **[XodetiStudio](https://xodetistudio.id)**.

---

## 🌟 Key Features

1. **Strict Departmental Budget Guardrails**
   - Automatically intercepts and validates requests against available department budgets.
   - Prevents over-spending before travel approvals are granted.

2. **4-Tier Approval Workflow**
   - **Employee**: Drafts travel plan, purpose, destination, and cost estimations.
   - **Direct Manager**: Reviews business justification and team schedule.
   - **HR Department**: Verifies travel policy compliance and company calendar.
   - **Finance**: Validates budget lines, issues cash advance, and reconciles GL journals.

3. **Standardized Expense Products & Accounting Integration**
   - Standard product items for Hotel, Flight, Transportation, and Per-Diem allowances.
   - Seamless generation of automated Journal Entries linked to Analytic Accounts (Cost Centers).

4. **Cash Advance & Settlement Reconciliation**
   - Handles employee cash advance requests and subsequent settlement with real expense receipts.
   - Automatically computes reimbursement balance or cash refund to the company.

5. **Official PDF Documentation**
   - One-click generation of official **Travel Duty Orders (Surat Tugas)** with formal signature blocks ready for archiving or digital signature.

---

## 📋 Technical Requirements & Dependencies

- **Odoo Version**: 18.0 (Community or Enterprise)
- **Dependencies**:
  - `base`
  - `hr`
  - `account`
  - `product`

---

## 🚀 Installation

1. Clone or download this repository.
2. Copy the `travel_request` folder into your Odoo `custom_addons` path.
3. Restart your Odoo server.
4. Enable **Developer Mode** in Odoo Settings.
5. Navigate to **Apps** &rarr; **Update Apps List**.
6. Search for `Corporate Travel & Expense Management` and click **Activate**.

---

## ⚙️ Configuration

1. Go to **Travel & Expenses** &rarr; **Configuration** &rarr; **Settings**.
2. Select your default **Travel Journal** for financial settlement entries.
3. Define department travel budgets under **Travel & Expenses** &rarr; **Budgets**.
4. Configure approval roles under **Settings** &rarr; **Users & Companies** &rarr; **Users** (Travel User / Manager / HR / Finance).

---

## 💼 Explore Flagship Enterprise Suites by XodetiStudio

Need mission-critical commercial solutions for your enterprise? Explore our flagship suites:

| Suite | Description | Pricing |
| :--- | :--- | :--- |
| **[Docu eSign Suite](https://xodetistudio.id/?deck=esign)** | PAdES-B-LT Cryptographic PDF Signing, Statutory PERURI e-Materai (UU No. 10/2020), Drag-and-Drop Coordinate Designer, Smart PIN 2FA. Zero SaaS tolls. | €600 (One-Time) |
| **[PathSFA Suite](https://xodetistudio.id)** | Enterprise Offline-First Sales Force Automation Flutter Mobile App + Odoo 18 Backend: GPS visit tracking, order booking, stock check, anti-fraud telemetry. | €2,999 (One-Time) |
| **[PathTMS Suite](https://xodetistudio.id)** | Enterprise Fleet, Dispatch & Transport Management System: delivery optimization, driver companion mobile app, fuel accounting, digital POD. | €2,999 (One-Time) |

---

## 📞 Support, Customization & Consulting

Need custom workflows, multi-company rules, or integration with external travel booking platforms? XodetiStudio provides bespoke engineering and ERP implementation services.

- **Website**: [https://xodetistudio.id](https://xodetistudio.id)
- **WhatsApp**: [+62 878-9516-4590](https://wa.me/6287895164590?text=Halo%20XodetiStudio%2C%20saya%20tertarik%20konsultasi%20modul%20Travel%20Request.)
- **Email**: [info@xodetistudio.id](mailto:info@xodetistudio.id)

---

## 📄 License

This module is licensed under the **GNU Lesser General Public License v3.0 (LGPL-3)**.  
Copyright &copy; 2026 [XodetiStudio](https://xodetistudio.id). Engineered by Muhammad Thoriq.

