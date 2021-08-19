from flask import Flask, render_template, redirect, jsonify, escape, url_for, flash, session, request, abort,send_from_directory
import os
from werkzeug.utils import secure_filename
import math

app = Flask(__name__)
app.secret_key="abc123"

uname="admin"
password="password"

#size for max folder size on media server
MAX_USER_CONTAINER_SIZE=10000 * 1024 * 1024

app.config['UPLOAD_FOLDER'] = 'static/files/vids/'

ALLOWED_EXTENSIONS = set(['avi', 'mp4'])

#max size for each file uploaded
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024

currCount=0
timeSincelast=0

# get list of all videos in this path
vids = os.listdir(app.config['UPLOAD_FOLDER'])

paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in vids]

#gets size of file
def getFileSize(stream):
    return len(stream.read())

#checkcs if allowed file type
def isAllowedFileType(fileName):
    print(fileName)
    ext = fileName[fileName.rindex(".")+1:]
    return ext in ALLOWED_EXTENSIONS

#get size of contents folder
def getContainerSize():
    size=0
    for path, dirs, files in os.walk(os.path.join(app.config['UPLOAD_FOLDER'])):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)
    return size

BLOCKED_LIST=[]
incorrect_login=0

@app.before_request
def limit_addr_req():
    if request.remote_addr in BLOCKED_LIST:
        abort(404)


@app.route("/")
def home():
    if request.method == 'GET':
        if not 'username' in session:
            return redirect(url_for('login'))
        else:
            loggedIn=True
            return render_template('index.html',loggedIn=loggedIn)

@app.route("/mediahome",methods=['GET'])
def mediahome():
    if request.method =='GET':
        if not 'username' in session:
            return redirect(url_for('login'))
        else:
            paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in vids]

            ffLink=""
            name="n/a"
            if(len(paths)>0):
                ffLink = paths[0]
                name = ffLink[ffLink.rindex("/") + 1:]
            print(ffLink)
            tSize=0
            tSize= getContainerSize()
            print(tSize)
            loggedIn = True
            return render_template('myVideoPlayer.html',size=tSize,name=name,vLink=ffLink,files=paths,loggedIn=loggedIn)


@app.route("/media",methods=['GET','POST'])
def medianew():
    tSize=0
    tSize= getContainerSize()
    tSize = math.floor(tSize / 1000000)
    per = (tSize / 10000) * 100
    per = math.floor(per)
    print(per)

    if request.method =='GET':

        if not 'username' in session:
            return redirect(url_for('login'))
        else:
            loggedIn = True
            return render_template('myfiles.html',loggedIn=loggedIn)

    elif request.method == 'POST':
        if not 'username' in session:
            return redirect(url_for('login'))
        else:
            loggedIn = True
            file = request.files['fileName']
            tFSize = getFileSize(file.stream)
            newBase = 0
            if tSize > MAX_USER_CONTAINER_SIZE:
                return render_template('myfiles.html',size=tSize,
                                       space_used="Container Exceeds Maximum Limit",loggedIn=loggedIn)
            if tFSize >= MAX_USER_CONTAINER_SIZE:
                return render_template('myfiles.html',size=tSize,
                                       space_used="File Exceeds Maximum Limit",loggedIn=loggedIn)
            if file and isAllowedFileType(file.filename):
                filename = secure_filename(file.filename)
                filename = filename
                file.seek(0)
                try:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                    return  redirect(url_for('mediahome'))
                except:
                    return render_template('myfiles.html',
                                           space_used="Sorry. Couldnt save the file",loggedIn=loggedIn)



@app.route("/media/<index>",methods=['GET'])
@app.route("/media  ",methods=['GET'])
def myVideoPlayer(index):
    if request.method == 'GET':
        if not 'username' in session:
            return redirect(url_for('home'))
        else:
            loggedIn = True
            tSize=0
            tSize= getContainerSize()
            print(tSize)
            paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in vids]
            if index !=0 or index !="none":
                ffLink = paths[int(index)]
            else:
                ffLink = paths[0]
            name = ffLink[ffLink.rindex("/")+1:]

            return render_template('myVideoPlayer.html',size=tSize,name=name,vLink=ffLink,files=paths,loggedIn=loggedIn)


@app.route("/login",methods=['GET','POST'])
def login():

    if request.method == 'GET':
        if 'username' in session:
            return redirect(url_for('home'))
        else:
            return render_template('login.html')
    elif request.method == 'POST':
        if 'username' in session:
            return redirect(url_for("login"))
        else:
            username = escape(request.form.get('username'))
            pword = escape(request.form.get('password'))

            print(username +" : "+username)
            print(pword +" : "+password)


            if username == uname and pword == password:
                session['username'] = uname
                return redirect(url_for('home'))
            else:
                error = "invalid credentials"
                return render_template('login.html', error=error)


@app.route("/logout")
def logout():
    if 'username' in session:
        session.pop('username',None)
        return redirect(url_for('home'))
    else:
        return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)



