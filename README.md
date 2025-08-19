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


---

# 🔐 Authentification pour Candidature

**1**  

<p align="center">
  <img width="1871" height="931" alt="Authentication Step 2" src="https://github.com/user-attachments/assets/9be9af8b-4e5c-498d-8fd1-2087d7ed4c9e" />
</p>


**2**  

<p align="center">
  <img width="1879" height="946" alt="Authentication Step 1" src="https://github.com/user-attachments/assets/a4eb8d48-0c0b-4eef-935c-aeccdb0d0aef" />
</p>

---

## 🚀 Installation et Configuration

📥 **Étape 1 : Installation du module**  
📁 Placez le dossier du module dans votre répertoire `addons/`  
🔄 Redémarrez votre serveur Odoo  
🎯 Allez dans **Applications** → Recherchez **"Custom Job Redirect"**  
⬇️ Cliquez sur **Installer**  

---

🍪 **Étape 2 : Activation des cookies**  
Pour que la redirection fonctionne correctement, il est essentiel d'activer les cookies :  

🎛️ Allez dans **Configuration → Site Web → Paramètres**  
📑 Dans l'onglet **Fonctionnalités**, activez l'option **Cookies**  

<p align="center">
  <img width="1879" height="946" alt="Cookies Setting" src="https://github.com/user-attachments/assets/e9824525-5c47-4c50-8d57-c512ada95786" />
</p>

⚠️ *Important : Sans les cookies activés, la session utilisateur ne peut pas être maintenue et la redirection ne fonctionnera pas correctement.*  

---

👥 **Étape 3 : Activation du Compte Client**  
Pour permettre aux visiteurs de créer des comptes et de se connecter :  

🎛️ Allez dans **Configuration → Site Web → Paramètres**  
📑 Dans l'onglet **Fonctionnalités**, activez l'option **Compte Client**  

<p align="center">
  <img width="1879" height="946" alt="Client Account Setting" src="https://github.com/user-attachments/assets/93d96f57-7430-4798-b704-fc274c43ff4e" />
</p>

Cette option permet aux utilisateurs de :  
- 🆕 Créer un compte depuis la page de connexion  
- 👤 Gérer leur profil  
- 📋 Suivre leurs candidatures  

---

## 📁 Structure du module

```plaintext
custom_job_redirect/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py
└── README.md
```

---

## 🔄 Compatibilité
✅ Odoo 18.0

---

## 🆘 Support
Pour toute question ou problème :

✅ Vérifiez que toutes les étapes de configuration sont complétées  
🔍 Vérifiez la compatibilité avec votre version d'Odoo

---

## 📄 Licence
Ce module est distribué sous licence LGPL-3.

---

## 📌 Note
Ce module modifie le comportement standard d'Odoo pour les candidatures. Assu-vous de tester en environnement de développement avant de déployer en production.
