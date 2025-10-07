from flask import Flask, request, redirect, render_template
from models import db, User
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_budget.db'
db.init_app(app)

@app.route('/register', methods=['POST'])
def register():
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    email = request.form['email']
    password = request.form['password']
    currency = request.form['currency']
    monthly_budget = request.form.get('monthlyBudget', 0.0)

    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(first_name=first_name, last_name=last_name,
                    email=email, password=hashed_password,
                    currency=currency, monthly_budget=monthly_budget)

    db.session.add(new_user)
    db.session.commit()
    return redirect('/login')
