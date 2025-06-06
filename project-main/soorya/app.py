from flask import Flask, render_template, request,redirect,url_for,flash
from datetime import datetime
from flask_mail import Mail, Message
import re
import mysql.connector

app = Flask(__name__)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Soorya@0213",  # Replace with your password
    database="faculty"
)
cursor = db.cursor()

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sooryas851@gmail.com'  # Replace with your Gmail
app.config['MAIL_PASSWORD'] = 'jznu akjd vlrf iwkr'     # Replace with app password

mail = Mail(app)

@app.route('/')
def form():
    return render_template('login.html')
@app.route('/log')
def log():
    return render_template('login.html')
@app.route('/home')
def home():      
    return render_template('home.html')

@app.route('/login1', methods=['POST'])
def login1():
   error = None
   success = None
   username = None
   user_type = None

   if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        # Validate username: at least one alphabetic letter
        if not re.search('[a-zA-Z]', username):
            error = 'Username must contain at least one alphabetic letter'
            return render_template('login.html', error=error, username=username, user_type=user_type)

        # Validate password: at least 6 characters
        if len(password) < 6:
            error = 'Password must be at least 6 characters long'
            return render_template('login.html', error=error, username=username, user_type=user_type)

        # Check for duplicate username
        select_query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(select_query, (username,))
        if cursor.fetchone():
            error = 'This username is already taken'
            return render_template('login.html', error=error, username=username, user_type=user_type)

        # If all validations pass, insert new user
        insert_query = "INSERT INTO users (username, password, user_type) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (username, password, user_type))
        db.commit()
        success = 'Account created successfully! Please log in.'
        return render_template('login.html', success=success)

   return render_template('login.html', error=error, username=username, user_type=user_type)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user_type = request.form['user_type']

    # Query to check if user exists
    select_query = "SELECT * FROM users WHERE username = %s AND password = %s AND user_type = %s"
    cursor.execute(select_query, (username, password, user_type))
    user = cursor.fetchone()

    if user:
        # User exists, redirect to home page
        return redirect(url_for('home'))
    else:
        # User doesn't exist, redirect to signup page
        return redirect(url_for('signup'))
    
@app.route('/submitpublication')
def submitpublication():
    return render_template('submit.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        data = (
            request.form['faculty_name'],
            request.form['department'],
            request.form['title'],
            request.form['pub_type'],
            request.form['publisher'],
            request.form['publisher_email'],
            request.form['publication_year'],
            request.form['doi_or_link']
        )
        cursor.execute("""
            INSERT INTO publications 
            (faculty_name, department, title, pub_type, publisher, publisher_email, publication_year, doi_or_link)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, data)
        db.commit()
        return redirect('/view_publications')  # or '/view' if that's your actual route
    return render_template('submit.html')

@app.route('/view_publications')
def view_publications():
    cursor.execute("SELECT * FROM publications")  # Adjust table name as needed
    records = cursor.fetchall()
    return render_template('view.html', records=records)


@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d %b %Y, %I:%M %p'):
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    return value.strftime(format)
@app.route('/admin')
def admin():
    cursor.execute("SELECT * FROM publications")
    records = cursor.fetchall()
    return render_template('admin.html', records=records)

@app.route('/send_remark', methods=['POST'])
def send_remark():
    sender_gmail = request.form['sender_gmail']  # manually entered in the frontend
    publisher_email = request.form['publisher_email']
    remark = request.form['remark']
    title = request.form['title']

    msg = Message(
        subject=f"Remark on Publication: {title}",
        sender=app.config['MAIL_USERNAME'],  # actual sender is your app-configured email
        recipients=[publisher_email]
    )
    msg.body = f"From: {sender_gmail}\n\nHere is a remark regarding the publication titled '{title}':\n\n{remark}\n\nRegards,\n{sender_gmail}"

    try:
        mail.send(msg)
        return "<script>alert('Remark sent successfully!'); window.location='/admin';</script>"
    except Exception as e:
        return f"<h3>Error sending email: {str(e)}</h3>"



@app.route('/home.html')
def home_page():
    return render_template('home.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/view')
def view():
    return ("hai")

if __name__ == '__main__':
    app.run(debug=True)