# 💎 Jewelry E-Commerce Website (Django)

An elegant and customizable online jewelry store built with Django. Users can browse products, add to cart, and securely pay using Razorpay.

---

## 🔥 Features

- User registration & login
- Add to Cart & Checkout
- Razorpay Payment Integration
- Admin panel for managing products
- Email confirmation system

---

## 🛠️ Tech Stack

- Backend: Django
- Frontend: HTML, CSS, Bootstrap
- Database: SQLite (dev), PostgreSQL (prod)
- Payment Gateway: Razorpay

---

## 🚀 Getting Started

1. **Clone the repo**  
   ```bash
   git clone https://github.com/yourusername/yourrepo.git
   cd yourrepo

2. **Create a virtual environment**


    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows

3. **Install dependencies**


    pip install -r requirements.txt

4. **Set environment variables**

Create a .env file in the root:

    EMAIL_HOST_USER=youremail@example.com
    EMAIL_HOST_PASSWORD=yourpassword
    RAZORPAY_KEY_ID=yourkeyid
    RAZORPAY_KEY_SECRET=yourkeysecret

5. **Run migrations**

    python manage.py migrate

6. **Load sample data (if provided)**

    python manage.py loaddata clean_data.json

7. **Run the project**

    python manage.py runserver