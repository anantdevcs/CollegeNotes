from flask import Flask,render_template,request,session,redirect, send_file
import pathlib
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from user import user
from upload import  upload

engine = create_engine("postgres://ukvpqsdphiottc:e796c82bf26cb08ef704ad6ed8bec02fe41a757726462727ab0ad9b6aca57c6e@ec2-52-200-119-0.compute-1.amazonaws.com:5432/d61hr65dl2k6ti")
db = scoped_session(sessionmaker(bind=engine))


app = Flask(__name__)
app.secret_key = "hellothere"
UPLOAD_FOLDER = '/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
import uuid


@app.route('/')

def index():
    feed_obj_arr = db.execute('SELECT * from filesref order by created_at DESC').fetchmany(10)
    if  "user" in session:
        return render_template('homepage.html',feed_obj_arr = feed_obj_arr,userid = session['user'])
    else:
        return render_template('homepage.html',feed_obj_arr = feed_obj_arr)

@app.route("/login",methods=['GET', 'POST'])

def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        user_id = request.form['user_id']
        password = request.form['password']
        matched = db.execute('SELECT * from users where user_id = :user and password = :password',{
            "password":password, "user":user_id}).fetchall()
        if len(matched) == 0:
            return render_template('login.html', error_msg = "Incorrect username or password")
        else:
            session['user'] = user_id
            session['college'] =  db.execute('SELECT * from users where user_id = :userid',{"userid" : user_id}).fetchall()[0]['password']
            print(session)

            return render_template('homepage.html', userid = session['user'])


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
        session['user'] = user_data['userID']
        session['college'] = user_data['college']
        return render_template('homepage.html', userid = session['user'])

@app.route('/upload',methods=['POST', 'GET'])

def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = request.form['filename']
        description = request.form['description']
        unique_file_name = str(uuid.uuid4())
        extention = file.filename.split('.')[-1]
        unique_file_name += '.' + extention
        file.save(unique_file_name )
        db.execute('INSERT INTO filesref (user_id, unique_filename, publicfilename, description) VALUES (:user_id, :unique_filename, :publicfilename, :description) ;',
                    {"user_id":session['user'], "unique_filename":unique_file_name , "publicfilename":filename, "description":description}   )
        db.commit()                   
        print("Success")
    if "user" not in session:
        return render_template('login.html', error_msg = "Login to Upload files")
    else:

        # file = request.files['file']
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], "##!!@@!!12qq"))
        # print("Success")
        return render_template('upload.html', userid = session['user'])

  
@app.route('/download/<filename>')
def download(filename):

    return send_file(filename,attachment_filename=filename)


@app.route('/delete/<unique_file>')

def delete(unique_file):
    if (db.execute('SELECT * from filesref where unique_filename = :unique_file AND user_id = :user_id',{"unique_file":unique_file, "user_id":session['user']}).fetchall()) is  None:
        return render_template('login.html', error_msg = "Login to Perform Action :X")
    if  'user' in session :#and db.execute('SELECT * from filesref where unique_filename = :unique_file',{"unique_file":unique_file}).fetchone()['user_id'] == session['user']:
        db.execute('DELETE from filesref where unique_filename = :unique_file AND user_id = :user_id', {'unique_file':unique_file, "user_id":session['user']})
        try:
            os.remove(unique_file)
        except :
            print("COunld not delete file")
        db.commit()
        return redirect('/')
    else:
        return render_template('login.html', error_msg = "Login to Perform Action")

@app.route('/dashboard')

def dashboard():
    if "user" in session  :

        user_name = session['user']
        uploads = db.execute('SELECT * from filesref WHERE user_id = :user_id',{'user_id' : user_name} ).fetchall()

        return render_template('dashboard.html',uploads = uploads)
    else:
        return render_template('login.html', error_msg = "Login to Perform Action")


@app.route('/home')
def home():
    return render_template('home.html') 

@app.route('/popular')

def popular():
    return render_template('popular.html')


@app.route('/college_wise')   

def college_wise():
    return render_template('college_wise.html')

@app.route('/explore', methods = ['POST', 'GET'])

def explore():
    if request.method == 'POST':
        return render_template('explore.html')

    else:
        return render_template('explore.html')


   

if __name__ == '__main__':

    app.run(debug=True)
