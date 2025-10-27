from app import app, db
from models import User, Expense
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

users_data = [
    {"first_name": "Rayane", "last_name": "Mtar", "email": "rayane@example.com", "password": "1234", "monthly_budget": 1200, "currency": "TND"},
    {"first_name": "Sarra", "last_name": "Ben Ali", "email": "sarra@example.com", "password": "1234", "monthly_budget": 1000, "currency": "TND"},
    {"first_name": "Omar", "last_name": "Trabelsi", "email": "omar@example.com", "password": "1234", "monthly_budget": 1500, "currency": "TND"},
    {"first_name": "Mariem", "last_name": "Jaziri", "email": "mariem@example.com", "password": "1234", "monthly_budget": 900, "currency": "TND"},
    {"first_name": "Ahmed", "last_name": "Zitoun", "email": "ahmed@example.com", "password": "1234", "monthly_budget": 1100, "currency": "TND"},
]


categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment"]

with app.app_context():
    users = []
    for u in users_data:
        if not User.query.filter_by(email=u["email"]).first():
            user = User(
            first_name=u["first_name"],
            last_name=u["last_name"],
            email=u["email"],
            password=generate_password_hash(u["password"], method="pbkdf2:sha256"),
            monthly_budget=u["monthly_budget"],
            currency=u["currency"]
            )

            db.session.add(user)
            users.append(user)
    db.session.commit()


    for user in users:
        for _ in range(10):
            expense = Expense(
                amount=round(random.uniform(5, 200), 2),
                category=random.choice(categories),
                description=f"Auto-generated {random.choice(categories)} expense",
                date=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                user_id=user.id
            )
            db.session.add(expense)
    db.session.commit()

    print("✅ Seed terminé avec succès !")
