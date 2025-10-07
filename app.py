from flask import Flask, request, redirect, render_template, url_for
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from models import Expense
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
with app.app_context():
    email = "john@example.com"
    if not User.query.filter_by(email=email).first():
        new_user = User(
            first_name="John",
            last_name="Doe",
            email=email,
            password=generate_password_hash("Password123", method="pbkdf2:sha256"),
            currency="EUR",
            monthly_budget=1000.0
        )
        db.session.add(new_user)
        db.session.commit()
    else:
        print("المستخدم بهذا الإيميل موجود بالفعل.")
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        currency = request.form['currency']
        monthly_budget = request.form.get('monthlyBudget', 0.0)

        hashed_password = generate_password_hash(password, method='sha256')
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
            return redirect(url_for('dashboard', user_id=user.id))
        else:
            return "Email ou mot de passe incorrect", 401
    return render_template('login.html')

@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    user = User.query.get(user_id)
    if not user:
        return "Utilisateur non trouvé", 404
    return render_template('acceuil.html', user=user)

if __name__ == "__main__":
    app.run(debug=True)
