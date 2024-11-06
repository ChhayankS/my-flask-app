from flask import Flask, render_template_string, redirect, url_for, request, flash, session
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys
import logging

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MONGO_URI'] = 'mongodb+srv://chhayankshekhar:OxIO5b6UC0NylaFo@cluster0.sxkx6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'  # Change this to your MongoDB URI if using Atlas
mongo = PyMongo(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Change to DEBUG to log detailed info

# Signup Form
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

@app.route('/')
def landing_page():
    landing_page_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Landing Page</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; background-color: #f8f9fa; }
            header { padding: 20px; background-color: #343a40; color: white; }
            .hero { background: #007bff; color: white; padding: 50px 0; }
            footer { background-color: #343a40; color: white; padding: 10px 0; }
            a { color: #007bff; text-decoration: none; }
        </style>
    </head>
    <body>
        <header>
            <h1>Welcome to Our Website!</h1>
            <a href="{{ url_for('login') }}">Login</a> | <a href="{{ url_for('signup') }}">Sign Up</a>
        </header>
        <section class="hero">
            <h2>Your Ultimate Solution</h2>
            <p>Experience the future of web applications.</p>
        </section>
        <footer>
            <p>&copy; 2024 Your Company</p>
        </footer>
    </body>
    </html>
    """
    return render_template_string(landing_page_html)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        try:
            username = form.username.data
            password = generate_password_hash(form.password.data)
            user_exists = mongo.db.users.find_one({'username': username})
            if user_exists:
                flash('Username already exists', 'danger')
                return redirect(url_for('signup'))
            mongo.db.users.insert_one({'username': username, 'password': password})
            flash('Signup successful!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"Error during signup: {e}")
            flash("An error occurred during signup, please try again.", "danger")
            return redirect(url_for('signup'))
    
    signup_page_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sign Up</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; }
            form { margin-top: 50px; }
            input { padding: 10px; margin: 5px; width: 200px; }
            button { padding: 10px 20px; background-color: #007bff; color: white; border: none; }
        </style>
    </head>
    <body>
        <header>
            <h1>Sign Up</h1>
        </header>
        <form method="POST">
            {{ form.hidden_tag() }}
            <div>
                <label for="username">Username:</label>
                {{ form.username() }}
            </div>
            <div>
                <label for="password">Password:</label>
                {{ form.password() }}
            </div>
            <button type="submit">Sign Up</button>
        </form>
        <footer>
            <p>&copy; 2024 Your Company</p>
        </footer>
    </body>
    </html>
    """
    return render_template_string(signup_page_html, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            username = form.username.data
            password = form.password.data

            # Log the login attempt details for debugging
            logging.debug(f"Attempting to log in with username: {username}")

            user = mongo.db.users.find_one({'username': username})

            if not user:
                logging.error(f"User {username} not found.")
                flash('Invalid credentials', 'danger')
                return redirect(url_for('login'))
            
            if not check_password_hash(user['password'], password):
                logging.error(f"Incorrect password for user {username}.")
                flash('Invalid credentials', 'danger')
                return redirect(url_for('login'))

            # Successful login
            session['user'] = username
            logging.debug(f"User {username} logged in successfully.")
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            logging.error(f"Error during login: {e}")
            flash("An error occurred during login, please try again.", "danger")
            return redirect(url_for('login'))
    
    login_page_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; }
            form { margin-top: 50px; }
            input { padding: 10px; margin: 5px; width: 200px; }
            button { padding: 10px 20px; background-color: #007bff; color: white; border: none; }
        </style>
    </head>
    <body>
        <header>
            <h1>Login</h1>
        </header>
        <form method="POST">
            {{ form.hidden_tag() }}
            <div>
                <label for="username">Username:</label>
                {{ form.username() }}
            </div>
            <div>
                <label for="password">Password:</label>
                {{ form.password() }}
            </div>
            <button type="submit">Log In</button>
        </form>
        <footer>
            <p>&copy; 2024 Your Company</p>
        </footer>
    </body>
    </html>
    """
    return render_template_string(login_page_html, form=form)

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        username = session['user']
        dashboard_page_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard</title>
        </head>
        <body>
            <h1>Welcome, {{ username }}!</h1>
            <p>This is your dashboard.</p>
        </body>
        </html>
        """
        return render_template_string(dashboard_page_html, username=username)
    return redirect(url_for('login'))

# Run Flask in a separate thread
def run_flask():
    app.run(port=5023, debug=False, use_reloader=False)

    run_flask()
