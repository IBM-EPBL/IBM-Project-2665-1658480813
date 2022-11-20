import numpy as np
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input
from flask import Flask,request,render_template,redirect,url_for,session
from cloudant.client import Cloudant
from flask_session import Session

client=Cloudant.iam('695cf4af-72b0-4809-a691-e501ac44c36f-bluemix','vsMu1-Dj7UH49P-WwAfOdcR6pt-pjvv61FXMzvpYvHFL',connect=True)
app=Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
model=load_model("first-model.h5")

usersDB=client.create_database('users')
userDetailsDB=client.create_database('user-history')

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/index.html')
def home():
  return render_template('index.html')

@app.route('/prediction.html')
def predict():
    return render_template('prediction.html')

@app.route('/prediction')
def predict1():
    return render_template('prediction.html')

@app.route('/get-prediction',methods=['POST'])
def getRes():
    if request.method=='POST':
        
        f=request.files['image']
        basepath=os.path.dirname(__file__)
        filepath=os.path.join(basepath,'uploads',f.filename)
        f.save(filepath)

        img=image.load_img(filepath,target_size=(299,299))
        x=image.img_to_array(img)
        x=np.expand_dims(x,axis=0)
        img_data=preprocess_input(x)
        prediction=np.argmax(model.predict(img_data),axis=1)
        index=['No Diabetic Retinopathy','Mild Diabetic Retinopathy','Moderate Diabetic Retinopathy','Severe Diabetic Retinopathy','Proliferative Diabetic Retinopathy']
        result=str(index[prediction[0]]) 
        user=session.get('uid')       
        query={'_id':{'$eq':user}}
        data=usersDB.get_query_result(query)
        return render_template('prediction.html',prediction=result)

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/login-validate',methods=['POST'])
def loginVal():
    x=[param for param in request.form.values()]
    user=x[0]
    pwd=x[1]
    query={'_id':{'$eq':user}}
    data=usersDB.get_query_result(query)
    if(len(data.all())==0):
        return render_template('login.html',status="Username Not found!!!")
    else:
        if((user==data[0][0]['_id'] and pwd==data[0][0]['pwd'])):
            session["name"]=data[0][0]['name']
            session["uid"]=data[0][0]['_id']
            print(session.get("name"))
            return redirect('/prediction')
        else:
            return render_template('login.html',status="Incorrect Username or Password!!!") 

@app.route('/registration.html')
def register():
    return render_template('registration.html')

@app.route('/reg-validate',methods=['POST'])
def regVal():
    x=[param for param in request.form.values()]
    session["name"] = x[0]
    session['uid']=x[1]
    data={
        '_id':x[1],
        'name':x[0],
        'pwd':x[2]
    }
    data1={
        '_id':x[1],
        'hist':[]
    }
    query={'_id':{'$eq':data['_id']}}
    docs=usersDB.get_query_result(query)
    if(len(docs.all())==0):
        u=usersDB.create_document(data)
        d=userDetailsDB.create_document(data1)
        return render_template('registration.html',status='Registration Successful!!')
    else:
        return render_template('registration.html',status='User Already Exists!!')

@app.route('/logout.html')
def predict1():
    session['name']=None
    session['uid']=None
    return render_template('logout.html')        

if __name__=="__main__":
  app.run(debug=False)