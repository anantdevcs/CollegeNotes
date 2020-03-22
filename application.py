from flask import Flask,render_template,request,session,redirect, send_file
import pathlib
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from user import user
from upload import upload as upload_obj

MAX_DOWN = 5


engine = create_engine("postgres://ukvpqsdphiottc:e796c82bf26cb08ef704ad6ed8bec02fe41a757726462727ab0ad9b6aca57c6e@ec2-52-200-119-0.compute-1.amazonaws.com:5432/d61hr65dl2k6ti")
db = scoped_session(sessionmaker(bind=engine))


app = Flask(__name__)
app.secret_key = "hellothere"
UPLOAD_FOLDER = '/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
import uuid
# Create a directory in a known location to save files to.
uploads_dir = os.path.join(app.instance_path, 'uploads')
# if 'uploads' not in 
# os.makedirs(uploads_dir)


@app.route('/')

def index():
    return redirect('/home')

@app.route("/login",methods=['GET', 'POST'])

def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        user_id = request.form['user_id']
        password = request.form['password']
        #Making a query
        Q = db.execute('SELECT * from users_db where user_id = :user_id  and password = :password',
            {'user_id':user_id, 'password':password}
        ).fetchall()
        if len(Q) == 0:
            return render_template('login.html', error_message = "Wrong Username or password")
        else:
            session['user'] = user_id
            session['college'] = Q[0]['college']
            session['num_downloads'] = 0
            session['num_uploads'] = 0
            return redirect('home')

@app.route('/signup', methods = ['POST', 'GET'])

def signup():
    if request.method == 'POST':
        #Check if this user id exists
        user_id = request.form['user_id']
        college = request.form['college']
        password = request.form['password']
        num_downloads = 0
        num_uploads = 0
        if len(db.execute('SELECT * from users_db WHERE user_id = :user_id',{'user_id':user_id}).fetchall()) != 0:
            return render_template('signup.html', error_message = "This user already exists")
    try:
        db.execute('INSERT into users_db (user_id, college, num_downloads, num_uploads,password) values (:user_id, :college, :num_downloads, :num_uploads, :password)',
            {"user_id":user_id, "college":college, "num_downloads":0, "num_uploads":0, "password":password}
        )
        db.commit()
        session['user'] = user_id
        session['college'] = college
        session['num_downloads'] = 0
        session['num_uploads'] = 0
        return redirect('/home')
    except:
        return render_template('signup.html', error_message = "DB not respnding Excetion.Try after some time")

    else:
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
        #check if user is logged in 
        if 'user' not in session:
            return render_template( 'login.html' , error_message = "Login to upload files " )
        file = request.files['file']
        filename = file.filename
        topic = request.form['topic']
        unique_filename = str(uuid.uuid4())
        extention = file.filename.split('.')[-1]
        unique_filename += '.' + extention
        topic = request.form['topic']
        file.save(os.path.join(uploads_dir, unique_filename ) )
        db.execute('insert into file_db (unique_filename, filename, num_downloads, uploader, college, topic) values (:unique_filename, :filename, :num_downloads, :uploader, :college, :topic) ',
            {"unique_filename":unique_filename, "filename":filename, "num_downloads": 0, "uploader":session['user'], "college":session['college'], "topic":topic}
        )

        db.commit()                   
        
        return render_template('upload.html', success_message = "File Uploaded Successfully")
    
    else:
        return render_template('upload.html')


  
@app.route('/download/<unique_filename>/<filename>')
def download(unique_filename, filename):
    #file.save(os.path.join(uploads_dir, unique_filename ) )
    return send_file(os.path.join(uploads_dir, unique_filename ),attachment_filename=filename)


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
    cur_user = None
    if 'user'  in session:
        cur_user = user(user_id=session['user'],college=session['college'],num_downloads=session['num_downloads'],num_uploads=session['num_uploads'])
    
    
    top_users = []
    for user_dict in db.execute('SELECT * from users_db order by num_downloads desc LIMIT :MAX_DOWN',{'MAX_DOWN':MAX_DOWN}).fetchall():
        top_users.append(user(user_id=  user_dict['user_id'],college=user_dict['college'],num_downloads= user_dict['num_downloads'],num_uploads=user_dict['num_uploads']))
    recent_uploads = []
    for upload_dict in db.execute('SELECT * from file_db order by created_at desc LIMIT :MAX_DOWN', {'MAX_DOWN':MAX_DOWN} ).fetchall():
        recent_uploads.append(upload_obj(filename = upload_dict['filename'], num_downloads=upload_dict['num_downloads'], uploader = upload_dict['uploader'], college = upload_dict['college'] , unique_filename = upload_dict['unique_filename'] ,
        topic = upload_dict['topic']))

        
    return render_template('home.html', user = cur_user, top_users = top_users, recent_uploads = recent_uploads )

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

@app.route('/signout')

def signout():
    session.pop('user', None)
    
    return redirect('/home')

   

if __name__ == '__main__':

    app.run(debug=True)
