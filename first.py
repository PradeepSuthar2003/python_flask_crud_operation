import smtplib
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import json
from datetime import datetime

# with open('config.json', 'r') as c:
#     params = json.load(c)["params"]


app = Flask(__name__)
app.secret_key = "key"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your-email'
app.config['MAIL_PASSWORD'] = 'your-pass-key'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flask_app' #add database here
db = SQLAlchemy(app)

#admin username and password

admin_email = "admin@gmail.com" 
admin_pass = "123"


class bolg_post(db.Model):
    p_id = db.Column(db.Integer, primary_key=True)
    p_tittle = db.Column(db.String(30), nullable=False)
    p_desc = db.Column(db.String(200), nullable=False)
    p_date = db.Column(db.String(12), nullable=False)


class feedback(db.Model):
    f_id = db.Column(db.Integer, primary_key=True)
    f_email = db.Column(db.String(30), nullable=True)
    f_tittle = db.Column(db.String(30), nullable=False)
    f_desc = db.Column(db.String(200), nullable=False)
    f_date = db.Column(db.String(12), nullable=False)


@app.route("/")
def home():
    posts = bolg_post.query.filter_by().all()
    return render_template("index.html", post=posts)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        email = request.form.get("txt_email")
        tittle = request.form.get("txt_tittle")
        desc = request.form.get("txt_desc")
        name = "POGPKS"
        feed = feedback(f_email=email, f_tittle=tittle,
                        f_desc=desc, f_date=datetime.now())
        db.session.add(feed)
        db.session.commit()

        msg = Message(
            tittle,
            sender='sender-email',
            recipients=[email]
        )
        msg.body = desc
        mail.send(msg)
        return render_template('index.html')
    else:
        return render_template('contact.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'email' in session and session['email'] == admin_email:
        post = bolg_post.query.all()
        return render_template('admin.html', email=session['email'], posts=post)

    if request.method == 'POST':
        f_email = request.form.get("txt_email")
        f_pass = request.form.get("txt_pass")

        if (f_email == admin_email and f_pass == admin_pass):
            post = bolg_post.query.all()
            session['email'] = f_email
            return render_template('admin.html', email=session['email'], posts=post)

    return render_template("login.html")


@app.route("/admin")
def admin():
    if 'email' not in session:
        return redirect('/login')
    return 'session not set'


@app.route("/logout")
def logout():
    if 'email' not in session:
        return redirect('/login')

    session.pop('email')
    return redirect('/login')


@app.route("/delete/<string:id>", methods=['GET', 'POST'])
def delete(id):
    post = bolg_post.query.all()
    if 'email' in session and session['email'] == admin_email:
        # posts = bolg_post.query.get(id)
        posts = bolg_post.query.filter_by(p_id=id).one()
        db.session.delete(posts)
        db.session.commit()

    return redirect('/login')


@app.route("/update/<string:id>", methods=['GET', 'POST'])
def update(id):
    if id != '0':
        post = bolg_post.query.filter_by(p_id=id).one()
    else:
        post = 0
    if 'email' in session and session['email'] == admin_email:
        if request.method == 'POST':
            tittle = request.form.get("txt_tittle")
            desc = request.form.get("txt_desc")

            if id == '0':
                post = bolg_post(p_tittle=tittle, p_desc=desc,
                                 p_date=datetime.now())
                db.session.add(post)
                db.session.commit()
                return redirect('/login')
            else:
                post.p_tittle = tittle
                post.p_desc = desc
                post.p_date = datetime.now()

                post = bolg_post(p_tittle=post.p_tittle,
                                 p_desc=post.p_desc, p_date=post.p_date)
                db.session.commit()
                return redirect('/login')
        else:
            return render_template("update.html", post=post)
    else:
        return redirect('/login')


app.run(debug=True, port=8000)
