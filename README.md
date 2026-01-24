<div align="center">
  <img src="app/static/img/screenshots/homepage.png" alt="Homepage" width="800">
</div>
<div align="center">

# Project Synapse
### Student Data Management & Registration System

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%23563D7C.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![Deployment](https://img.shields.io/badge/Deployed%20on-PythonAnywhere-2ca5e0?style=for-the-badge&logo=pythonanywhere&logoColor=white)

**ACES Synapse** is a centralized web platform designed to streamline student registration, data encoding, and membership management for the **Association of Computer Engineering Students (ACES)** and other academic organizations at **PUP Biñan Campus**.

[View Live Demo](https://aces2026synapse.pythonanywhere.com) · [Report Bug](https://github.com/JOBIJEEEB/pupbc_synapse/issues) · [Request Feature](https://github.com/JOBIJEEEB/pupbc_synapse/issues)

</div>

---
## 🛠️ Technical Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) | Core web framework handling routes and logic. |
| **Database** | ![SQLite](https://img.shields.io/badge/SQLite-07405e?style=flat-square&logo=sqlite&logoColor=white) | Lightweight, serverless relational database. |
| **ORM** | ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white) | Object-Relational Mapper for safe database queries. |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white) | Custom Bento Grid CSS and jQuery Inputmask. |
| **Hosting** | ![PythonAnywhere](https://img.shields.io/badge/PythonAnywhere-2ca5e0?style=flat-square&logo=pythonanywhere&logoColor=white) | Cloud platform for WSGI deployment. |

---

## 📸 Project Screenshots

| **Student Registration** | **Admin Dashboard** |
|:---:|:---:|
| <img src="app/static/img/screenshots/registration.png" alt="Registration Form" width="400"> | <img src="app/static/img/screenshots/dashboard.png" alt="Bento Dashboard" width="400"> |
| *Multi-step wizard with live ID preview* | *Bento-grid layout for managing records* |

---

## ✨ Key Features

* **Dynamic Registration Wizard** 📝  
    Replaces manual encoding with a multi-step digital form that validates student data in real-time.
    
* **Live ID Preview** 🪪  
    Automatically generates a visual preview of the student's ID card as they type, ensuring accuracy before submission.

* **Bento-Grid Dashboard** 🍱  
    A modern, responsive admin interface inspired by bento box layouts for efficient record management.

* **Smart Data Export** 📊  
    One-click CSV generation formatted specifically for class and section lists, ready for printing or Excel.

* **Organization Isolation** 🏫  
    Supports multiple organizations (ACES, HRSS, JPIA) with dynamic branding, headers, and color themes.

---

## 📂 Project Structure

```text
pupbc_synapse/
├── app/
│   ├── routes/          # Blueprints (Auth, Admin, Main)
│   ├── static/          # Assets (CSS, JS, Org Logos)
│   ├── templates/       # Jinja2 HTML Templates
│   └── models.py        # Database Schema
├── instance/            # SQLite Database
├── config.py            # App Configuration
├── seed.py              # Data Seeder
└── run.py               # Entry Point
