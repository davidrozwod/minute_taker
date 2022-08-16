from tkinter import CURRENT
from flask import Flask, render_template,flash, redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from wtforms_alchemy import ModelForm
from wtforms.validators import Email



app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meeting.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "random string"
db = SQLAlchemy(app)
login = LoginManager(app)
db.init_app(app)
login.init_app(app)
login.login_view = 'login'
 


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(), nullable=False)

    def set_password(self,password): 
     self.password_hash = generate_password_hash(password)
     
    def check_password(self,password):
     return check_password_hash(self.password_hash,password)

class UserForm(ModelForm):
    class Meta:
        model = User
        validators = {'email': [Email()]}

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(30), nullable=False)
    taker = db.Column(db.String(30), nullable=False)
    topic = db.Column(db.String(30), nullable=False)
    atendees = db.Column(db.String(200), nullable=False)
    raisedby = db.Column(db.String(30), nullable=False)
    actionsrequired = db.Column(db.String(200), nullable=False)
    tobeactioned = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.String(500), nullable=False)
    dates = db.Column(db.String(8), nullable=False)
    starttime = db.Column(db.String(6), nullable=False)
    endtime = db.Column(db.String(6), nullable=False)   
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

def __init__(self, title, taker, topic, atendees,raisedby, actionsrequired, tobeactioned, notes, date, starttime, endtime, user_id):
   self.title = title
   self.taker = taker
   self.topic = topic
   self.atendees = atendees
   self.raisedby = raisedby
   self.actionsrequired = actionsrequired
   self.tobeactioned = tobeactioned
   self.notes = notes
   self.date = date
   self.starttime = starttime
   self.endtime = endtime;
   self.user_id = user_id;

db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/meeting", methods=['GET', 'POST'])
@login_required
def meeting():
    if request.method == 'POST':
        mtndata = Meeting(title = request.form['title'],
           taker = request.form['taker'],
           topic = request.form['topic'],
           atendees = request.form['atendees'],
           raisedby = request.form['raisedby'],
           actionsrequired = request.form['actionsrequired'],
           tobeactioned = request.form['tobeactioned'],
           notes = request.form['notes'],
           dates = request.form['dates'],
           starttime = request.form['starttime'],
           endtime = request.form['endtime'],
           user_id = current_user.id)
        user_id = current_user.id
        db.session.add(mtndata)
        db.session.commit()
        items = Meeting.query.with_entities(Meeting.id, Meeting.title, Meeting.taker, Meeting.topic, Meeting.atendees, Meeting.raisedby, Meeting.actionsrequired, Meeting.tobeactioned,
        Meeting.notes, Meeting.dates, Meeting.starttime, Meeting.endtime).filter_by(user_id = user_id)
        return render_template('meetings.html', items=items)
    else:
      user_id = current_user.id
      items = Meeting.query.with_entities(Meeting.id, Meeting.title, Meeting.taker, Meeting.topic, Meeting.atendees, Meeting.raisedby, Meeting.actionsrequired, Meeting.tobeactioned,
      Meeting.notes, Meeting.dates, Meeting.starttime, Meeting.endtime).filter_by(user_id = user_id)
    return render_template('meetings.html', items=items) 


@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/meeting')
     
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email = email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/meeting')
    flash('You were successfully logged in')
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def register():
    
    if current_user.is_authenticated:
        return redirect('/meeting')
        
     
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
           flash('Email already registered')
           return render_template('signup.html')
        else: 
         user = User(email=email)
         user.set_password(password)
         db.session.add(user)
         db.session.commit()
         return redirect('/login')
    return render_template('signup.html')

@app.route('/logout')
def logout():
      if current_user.is_authenticated:
        logout_user()
      return redirect('/index')

@app.route('/delete/<meeting_id>')
def delete(meeting_id):
    if current_user.is_authenticated:
     row = Meeting.query.filter_by(id=meeting_id).first_or_404()
     db.session.delete(row)
     db.session.commit()
    return redirect('/meeting')

app.run(debug = True)