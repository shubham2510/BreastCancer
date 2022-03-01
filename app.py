import numpy as np
import pandas as pd
from flask import Flask, flash, request, render_template, flash, redirect, url_for, session,  request, abort

import config
from datetime import datetime

import mysql.connector


import pickle




mydb = mysql.connector.connect(
  host="sql6.freemysqlhosting.net",
  user="sql6476131",
  password="kt49YJuiZj",
  database="sql6476131"
)

mycursor = mydb.cursor(buffered=True)

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'



@app.route('/')
def home():
    return render_template('home.html',login=config.isLoggedIn())   

@app.route('/home')
def hom():
    return render_template('home.html',login=config.isLoggedIn())




@app.route('/signup')
def signup():
    return render_template('register.html',login=config.isLoggedIn())

@app.route('/signup', methods=['GET', 'POST'])
def register_post():
    # Output message if something goes wrong...
    msg = '' 
    
    name = request.form['name']
    
    mobile = request.form['mob'] 
    email = request.form['email'] 
    blood = request.form['blood'] 
    address = request.form['address'] 
    date = request.form['date'] 
    doctor = request.form['doc'] 
    password = request.form['password']
    
    mycursor.execute('SELECT * FROM users WHERE email =%s',(email,))
    account = mycursor.fetchone() 
    if account: 
        msg = 'Account already exists !'
    else:
        sq='INSERT INTO users VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)'
        mycursor.execute(sq, (name, mobile, email, blood, address, date, doctor, password, )) 
        mydb.commit()
        msg = 'You have successfully registered !'    
    return render_template('register.html', msg = msg) 


@app.route('/login')
def login():
    return render_template('log.html',login=config.isLoggedIn())

@app.route('/login', methods =['POST']) 
def login_post(): 
    msg = ''
    email = request.form['txtEmail']  
    password = request.form['password'] 
    print(email)
    print(password)
   
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute('SELECT * FROM users WHERE email = %s and password = %s', (email, password, )) 
    account = mycursor.fetchone()  
    if account: 
        session['loggedin'] = True
        session['id'] = account[0] 
        session['name'] = account[1] 
        session['email'] = account[3]
        session['mobile'] = account[4] 
        msg = 'Logged in successfully !'
        return redirect(url_for('dashboard')) 
    else: 
        msg = 'Incorrect username / password !'
        return render_template('log.html', msg = msg) 

@app.route('/contact')
def contactus():
    return render_template('contact-us.html',login=config.isLoggedIn())

@app.route('/contact', methods=['POST'])
def contact_form_post():
    mycursor = mydb.cursor()
    name = request.form['name']
    mobile = request.form['phonenumber']
    email = request.form['email']
    messageData = request.form['messages']


    try:
        sq='INSERT INTO contact VALUES (%s, %s, %s, %s, NULL)'
        mycursor.execute(sq, (name, mobile, email, messageData, )) 
        mydb.commit()
        flash="Hey "+ name +"! Your Message Has Been Sent Successfully ."
    except:
        flash="Hey "+ name +"! Sorry ... Some Internal Problem"
    return render_template('contact-us.html', flash=flash) 

@app.route('/dashboard')
def dashboard():
    if config.isLoggedIn():
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('login'))


@app.route('/dashboard/profile')
def profile():
    if config.isLoggedIn():
        uid=session['id']

        mycursor.execute('SELECT * FROM users WHERE uid =%s',(uid,))
        
        account = mycursor.fetchone()
        
        if account:
            name = account[1] 
            mobile = account[2]
            blood = account[4] 
            dob = account[6]
            address = account[5] 
            doctor = account[7]
            mycursor.execute('SELECT * FROM predict WHERE uid =%s',(uid,))
            acc = mycursor.fetchone()
            glucose=0
            typeof=''
            if acc is not None: 
                if acc[2] == '1':
                    predict=True
                    typeof=acc[3]
                else:
                    predict=False
            else:
                predict=False







        return render_template('dashboard/profile.html',login=config.isLoggedIn(),uid=session['id'], name=name,mobile=mobile,blood=blood,dob=dob,address=address,doctor=doctor,predict=predict,glucose=glucose,typeof=typeof)
    else:
        return redirect(url_for('login'))
    
  
@app.route('/dashboard/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('email', None)
    session.pop('id', None)
    session.pop('name', None)
  
    flash="Logged Out Successfully"
    
    return render_template('log.html',msg1=flash)

@app.route('/dashboard/logout',methods=['POST'])
def logout_post():
    msg = ''
    email = request.form['txtEmail']  
    password = request.form['password'] 
    print(email)
    print(password)
   
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute('SELECT * FROM users WHERE email = %s and password = %s', (email, password, )) 
    account = mycursor.fetchone()  
    if account: 
        session['loggedin'] = True
        session['id'] = account[0] 
        session['name'] = account[1] 
        session['email'] = account[3]
        session['mobile'] = account[4] 
        msg = 'Logged in successfully !'
        return redirect(url_for('dashboard')) 
    else: 
        msg = 'Incorrect username / password !'
        return render_template('log.html', msg = msg) 


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',login=config.isLoggedIn())

@app.route('/dashboard/predict')
def prdict():
    if config.isLoggedIn():
        return render_template('index.html',login=config.isLoggedIn())
    else:
        return redirect(url_for('login'))

@app.route('/dashboard/predict',methods=['POST'])
def predict():
  input_features = [int(x) for x in request.form.values()]
  features_value = [np.array(input_features)]

  features_name = ['clump_thickness', 'uniform_cell_size', 'uniform_cell_shape',
       'marginal_adhesion', 'single_epithelial_size', 'bare_nuclei',
       'bland_chromatin', 'normal_nucleoli', 'mitoses']

  df = pd.DataFrame(features_value, columns=features_name)
  output = model.predict(df)



  uid=session['id']

  if output == 4:
    res_val = "You have Breast cancer of Malignant type"
    pr='1'
    typ='Malignant'
  elif output == 2:
    res_val = "You have Breast cancer of Benign type"
    pr='1'
    typ='Benign'
  else:
    res_val = "You don't have Breast cancer"
    pr='0'
    typ=''


  predict=pr
  typeof=typ
  mycursor.execute('SELECT * FROM predict WHERE uid = %s ', (uid, )) 
  account = mycursor.fetchone()  
  if account:
      sql='UPDATE `predict` SET `predict`=%s,`typeof`=%s WHERE uid =%s'
      mycursor.execute(sql, (predict,typeof,uid, ))
      mydb.commit()
  else:
      sql='INSERT INTO predict VALUES (NULL, %s, %s, %s)'
      mycursor.execute(sql, (uid,  predict, typeof,))
      mydb.commit()

  return render_template('index.html', prediction_text='{}'.format(res_val))



if __name__ == "__main__":
    app.run(debug=True)
