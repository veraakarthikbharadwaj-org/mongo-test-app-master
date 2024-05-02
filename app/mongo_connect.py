#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# Import the required Python modules and Flask libraries
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_pymongo import PyMongo
from pymongo import MongoClient
import os
import logging
import sys

app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'users'
app.config["MONGO_URI"] = "mongodb://localhost:27017/users"
app.secret_key = os.urandom(32)
mongo = PyMongo(app)
db_operations = mongo.db.users

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


# not for vuln demonstration purposes, just an api for testing purposes to confirm
# that the correct data is appearing in the database
# Same functionality and function contents as the former '/read' app route
@app.route("/api/list_users", methods=['GET'])
def fetch_users():
    user = list(db_operations.find())
    output = [{'User' : i['username'], 'user id' : i['user_id'], 'email address' : i['email']} for i in user]
    return jsonify(output)


# Poorly Coded Login Functionality Endpoints
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        user = db_operations.find_one({"username": username})
        if user and user["password"] == password:
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid credentials, please try again!"
            return render_template('login.html', error=error)
    return render_template('login.html', error=error)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', name=session['username'])


@app.route('/logout')
def logout():
    return render_template('logout.html')


# Vulnerable Endpoints
@app.route("/user/<name>")
def where_op_inject(name):
    resp = db_operations.find({ '$where': f'function() {{ return(this.username == "{name}") }}' })
    retstr = "<pre>"
    for user in resp:
        retstr += f"{user['username']} with email address '{user['email']}'\n"
    return(retstr)


@app.route("/user_id/<uid>")
def regex_inject(uid):
    resp = db_operations.find({'user_id' : {'$regex': uid}})
    retstr = "<pre>"
    for user in resp:
        retstr += f"{user['username']} with user id '{user['user_id']}'\n"
    return(retstr)


if __name__ == '__main__':
    app.run(debug=True)