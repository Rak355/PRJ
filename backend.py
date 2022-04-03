import imp
import json
from os import stat
from flask import Flask, flash, make_response, render_template, request, redirect, url_for, session, jsonify
app = Flask(__name__)

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate('./juhi-e61b7-ab27988f3855.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

app.secret_key = b'_P#@SFR^&%WSAX/'

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print("signup request recvd:", username, password)

        doc_ref = db.collection(u'users').document(username)
        doc = doc_ref.get()
        if doc.exists:
            flash("username already present")
            return redirect(url_for('signup'))
        else:
            doc_ref = db.collection(u'users').document(username)
            doc_ref.set({
                u'username': username,
                u'password': password,
            })
            flash("registered successfully")
            return redirect(url_for('signup'))
    else:
        return render_template('signup.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    # check if there is a session is already active
    try:
        username = session['username']
    except:
        username = None

    # redirect to main page if yes
    if username != None:
        print(username)
        return redirect(url_for('main'))
    
    # handler for login request
    if request.method == 'POST':
        # get the submitted username and password 
        username = request.form['username']
        password = request.form['password']

        print('login request recvd:', username, password)

        username_db = ''
        password_db = ''

        # get the username and password values present in the database
        doc_ref = db.collection(u'users').document(username)
        doc = doc_ref.get()
        if doc.exists:
            dic_c = doc.to_dict()
            username_db = dic_c['username']
            password_db = dic_c['password']
        
        # check if submitted and database credentials matches
        if username == username_db and password == password_db:
            session['username'] = username
            return redirect(url_for('main'))
            
        else:
            flash("Invalid credentials")
            return redirect(url_for('login'))
    else:
        return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# route handler for main page
@app.route("/main", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        print(request.form['value'])
        value = request.form['value']

        # load the table (initialy done on after main page is ready)
        if value == 'load_table':
            json_obj = load_table()
            return json_obj

        # delete row
        elif value == 'delete_row':
            # save the row's id to i
            i = request.form['i']
            
            # get the reference to the selected row
            doc_ref = db.collection(u'users').document(session['username']).collection(u'company').document(i)
            doc = doc_ref.get()
            
            # delete the row and return the new table data 
            doc.reference.delete()
            json_obj = load_table()
            return json_obj

        # edit row
        elif value == 'edit_row':
            # get the edit data
            i = request.form['i']
            name = request.form['name']
            website = request.form['website']
            phoneno = request.form['phoneno']
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            country = request.form['country']
            industry = request.form['industry']

            # get the document reference to the selected row
            doc_ref = db.collection(u'users').document(session['username']).collection(u'company').document(name)
            doc = doc_ref.get()

            # check if company already exists
            if doc.exists and i != name:
                print('company already exists')
                return 'company already exists'
            else:
                # eliminate the older document
                doc_ref = db.collection(u'users').document(session['username']).collection(u'company').document(i)
                doc = doc_ref.get()
                doc.reference.delete()

                # save the new data
                doc_ref = db.collection(u'users').document(session['username']).collection(u'company').document(name)
                doc = doc_ref.get()
                doc_ref.set({
                    u'name': name,
                    u'website': website,
                    u'phoneno': phoneno,
                    u'address': address,
                    u'city': city,
                    u'state': state,
                    u'country': country,
                    u'industry': industry
                })
            json_obj = load_table()
            return json_obj

        # add new row
        elif value == 'add_row':
            # get add data
            name = request.form['name']
            website = request.form['website']
            phoneno = request.form['phoneno']
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            country = request.form['country']
            industry = request.form['industry']

            i = name

            # get the document reference to the selected row
            doc_ref = db.collection(u'users').document(session['username']).collection(u'company').document(name)
            doc = doc_ref.get()

            # check if company already exists
            if doc.exists:
                print('company already exists')
                return 'company already exists'
            else:
                # save the new data
                doc_ref = db.collection(u'users').document(session['username']).collection(u'company').document(name)
                doc = doc_ref.get()
                doc_ref.set({
                    u'name': name,
                    u'website': website,
                    u'phoneno': phoneno,
                    u'address': address,
                    u'city': city,
                    u'state': state,
                    u'country': country,
                    u'industry': industry
                })
            json_obj = load_table()
            return json_obj

    else:
        return render_template('main.html')

# function to send table data
def load_table():
    # get the document reference
    doc_ref = db.collection(u'users').document(session['username']).collection(u'company')
    doc = doc_ref.get()

    # build the json object by concatenating strings
    json_str = '{"data":['

    # flag to check if there is any record for this company
    item_flag = False
    for i in doc:
        json_str = json_str + '['

        # set flag true if there is a record
        item_flag = True

        if i.exists:
            print(i.id)
            dic_c = i.to_dict()
            json_str = json_str + '"' + dic_c['name'] + '"'
            json_str = json_str + ',' + '"' + dic_c['website'] + '"'
            json_str = json_str + ',' + '"' + dic_c['phoneno'] + '"'
            json_str = json_str + ',' + '"' + dic_c['address'] + '"'
            json_str = json_str + ',' + '"' + dic_c['city'] + '"'
            json_str = json_str + ',' + '"' + dic_c['state'] + '"'
            json_str = json_str + ',' + '"' + dic_c['country'] + '"'
            json_str = json_str + ',' + '"' + dic_c['industry'] + '"'
            json_str = json_str + ',' + '"<button id=\'edit'+ i.id +'\' onclick=edit(\''+ i.id + '\')>edit</button><button id=\'delete' + i.id + '\' onclick=del(\'' + i.id +'\')>delete</button>"'
            json_str = json_str + '],'

    # if there is a record then trim the last comma separator in the list        
    if item_flag == True:
        json_str = json_str[:len(json_str)-1]
    # close the json string
    json_str = json_str + ']}'

    print(json_str)

    # finally convert the string to json object
    json_obj = json.loads(json_str)
    return jsonify(json_obj)
