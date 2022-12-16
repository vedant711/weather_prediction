from flask import Flask,render_template,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import pickle
import numpy as np
import pandas as pd
import datetime
import requests
import random
import csv
from playsound import playsound
from threading import Thread

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))


app.config['SECRET_KEY'] = 'MLXH243GssUWwKdTWS7FDhdwYF56wPj8'
db_name='users.db'
app.config['SQLALCHEMY_DATABASE_URI']="mysql://root:12345678@localhost/users"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False)
    password=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100),nullable=False)
    mobile_number=db.Column(db.String(10),nullable=False)
    

class Weather(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False)
    date=db.Column(db.String(20),nullable=False)
    precipitation=db.Column(db.String(20),nullable=False)
    max_temp=db.Column(db.String(20),nullable=False)
    min_temp=db.Column(db.String(20),nullable=False)
    wind_speed=db.Column(db.String(20),nullable=False)
    forecast=db.Column(db.String(20),nullable=False)
    # sunday=db.Column(db.String(20),nullable=False)
    

app.app_context().push()


@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=['GET',"POST"])
def home():
    if request.method=='POST':
        name=request.form.get('name')
        password=request.form.get('password')
        pwd=password.encode('utf-8')
        # pwd_hash = 
        # print(name,password)
        user=User.query.filter(User.name==name).first()
        # pwd_hash = user.password
        if name=='admin' and password=='711':
            return redirect('/admin')
        # elif user and user.password == password:
        elif user and bcrypt.checkpw(pwd,user.password.encode('utf-8')):
            # flash('Log In successful')
            return redirect('/'+str(user.id))

        else: 
            flash('Incorrect Credentials')
        # print(user)
    return render_template('index.html')

@app.route('/create',  methods=['GET',"POST"])
def create():
    if request.method=='POST':
        name=request.form.get('name')
        password=request.form.get('password')
        email=request.form.get('email')
        mob=request.form.get('mob')
        user=User.query.filter(User.name==name).all()
        if not user and name!='admin' and name!='' and password!='' and len(mob)==10:
            pwd=password.encode('utf-8')
            mySalt = bcrypt.gensalt()
            pwhash = bcrypt.hashpw(pwd,mySalt)
            user = User(name=name,password=pwhash,email=email,mobile_number=mob)
            # print(user)
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        else:
            flash('Incorrect Input')
    return render_template('create.html')


@app.route('/<id>',methods=['GET','POST'])
def indi_usr(id):
    usr=User.query.filter(User.id==id).all()
    if request.method=='POST':
        # api_key = 'ddf2df38a550175470ef6bf036a717f7'
        final_features = [float(x) for x in request.form.values()]
        # final_features = [list(int_features)]
        # print(final_features)
        weat1={}
        today = datetime.date.today()
        dates = [today + datetime.timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]
        final_list=[]
        global weather
        weather = {}
        for date in dates:
            date = pd.to_datetime(date)
            date = date.strftime('%d.%m.%Y')
            d1 = [date]
            d=pd.DataFrame(d1)
            year = pd.DatetimeIndex(d[0]).year
            month = pd.DatetimeIndex(d[0]).month
            day = pd.DatetimeIndex(d[0]).day
            dayofyear = pd.DatetimeIndex(d[0]).dayofyear
            weekofyear = pd.DatetimeIndex(d[0]).weekofyear
            weekday = pd.DatetimeIndex(d[0]).weekday
            quarter = pd.DatetimeIndex(d[0]).quarter
            is_month_start = pd.DatetimeIndex(d[0]).is_month_start
            is_month_end = pd.DatetimeIndex(d[0]).is_month_end
            d2 = [year[0], month[0],day[0],dayofyear[0],weekofyear[0],weekday[0],quarter[0],is_month_start[0],is_month_end[0]]
            new_list = final_features + d2
            # final_list.append(new_list)
            weather_pred = model.predict([np.array(new_list)])
            weather_pred = list(weather_pred)
            weather[date] = [final_features[0],final_features[1],final_features[2],final_features[3],weather_pred[0]]
            # weat1[date] = weather_pred
            weat = Weather(name=usr[0].name,date=date,precipitation=final_features[0],max_temp=final_features[1],min_temp=final_features[2],wind_speed=final_features[3],forecast=weather_pred[0])
            db.session.add(weat)

            for ele in final_features:
                i=round(random.uniform(-10,10),2)
                ind = final_features.index(ele)
                if ind!=len(final_features)-1:
                    ele+=i
                else:
                    ele+=i
                    if ele < 0:
                        ele=0
                final_features[ind] = round(ele,2)
        db.session.commit()
        
        # weather={}
        # for tup in final_list:
        #     weather_pred = model.predict([np.array(tup)])
        #     weather.append(weather_pred)
        return render_template('indi_usr.html',user=usr,weather=weather)
    return render_template('indi_usr.html',user=usr)
    

# @app.route('/predict')

@app.route('/admin')
def admin():
    users = User.query.all()
    return render_template('admin.html',users=users)

@app.route('/delete/<id>')
def delete_usr(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/admin')

@app.route('/edit/<id>', methods=['GET','POST'])
def edit_usr(id):
    user = User.query.get(id)
    # print(request.form)
    name = request.form.get('name')
    user1 = User.query.filter(User.name==name).all()
    if not user1 and name!='admin':
        user.name = name
        db.session.commit()
    else:
        flash('Username already taken')
    return redirect('/admin')

@app.route('/editown/<id>', methods=['GET','POST'])
def edit_usr1(id):
    user = User.query.get(id)
    # print(request.form)
    name = request.form.get('name')
    user1 = User.query.filter(User.name==name).all()
    if not user1 and name!='admin':
        user.name = name
        db.session.commit()
    else:
        flash('Username already taken')
    return redirect('/'+id)

@app.route('/editpwd/<id>', methods=['GET','POST'])
def edit_pwd(id):
    user = User.query.get(id)
    password = request.form.get('password')
    pwd=password.encode('utf-8')
    mySalt = bcrypt.gensalt()
    pwhash = bcrypt.hashpw(pwd,mySalt)
    user.password = pwhash
    db.session.commit()
    return redirect('/'+id)

# @app.route('/export')
# def export_csv():
#     global weather
#     csv1={}
#     csv_row = []
#     field_names=['Date','Forecast']
#     dates = list(weather.keys())
#     forecast = list(weather.values())
#     for i in range(1,len(dates)):
#         csv1['Date'] = dates[i]
#         csv1['Forecast'] = forecast[i]
#         csv_row.append(csv)
#     with open('Names.csv', 'w') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames = field_names)
#         writer.writeheader()
#         writer.writerows(csv_row)
#     return redirect('/'+str(dates[0]))

@app.route('/setalarm/<id>', methods=['GET','POST'])
def thread(id):
    t=Thread(target=alarm,args=(id,))
    t.run()

@app.route('/logout')
def logout():
    return redirect('/')

def alarm(id):
    time = request.form.get('time')
    if len(time) != 11:
        vali = 'Incorrect format'
    elif int(time[:2]) > 12 and int(time[:2])<0:
        vali = 'Incorrect format'
    elif int(time[3:5]) >= 60 and int(time[3:5]) < 0:
        vali = 'Incorrect format'
    elif int(time[6:8]) >= 60 and int(time[6:8]) < 0:
        vali = 'Incorrect format'
    elif time[9:11].lower() != 'am' and time[9:11].lower() != 'pm':
        vali = 'Incorrect format'
    else:
        vali = 'ok'
    
    # w = Label(root, text=vali,font=("Helvetica 10 bold"),fg="red")

    if vali != 'ok':
        # print(vali)
        # print(time)
        # w.pack()
        flash(vali)
    else:
        flash(f'Alarm set for {time}')
        # Label(root, text=f'Alarm set for {time}',font=("Helvetica 10 bold"),fg="red").pack()
        while True:
            # print('sleep')
            now = datetime.datetime.now()
            if int(time[:2]) == int(now.strftime('%I')) and int(time[3:5]) == int(now.strftime('%M')) and int(time[6:8]) == int(now.strftime('%S')) and time[9:11].upper() == now.strftime('%p'):
                # print('Wake Up!')
                # Label(root, text=f'Wake Up!',font=("Helvetica 10 bold"),fg="red").pack()
                flash('Wake Up!')
                playsound('alarm_classic.mp3')
                break
    return redirect('/'+id)

if __name__=='__main__':
    app.run(debug=True)

