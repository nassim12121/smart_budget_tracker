from app import app, db
from models import User, Expense

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
            
            # جلب كل المصاريف الخاصة بالمستخدم
            expenses = Expense.query.filter_by(user_id=user.id).all()
            if not expenses:
                print("لا توجد مصاريف لهذا المستخدم.")
            else:
                print("Mesarif:")
                for exp in expenses:
                    print(f"  ID: {exp.id}")
                    print(f"  Montant: {exp.amount}")
                    print(f"  Catégorie: {exp.category}")
                    print(f"  Description: {exp.description}")
                    print(f"  Date: {exp.date}")
                    print("  -" * 10)
            
            print("-" * 40)
