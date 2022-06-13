from flask import Flask, render_template,request,redirect
import pickle
import sqlite3
import os
import numpy as np
import random
import smtplib
from flask_mail import Mail, Message
from config import mail_username, mail_password

currentloc=os.path.dirname(os.path.abspath(__file__))
    
app = Flask(__name__)

app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = mail_username
app.config["MAIL_PASSWORD"] = mail_password

mail=Mail(app)

class USER:
    def __init__(self,phone,name,account,password,balance,email):
        self.phone=phone
        self.name=name
        self.account_no=account
        self.password=password
        self.balance=balance
    def show(self):
        print(type(self.phone))
        print(type(self.name))
        print(type(self.balance))


@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/forgotpassword')
def renderpassword():
    return render_template('forgotpassword.html')


@app.route('/changepassword',methods=['POST'])
def rendernewpassword():
    phone=int(request.form['phoneno'])
    password=str(request.form['newpassword'])
    
    sqlconnection=sqlite3.Connection(currentloc + "\\users.db")
    sqlconnection.row_factory=sqlite3.Row
    cursor=sqlconnection.cursor()
    
    cursor.execute("UPDATE Login SET Password='{np}' where Phone_No={ph}".format(np=password,ph=phone))
    sqlconnection.commit()
    sqlconnection.close()
    return render_template('passwordchanged.html')


@app.route('/authentication',methods=["GET","POST"])
def authorization():
    if request.method=="POST":
        phone=request.form["phone"]
        passw=request.form["password"]
        
        sqlconnection=sqlite3.Connection(currentloc + "\\users.db")
        sqlconnection.row_factory=sqlite3.Row  #for accessing the columns and its values
        cursor=sqlconnection.cursor()
        
        query1="select Phone_No, Password from Login where Phone_No='{un}' AND Password='{pw}' ".format(un=phone,pw=passw)
        rows=cursor.execute(query1)
        rows=rows.fetchall()
        
        cursor.execute("Select * from Login where Phone_No='{un}' AND Password='{pw}' ".format(un=phone,pw=passw))
        row=cursor.fetchone()
        
        if len(rows)==1:
            obj=USER(row[0],row[1],row[2],row[3],row[4],row[5])
            sqlconnection.close()        
            
            return render_template('index.html',info=obj)
        else:
            print(row,rows)
            return render_template('failedlogin.html')

@app.route('/contact',methods=['GET','POST'])
def contact():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        msg = Message(subject=f"Mail from {name}",body=f"E-Mail Id: {email}\nPhone Number: {phone}\nMessage: {message}",sender=mail_username,recipients=[email])
        mail.send(msg)
        return render_template('contact.html',success=True)


    return render_template('contact.html')


@app.route('/indexpageform/<int:phone>',methods=['POST'])
def transaction(phone):
    money=request.form['amount']
    sqlconnection=sqlite3.Connection(currentloc + "\\users.db")
    sqlconnection.row_factory=sqlite3.Row
    cur=sqlconnection.cursor()
    ls=[]
    cur.execute("Select Balance from Login where Phone_No={ph}".format(ph=phone))
    row=cur.fetchone()
    if row['Balance']>=int(money):
        with open('credicard_model','rb') as f:
            modal=pickle.load(f)
        cur.execute("select * from Data where Phone_No={ph}".format(ph=phone))
        dat=cur.fetchone()
        
        print(dat[0],type(dat[0]))
        for i in range(1,29):
            ls.append(dat[i])
            
        ls.insert(0,random.randint(0,172792))
        ls.append(money)
        arr=np.array([ls])
        for i in arr:
            print(arr)
        y_hat=modal.predict(arr)
        
        if(y_hat==1 and dat[0]!=191290):
            remaining=row['Balance']-int(money)
            cur.execute("update Login set Balance={re} where Phone_no='{ph}'".format(re=remaining,ph=phone))
            sqlconnection.commit()
            sqlconnection.close()
            return render_template('success.html')
        else:
            # cur.execute("select * from Login where Phone_No={ph}".format(ph=phone))
            # email=cur.fetchone()
            # print(email)

            # msg = Message(subject=f"Mail from {email}",body=f"E-Mail Id: {email}\nSome malicious activity has been detected from your account!! Kindly check it out!!",sender=mail_username,recipients=[email])
            # mail.send(msg)
            
            return render_template('failedtransaction.html')
    else:
        return render_template('failed.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__== '__main__':
    app.run(debug=True)