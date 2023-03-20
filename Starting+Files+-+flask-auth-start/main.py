from flask import Flask, render_template, redirect, url_for, send_from_directory, request, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
login_manager = LoginManager()

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/files/'
app.config['CHEAT_SHEET_FILE_NAME'] = 'cheat_sheet.pdf'

db = SQLAlchemy(app)
Bootstrap(app)

##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegisterForm(FlaskForm):
    name = StringField(label='name', validators=[DataRequired()])
    email = EmailField(label='email', validators=[DataRequired(), Email()])
    password = PasswordField (label='password', validators=[DataRequired()])
    button = SubmitField("Sign me up")

@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        user = User(email=form.email.data, name=form.name.data, password=hash_and_salted_password)

        db.session.add(user)
        db.session.commit()
        return redirect(url_for("secrets"))
    else:
        return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Find user by email entered.
        user = User.query.filter_by(email=email).first()
        if user:
            # Check stored password hash against entered password hashed.
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('secrets'))
            else:
                flash('invalid password', 'error')
        else:
            flash('email not registered', 'error')

    return render_template("login.html", logged_in=current_user.is_authenticated)

@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", logged_in=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               app.config['CHEAT_SHEET_FILE_NAME'], as_attachment=True)


if __name__ == "__main__":
    login_manager.init_app(app)
    app.run(debug=True)
