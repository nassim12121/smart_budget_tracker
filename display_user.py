from app import app, db
from models import User

with app.app_context():
    # إنشاء الجداول إذا ما كانوا موجودين
    db.create_all()

    # جلب كل المستخدمين
    users = User.query.all()

    if not users:
        print("لا يوجد مستخدمين في قاعدة البيانات.")
    else:
        for user in users:
            print(f"ID: {user.id}")
            print(f"Prénom: {user.first_name}")
            print(f"Nom: {user.last_name}")
            print(f"Email: {user.email}")
            print(f"Devise: {user.currency}")
            print(f"Budget mensuel: {user.monthly_budget}")
            print("-" * 40)
