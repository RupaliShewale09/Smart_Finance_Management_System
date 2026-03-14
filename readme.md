# SmartFinance – AI-Powered Personal Finance Intelligence Platform

An AI-powered personal finance platform that automates expense tracking, predicts spending patterns, and provides intelligent financial guidance.

The system combines a **FastAPI backend**, **Machine Learning for expense categorization**, and **Generative AI (Gemini)** to help users manage their finances more effectively.


---

# 🚀 Key Features

### 1.  Secure Authentication & Digital Wallet

- Secure user signup and login with password hashing  
- Automatic generation of unique wallet IDs for user and vendor
- Personalized QR codes for wallet payments  
- Real-time wallet balance tracking  
- Instant balance updates after transactions  

This module simulates a **digital wallet ecosystem** for merchant transactions and balance management.

---

### 2.  🤖 Intelligent Scan & Pay with ML Categorization

The system automatically categorizes expenses using a **Random Forest Machine Learning model**.

**Expense Categories**

| Category | Description |
|----------|-------------|
| 🔴 Critical | Essential spending such as rent, bills, or medical expenses |
| 🟠 Necessary | Regular lifestyle expenses like groceries or transportation |
| 🟡 Discretionary | Optional spending such as entertainment or food delivery |

### Features Used for Prediction

- Merchant name and category  
- Transaction amount  
- User wallet balance  
- Time of transaction (hour)  
- Day of week  
- Recurring transaction detection (30-day history)

---

### 3. 📊 Spending Insights & Analytics

- Daily spending trends using **interactive graphs**
- Category-wise expense distribution
- Merchant-wise spending analysis

**Visualization:** Plotly with dynamic frontend updates.

---

### 4. ⚠️ Predictive Spending Limits & Alerts

The platform automatically calculates spending limits for different
categories based on historical financial behavior.


### Alert System

Two levels of alerts are triggered to prevent overspending.

| Alert Type | Trigger |
|------------|---------|
| ⚠️ Warning | When 85% of the spending limit is reached |
| 🚨 Danger | When the spending limit is exceeded |

These alerts help users control overspending.

---

### 5. 🧠 AI Financial Coach (Gemini Integration)

An AI-powered financial advisor that analyzes transactions and provides personalized recommendations

### AI Coach Capabilities

-   Analyzes recent transaction history
-   Evaluates active spending alerts
-   Generates personalized financial recommendations


This enables fast, context-aware financial guidance tailored to the
user's financial behavior.

---

### 6. 💰 Savings Estimation & Investment Suggestions

The system estimates how much money a user can safely save based on
their income and predicted expenses.

### Savings Prediction

Safe Savings = Income − Predicted Expenses

### Suggested Investment Options

Based on saving potential, the system recommends:

-   SIP (Systematic Investment Plans)
-   Mutual Funds
-   Stocks
-   Debt Funds
-   Emergency savings allocation

This feature encourages users to move from expense tracking to wealth
building.

---

### 7. 🔔 AI Behavioral Nudges

Short AI-generated nudges encourage better financial habits.

Examples:

- "You've spent ₹900 on coffee this week. Brewing at home could save ₹3000 monthly."
- "You're close to your entertainment budget. Consider a free activity this weekend."


### Background Scheduler

A background task scheduler ensures nudges are delivered at optimal
times without overwhelming the user.


---

# 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, Python, SQLAlchemy |
| Database | SQLite |
| Machine Learning | Scikit-Learn, Random Forest, Pandas, Joblib |
| Generative AI | Google Gemini API |
| Frontend | HTML, CSS, JavaScript |
| Visualization | Plotly |

---


# ⚙️ Installation & Setup

### 1. Clone the Repository

git clone
https://github.com/RupaliShewale09/Smart_Finance_Management_System.git                                                       
cd Smart_Finance_Management_System

### 2. Install Dependencies

pip install -r requirements.txt

### 3. Configure Environment Variables

Create a `.env` file and add:

GEMINI_API_KEY=your_api_key_here

### 4. Run the FastAPI Server

python backend/main.py

or

uvicorn backend.main:app --reload

### 5. Access the Application

http://127.0.0.1:8000


---

# 🎯 Project Objective

To build an intelligent personal finance ecosystem integrating Machine Learning, Generative AI, and financial analytics to help users make smarter financial decisions.

---

Developed by *Rupali Shewale*







