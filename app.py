from flask import Flask, request, redirect, render_template, url_for, session, flash
from models import db, User, Expense
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Créer les tables
with app.app_context():
    db.create_all()

# Ajouter un utilisateur de test si inexistant
with app.app_context():
    email = "john@example.com"
    if not User.query.filter_by(email=email).first():
        new_user = User(
            first_name="John",
            last_name="nassim",
            email=email,
            password=generate_password_hash("Password123", method="pbkdf2:sha256"),
            currency="EUR",
            monthly_budget=1000.0
        )
        db.session.add(new_user)
        db.session.commit()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        currency = request.form['currency']
        monthly_budget = float(request.form.get('monthly_budget', 0.0))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password,
            currency=currency,
            monthly_budget=monthly_budget
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('sign_up.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard', user_id=user.id))
        else:
            flash("Email ou mot de passe incorrect.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    user = User.query.get(user_id)
    if not user:
        return "Utilisateur non trouvé", 404

    expenses = Expense.query.filter_by(user_id=user.id).order_by(Expense.date.desc()).limit(10).all()
    total_spent = sum(e.amount for e in user.expenses)
    remaining = user.monthly_budget - total_spent

    return render_template('acceuil.html', user=user, expenses=expenses, total_spent=total_spent, remaining=remaining)

@app.route('/expense', methods=['POST'])
def expense():
    if 'user_id' not in session:
        flash("Vous devez être connecté pour ajouter une dépense.")
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)
    if not user:
        flash("Utilisateur introuvable.")
        return redirect(url_for('login'))

    try:
        montant = float(request.form.get('amount', 0))
        category = request.form.get('category')
        description = request.form.get('description', '')
        date_str = request.form.get('date')

        # 🔥 Conversion ici du string en objet datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

        new_expense = Expense(
            user_id=user_id,
            amount=montant,
            category=category,
            description=description,
            date=date_obj  # 👈 ici on passe un datetime et plus un string
        )

        db.session.add(new_expense)
        db.session.commit()

        flash("Dépense ajoutée avec succès !")
        return redirect(url_for('dashboard', user_id=user_id))

    except Exception as e:
        print("Erreur lors de l'ajout de la dépense :", e)
        flash("Une erreur s'est produite lors de l'ajout de la dépense.")
        return redirect(url_for('dashboard', user_id=user_id))
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
