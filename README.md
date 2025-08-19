🕒 Time Off Module

📌 Overview
The Time Off module is a custom Odoo add-on designed to streamline employee leave and time-off management.
It enables employees to request leave, managers to approve or refuse requests, and HR to track leave balances efficiently.

✨ Features
📝 Leave Requests – Employees can submit and manage their leave requests.

✅ Approval Workflow – Managers can approve or refuse leave requests.

💬 Refusal Wizard – Managers can provide detailed feedback when refusing requests.

📄 Custom Views – Tailored forms and list views for efficient leave management.

🔒 Role-based Access Control – Specific access rights for different user roles.

🌍 Multilingual Support – Includes French translation.

🛠 Main Components
* Models
hr_leave.py – Core logic for leave requests, validation, and state transitions.

* Wizards
leave_refuse_wizard.py – Wizard interface for managers to refuse leave with a reason.

* Views
hr_leave_views.xml – Customized leave request forms and list views.

leave_refuse_wizard_views.xml – Interface for the leave refusal wizard.

* Security
ir.model.access.csv – Defines access rights for various user roles.

