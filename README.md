# 💰 SalaryNow – Pre-Salary Web Application

SalaryNow is a web-based application that allows employees to request salary advances easily, while enabling admins to review and manage those requests efficiently. The system also includes an AI-powered assistant for user support.

---

## 🚀 Project Overview

This project simplifies the salary advance process. Users can register, log in, and submit requests, while admins can approve or reject them through a dedicated dashboard. An AI assistant is integrated to improve user experience.

---

## ✨ Key Features

### 👤 User Features
- User Signup & Login system  
- Submit salary advance requests  
- View request status (Pending / Approved / Rejected)  
- Interactive dashboard  

### 🛠️ Admin Features
- Secure admin login  
- View all user requests  
- Approve or reject requests  
- Admin dashboard  

### 🤖 AI Integration
- AI assistant for user queries  
- Helps users understand the system  

---

## 🧰 Tech Stack

- Backend: Python, Flask  
- Database: SQLite  
- Frontend: HTML, CSS, JavaScript  
- AI: OpenAI API  

---

## 📁 Project Structure

salary-now/
│
├── app.py  
├── salarynow.db  
├── templates/  
│   ├── login.html  
│   ├── signup.html  
│   ├── dashboard.html  
│   ├── admin_login.html  
│   └── admin_dashboard.html  
│
├── static/  
└── README.md  

---

## ⚙️ How It Works

1. User logs in  
2. Submits salary request  
3. Data stored in database  
4. Admin reviews request  
5. Approves or rejects  
6. User sees updated status  

---

## ▶️ How to Run

```bash
pip install flask openai
python app.py
