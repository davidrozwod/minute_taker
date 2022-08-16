#Declaring python packages
from flask import Flask, render_template,flash, redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import re


#Initializing flask app 
app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meeting.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "random string"

#Initializing database
db = SQLAlchemy(app)

#Initializing login manager
login = LoginManager(app)
db.init_app(app)
login.init_app(app)
login.login_view = 'login'
 

#Creating user database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(), nullable=False)

    def set_password(self,password): 
     self.password_hash = generate_password_hash(password)
     
    def check_password(self,password):
     return check_password_hash(self.password_hash,password)

#User loader method
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

#Creating meeting database
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

#Initialize object attributes
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

#Create database file
db.create_all()

#Route to index page
@app.route("/")
def home():
    return render_template("index.html")

#Route to index page
@app.route("/index")
def index():
    return render_template("index.html")

#Route to meeting page
@app.route("/meeting", methods=['GET', 'POST'])
@login_required
def meeting():
    if request.method == 'POST':
        #Checks user input
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
        #Populates the database
        db.session.add(mtndata)
        db.session.commit()
        #Retriving table from database for current user
        items = Meeting.query.with_entities(Meeting.id, Meeting.title, Meeting.taker, Meeting.topic, Meeting.atendees, Meeting.raisedby, Meeting.actionsrequired, Meeting.tobeactioned,
        Meeting.notes, Meeting.dates, Meeting.starttime, Meeting.endtime).filter_by(user_id = user_id)
        return render_template('meetings.html', items=items)
    else:
      #Retriving table from database for current user
      user_id = current_user.id
      items = Meeting.query.with_entities(Meeting.id, Meeting.title, Meeting.taker, Meeting.topic, Meeting.atendees, Meeting.raisedby, Meeting.actionsrequired, Meeting.tobeactioned,
      Meeting.notes, Meeting.dates, Meeting.starttime, Meeting.endtime).filter_by(user_id = user_id)
    return render_template('meetings.html', items=items) 

#Route to login page
@app.route('/login', methods = ['POST', 'GET'])
def login():
    #Checks if user is logged in
    if current_user.is_authenticated:
        return redirect('/meeting')
    #Checks user input
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email = email).first()
        #Checks if email exists on database and that password is correct
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/meeting')
        #Checks if email exists on the database
        if user is None:
            flash('Email not registered')
            render_template('login.html')
        #Checks that password is correct
        if user is not None and user is not user.check_password(request.form['password']):
            flash('Wrong password')
            render_template('login.html')
    return render_template('login.html')

#Route to signup page
@app.route('/signup', methods=['POST', 'GET'])
def register():
    #RFC 5322 compliant regex for valid emails
    regex = "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\\])"

    #Checks if user is logged in
    if current_user.is_authenticated:
        return redirect('/meeting')
        
    #Checks user input
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        #Check that email is unique
        if User.query.filter_by(email=email).first():
           flash('Email already registered')
           return render_template('signup.html')
        #Checks password length
        if len(password) <8:
         flash('Password is too short It must be between 8 and 12 characters')
         return render_template('signup.html')
        if len(password) >12:
         flash('Password is too long It must be between 8 and 12 characters')
         return render_template('signup.html')
        #Checks that email is valid
        if re.match(regex, email): 
           user = User(email=email)
           user.set_password(password)
           #Populates the database
           db.session.add(user)
           db.session.commit()
           flash('Thank you for signing up!')
           return redirect('/login')
        else:
           flash('Email not valid')
           return render_template('signup.html')
    return render_template('signup.html')

#Route to logout
@app.route('/logout')
def logout():
      #Checks if user is logged in
      if current_user.is_authenticated:
        logout_user()
        flash('User logged out')
        return redirect('/index')
      else:
        flash('Not logged in')
        return redirect('/login')

#Route to delete meeting row
@app.route('/delete/<meeting_id>')
def delete(meeting_id):
    if current_user.is_authenticated:
     row = Meeting.query.filter_by(id=meeting_id).first_or_404()
     #Delete row from database
     db.session.delete(row)
     db.session.commit()
     flash('Meeting deleted')
    return redirect('/meeting')

#Run flask app
if __name__ == "__main__":
 app.run(debug = True)