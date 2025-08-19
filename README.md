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



<img width="1879" height="946" alt="image" src="https://github.com/user-attachments/assets/a4eb8d48-0c0b-4eef-935c-aeccdb0d0aef" /><img width="1871" height="931" alt="image" src="https://github.com/user-attachments/assets/9be9af8b-4e5c-498d-8fd1-2087d7ed4c9e" />


 🔐 Module Custom Job Redirect
📋 Description
Le module Custom Job Redirect 🚀 force l'authentification des utilisateurs avant de pouvoir postuler à une offre d'emploi. Ce module redirige automatiquement les utilisateurs non connectés vers la page de connexion lorsqu'ils tentent de postuler à un poste.
✨ Fonctionnalités

✅ Redirection automatique vers la page de connexion pour les utilisateurs non authentifiés
✅ Conservation de l'URL de destination après connexion
✅ Compatibilité avec les routes existantes d'Odoo HR Recruitment
✅ Logging détaillé pour le débogage

🛠️ Prérequis

📦 Odoo 15.0+ (ou version compatible)
🏢 Module website_hr_recruitment installé
👤 Module portal activé pour la gestion des comptes clients

🚀 Installation et Configuration
📥 Étape 1 : Installation du module

📁 Placez le dossier du module dans votre répertoire addons/
🔄 Redémarrez votre serveur Odoo
🎯 Allez dans Applications → Recherchez "Custom Job Redirect"
⬇️ Cliquez sur Installer

🍪 Étape 2 : Activation des cookies
Pour que la redirection fonctionne correctement, il est essentiel d'activer les cookies :

🎛️ Allez dans Configuration → Site Web → Paramètres
📑 Dans l'onglet Fonctionnalités, activez l'option Cookies
<img width="1879" height="946" alt="image" src="https://github.com/user-attachments/assets/e9824525-5c47-4c50-8d57-c512ada95786" />
⚠️ Important : Sans les cookies activés, la session utilisateur ne peut pas être maintenue et la redirection ne fonctionnera pas correctement.
👥 Étape 3 : Activation du Compte Client
Pour permettre aux visiteurs de créer des comptes et de se connecter :

🎛️ Allez dans Configuration → Site Web → Paramètres
📑 Dans l'onglet Fonctionnalités, activez l'option Compte Client
<img width="1879" height="946" alt="image" src="https://github.com/user-attachments/assets/93d96f57-7430-4798-b704-fc274c43ff4e" />
Cette option permet aux utilisateurs de :

🆕 Créer un compte depuis la page de connexion
👤 Gérer leur profil
📋 Suivre leurs candidatures

🎯 Utilisation
👥 Pour les visiteurs

🔍 Navigation normale : Les visiteurs peuvent parcourir les offres d'emploi sans restriction
📝 Tentative de candidature : Lorsqu'un visiteur non connecté clique sur "Postuler"
🔄 Redirection automatique : Il est automatiquement redirigé vers la page de connexion
↩️ Retour après connexion : Après connexion/inscription, il est redirigé vers la page de candidature

🔐 Pour les utilisateurs connectés
Les utilisateurs déjà authentifiés peuvent postuler normalement sans interruption.
🛠️ Dépannage
⚠️ Problèmes courants
🚫 La redirection ne fonctionne pas :

✅ Vérifiez que les cookies sont activés
✅ Vérifiez que le module portal est installé
📄 Consultez les logs Odoo pour les erreurs

❌ Page de candidature inaccessible :

📦 Vérifiez que website_hr_recruitment est installé et actif
🔐 Vérifiez les permissions sur les modèles hr.job

📁 Structure du module
custom_job_redirect/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py
└── README.md
🔄 Compatibilité
✅ Odoo 18.0

🆘 Support
Pour toute question ou problème :

✅ Vérifiez que toutes les étapes de configuration sont complétées
🔍 Vérifiez la compatibilité avec votre version d'Odoo

📄 Licence
Ce module est distribué sous licence LGPL-3.

📌 Note : Ce module modifie le comportement standard d'Odoo pour les candidatures. Assurez-vous de tester en environnement de développement avant de déployer en production.




