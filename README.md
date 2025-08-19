# 🕒 Time Off Module

## 📌 Overview
The **Time Off** module is a custom Odoo add-on designed to streamline employee leave and time-off management.  
It enables employees to request leave, managers to approve or refuse requests, and HR to track leave balances efficiently.

---

## ✨ Features
- 📝 **Leave Requests** – Employees can submit and manage their leave requests.  
- ✅ **Approval Workflow** – Managers can approve or refuse leave requests.  
- 💬 **Refusal Wizard** – Managers can provide detailed feedback when refusing requests.  
- 📄 **Custom Views** – Tailored forms and list views for efficient leave management.  
- 🔒 **Role-based Access Control** – Specific access rights for different user roles.  
- 🌍 **Multilingual Support** – Includes French translation.  

---

## 🛠 Main Components

### 📂 Models
- `hr_leave.py` – Core logic for leave requests, validation, and state transitions.  

### 📂 Wizards
- `leave_refuse_wizard.py` – Wizard interface for managers to refuse leave with a reason.  

### 📂 Views
- `hr_leave_views.xml` – Customized leave request forms and list views.  
- `leave_refuse_wizard_views.xml` – Interface for the leave refusal wizard.  

### 📂 Security
- `ir.model.access.csv` – Defines access rights for various user roles.  

---

# 📸 Module de Recrutement

### Étapes

**1**  
<p align="center">
  <img width="337" height="312" alt="Step 1" src="https://github.com/user-attachments/assets/bbe83434-d142-46ac-a09d-e9cb205deefe" />
</p>

**2**  
<p align="center">
  <img width="611" height="355" alt="Step 2" src="https://github.com/user-attachments/assets/19dffa2b-2f03-4dc5-a506-98482550748a" />
</p>

**3**  
<p align="center">
  <img width="611" height="355" alt="Step 3" src="https://github.com/user-attachments/assets/bf63a5d5-993f-40bc-941b-a51f6afa82f0" />
</p>

---

# 🌍 Changement de langue

**1**  
<p align="center">
  <img width="361" height="188" alt="Language Change Step 1" src="https://github.com/user-attachments/assets/6d90735f-b9ff-4c94-9250-5587c0cbb4ea" />
</p>

**2**  
<p align="center">
  <img width="796" height="242" alt="Language Change Step 2" src="https://github.com/user-attachments/assets/b0e63a30-cdb6-473c-b0ea-b5bc2fed2558" />
</p>
