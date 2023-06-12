from flask import Flask, render_template, url_for ,request,redirect,flash
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from werkzeug.utils import secure_filename
from GPSPhoto import gpsphoto
from flask_mysqldb import MySQL
from datetime import datetime
import urllib.request
import os


app=Flask(__name__)

UPLOAD_FOLDERS='static/uploads/'
app.secret_key="secret keys"
app.config['UPLOAD_FOLDER']= UPLOAD_FOLDERS
app.config['MAX_CONTENT_LENGTH']=16*1024*1024
app.config['MYSQL_HOST']="sql12.freesqldatabase.com"
app.config['MYSQL_USER']="sql12624535"
app.config['MYSQL_PASSWORD']=""
app.config['MYSQL_DB']="sql12624535"

mysql=MySQL(app)

ALLOWED_EXTENSIONS_SET=set(['jpg','png','jpeg','gif','JPG','PNG','JPEG','GIF'])

@app.route("/",methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/uploadImage', methods=['GET','POST'])
def uploadImage():
      file=request.files['file']
      if file and allowed_file(file.filename):
         filename=secure_filename(file.filename)
         file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
         data = gpsphoto.getGPSData("static/uploads/"+filename)
         flash('Image successfully uploaded!')
         districtName=request.form['district'].lower()
         latitude=data['Latitude']
         if latitude<0:
             latitude= -1 * latitude
         longitude=data['Longitude']
         if longitude<0:
             longitude= -1 * longitude
         dateTime=datetime.now()
         filename="static\\uploads\\" + filename

         cur=mysql.connection.cursor()
         cur.execute("INSERT into geospatial(photo,district,latitude,longitude,date) values(%s,%s,%s,%s,%s)",(filename,districtName,latitude,longitude,dateTime))
         mysql.connection.commit()
         cur.close()
      return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_SET

@app.route('/location',methods=['GET','POST'])
def findLocation():
    return render_template('location.html')

@app.route('/displayImage',methods=['GET','POST'])
def displayImage():
    dname=request.form['dname']
    disName=dname.lower()
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM geospatial where district=%s",[disName])
    result = cur.fetchall()
    img=[]

    for i in result:
        img.append(os.path.join(app.config['UPLOAD_FOLDER'], i[1]))

    return render_template('location.html',img=img,result=result,dname=dname)

if __name__ == "__main__":
    app.run(debug=True)