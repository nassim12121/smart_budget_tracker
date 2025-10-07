import pandas as pd
from models import db, Expense, User
from app import app
import os

USER_ID = 2  # المستخدم اللي تحب تاخذ بياناته

with app.app_context():
    # جلب المصاريف للمستخدم id=2
    expenses = db.session.query(
        Expense.date,
        Expense.category,
        Expense.amount,
        User.first_name,
        User.last_name,
        User.email
    ).join(User).filter(User.id == USER_ID).all()

    # تحويل النتائج لقائمة قواميس
    data = [{
        "date": e.date,
        "category": e.category,
        "amount": e.amount,
        "first_name": e.first_name,
        "last_name": e.last_name,
        "email": e.email
    } for e in expenses]

    # تحويل لقالب DataFrame
    df = pd.DataFrame(data)

    # التأكد من وجود مجلد data
    if not os.path.exists("data"):
        os.makedirs("data")

    # حفظ كملف CSV
    csv_path = f"data/user_{USER_ID}_expenses.csv"
    df.to_csv(csv_path, index=False)

    #print(df.head(30))

# تحويل العمود 'date' لتاريخ
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# تحويل العمود 'amount' لأرقام
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

# إزالة أي صفوف فيها قيم ناقصة أو خاطئة
df = df.dropna(subset=['date', 'category', 'amount'])


#print(df.info())
category_totals = df.groupby('category')['amount'].sum()
print(category_totals)
daily_avg = df.groupby('date')['amount'].sum().mean()
print("daily_avg:", daily_avg)
daily_sum = df.groupby('date')['amount'].sum()
max_day = daily_sum.idxmax()
max_amount = daily_sum.max()
print(f"most day:  {max_day} amount:  {max_amount}")

summary = f"""
Expense summary for user {df['first_name'].iloc[0]} {df['last_name'].iloc[0]}:

- Total expenses by category:
{category_totals.to_string()}

- Daily average: {daily_avg:.2f}
- Highest spending day: {max_day.date()} with amount {max_amount:.2f}
"""
print(summary)

import matplotlib.pyplot as plt

# Bar chart: expenses by category
plt.figure(figsize=(6,4))
category_totals.plot(kind='bar', color='skyblue')
plt.title('Expenses by Category')
plt.ylabel('Amount')
plt.xlabel('Category')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
#plt.savefig(f'graphs/user_{USER_ID}_category.png')
plt.close()

# Line chart: daily expenses
daily_sum.plot(kind='line', marker='o', color='green')
plt.title('Daily Expenses')
plt.ylabel('Amount')
plt.xlabel('Date')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
#plt.savefig(f'graphs/user_{USER_ID}_daily.png')
plt.close()
