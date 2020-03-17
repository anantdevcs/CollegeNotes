from flask import Flask,render_template,request,session,redirect

import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://ukvpqsdphiottc:e796c82bf26cb08ef704ad6ed8bec02fe41a757726462727ab0ad9b6aca57c6e@ec2-52-200-119-0.compute-1.amazonaws.com:5432/d61hr65dl2k6ti")
db = scoped_session(sessionmaker(bind=engine))


app = Flask(__name__)

@app.route('/')

def index():
    return render_template('homepage.html')


@app.route("/login")

def login():
    return render_template("login.html")


@app.route('/signup')

def signup():

    return render_template('signup.html')

@app.route('/validate',methods=['POST'])

def validate():
    user_data = request.form;

    print(user_data)
    confilcting_users = db.execute("Select * from Users where user_id = :userID",{"userID" : user_data['userID']}).fetchall()
    if len(confilcting_users) != 0:
        return render_template('signup.html', error_msg = "This UserID is taken")
    else:
        db.execute("INSERT into users (user_id, password, college) VALUES (:UserID,:Password, :College);", 
        {"UserID":user_data['userID'], "Password":user_data['password'], "College":user_data['college']} )

        db.commit()
    return redirect('/')



if __name__ == '__main__':

    app.run(debug=True)
