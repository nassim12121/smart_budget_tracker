import pandas as pd
from models import db, Expense, User
from app import app
import os
import plotly.express as px
import plotly.graph_objects as go

USER_ID = 3  # ID of the user to analyze

with app.app_context():
    # Fetch expenses for the selected user
    expenses = db.session.query(
        Expense.date,
        Expense.category,
        Expense.amount,
        User.first_name,
        User.last_name,
        User.email,
        User.monthly_budget
    ).join(User).filter(User.id == USER_ID).all()

    # Convert query results to list of dicts
    data = [{
        "date": e.date,
        "category": e.category,
        "amount": e.amount,
        "first_name": e.first_name,
        "last_name": e.last_name,
        "email": e.email,
        "monthly_budget": e.monthly_budget
    } for e in expenses]

    # Create DataFrame
    df = pd.DataFrame(data)

# === Data Cleaning ===
required_cols = {'date', 'category', 'amount'}
if not required_cols.issubset(df.columns):
    raise ValueError("❌ Missing one of the required columns: date, category, amount")

df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
df = df.dropna(subset=['date', 'category', 'amount']).drop_duplicates()
df = df[df['amount'] >= 0]

monthly_budget = df['monthly_budget'].iloc[0]

# === Data Analysis ===
category_totals = df.groupby('category')['amount'].sum()
daily_sum = df.groupby('date')['amount'].sum()
daily_avg = daily_sum.mean()
max_day = daily_sum.idxmax()
max_amount = daily_sum.max()
cumulative = daily_sum.sort_index().cumsum()
remaining_budget = monthly_budget - cumulative.iloc[-1]

# === Create folders ===
user_folder = f"data/user_{USER_ID}"
os.makedirs(user_folder, exist_ok=True)
graphs_folder = os.path.join(user_folder, "graphs")
os.makedirs(graphs_folder, exist_ok=True)

# === Save CSV ===
csv_path = os.path.join(user_folder, "expenses.csv")
df.to_csv(csv_path, index=False)

# === Generate summary ===
summary = f"""
Expense summary for user {df['first_name'].iloc[0]} {df['last_name'].iloc[0]}:

- Total expenses by category:
{category_totals.to_string()}

- Daily average: {daily_avg:.2f}
- Highest spending day: {max_day.date()} with amount {max_amount:.2f}
- Monthly budget: {monthly_budget:.2f}
- Current cumulative spending: {cumulative.iloc[-1]:.2f}
- Remaining budget: {remaining_budget:.2f}
"""
summary_path = os.path.join(user_folder, "summary.txt")
with open(summary_path, "w", encoding="utf-8") as f:
    f.write(summary)

print("✅ Data and summary saved successfully!")
print(summary)

# === Plotly Graphs ===

# Bar chart: Expenses by Category
fig_bar = px.bar(category_totals, x=category_totals.index, y=category_totals.values,
                 labels={'x':'Category', 'y':'Amount'}, title="Expenses by Category")
fig_bar.write_html(os.path.join(graphs_folder, f"user_{USER_ID}_category.html"), include_plotlyjs='cdn')

# Line chart: Daily Expenses
fig_line = px.line(x=daily_sum.index, y=daily_sum.values, markers=True,
                   labels={'x':'Date', 'y':'Amount'}, title="Daily Expenses")
fig_line.write_html(os.path.join(graphs_folder, f"user_{USER_ID}_daily.html"), include_plotlyjs='cdn')

# Pie chart: Expense Distribution
fig_pie = px.pie(names=category_totals.index, values=category_totals.values,
                 title="Expense Distribution by Category")
fig_pie.write_html(os.path.join(graphs_folder, f"user_{USER_ID}_pie.html"), include_plotlyjs='cdn')

# Cumulative Spending vs Budget
fig_budget = go.Figure()
fig_budget.add_trace(go.Scatter(x=cumulative.index, y=cumulative.values, mode='lines+markers',
                                name='Cumulative Spending'))
fig_budget.add_trace(go.Scatter(x=cumulative.index, y=[monthly_budget]*len(cumulative),
                                mode='lines', name='Monthly Budget', line=dict(dash='dash', color='red')))
fig_budget.update_layout(title="Cumulative Expenses vs Monthly Budget",
                         xaxis_title="Date", yaxis_title="Amount")
fig_budget.write_html(os.path.join(graphs_folder, f"user_{USER_ID}_cumulative_vs_budget.html"), include_plotlyjs='cdn')

print("✅ Plotly interactive graphs generated and saved successfully!")
