from flask import Flask,redirect,url_for,render_template,request,flash
from flask_mail import Mail,Message
from random import randint
from projectdatabase import Register,Base,User
from sqlalchemy.orm import sessionmaker 
from sqlalchemy import create_engine
from flask_login import LoginManager,login_user,current_user,logout_user,login_required


engine=create_engine('sqlite:///iiit.db',connect_args={'check_same_thread':False},echo=True)
Base.metadata.bind=engine
DBSession=sessionmaker(bind=engine)
session=DBSession()

app=Flask(__name__)
app.secret_key='super_secret_key'

login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'




app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='babymattaparthi511@gmail.com'
app.config['MAIL_PASSWORD']='vigneswara'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True

mail=Mail(app)
otp=randint(000000,999999)

@app.route("/hello")
def demo():
	return "<font color=red>hello world welcome to IIIT rgukt"


@app.route("/student/register")
def reg():
	return "register page"

@app.route("/data/<name>/<int:number>")

def data(name,number):
	return "hello {} number {}". format(name,number)

@app.route("/admin")
def admin():
	return "hello admin"

@app.route("/student")
def student():
	return "hello student"

@app.route("/info/<name>")
def info(name):
	if name=='admin':
		return redirect(url_for('admin'))
	elif name=='student':
		return redirect(url_for('student'))
	else:
		return "no data available"

@app.route("/demo_html")
def sample_html():
	return render_template('index.html')

@app.route("/loginform")
def loginform():
	return render_template('login_form.html')

@app.route("/applicationform")
def applicationform():
	return render_template('appicationform.html')

@app.route("/person/<pname>/<int:number>/<pbranch>")
def per(pname,number,pbranch):
	return render_template('sample.html',name=pname,num=number,branch=pbranch)

@app.route("/table/<int:number>")
def table(number):
	return render_template("table.html",n=number)

dummy=[{"name":'siri','dob':'1996','org':'sdc'},{"name":'baby','dob':'1998','org':'adde'}]
@app.route("/dummy_data")
def dummy_data():
	return render_template('dummy.html',data=dummy)


@app.route("/file_upload",methods=['POST','GET'])
def file_upload():
	return render_template('file_upload.html')

@app.route("/success",methods=['POST','GET'])
def success():
	if  request.method=='POST':
		f=request.files['file']
		f.save(f.filename)
		return render_template("files.html",file_name=f.filename)


@app.route("/email")
def  ssemail():
	return render_template("demo_email.html")

@app.route("/email_verify",methods=['POST','GET'])
def verify_email():
	email=request.form['email']
	msg=Message('One Time Password',sender='babymattaparthi511@gmail.com',recipients=[email])
	msg.body=str(otp)
	mail.send(msg)
	return render_template('email_verify.html')

@app.route("/email_validate",methods=['POST','GET'])
def email_validate():
	user_otp=request.form['otp']
	if otp==int(user_otp):
		register=session.query(Register).all()
		flash("successfully login...")
		return redirect(url_for('showData',reg=register))
		flash("please check your otp")
	return render_template(url_for("email_verify.html"))

@login_required
@app.route("/show", methods=['POST','GET'])
def showData():
	register=session.query(Register).all()
	return render_template('show.html',reg=register)


@app.route("/add",methods=['POST','GET'])
def addData():
	if request.method=='POST':
		newData=Register(name=request.form['name'], 
			surname=request.form['surname'],
			email=request.form['email'],
			branch=request.form['branch'])
		session.add(newData)
		session.commit()

		flash("successfully added %s" %(newData.name))
		return redirect(url_for('showData'))
	
	else:

		return render_template('add.html')


@app.route("/<int:register_id>/edit", methods=['POST','GET'])
def editData(register_id):
	editedData=session.query(Register).filter_by(id=register_id).one()
	if request.method=='POST':
		editedData.name=request.form['name']
		editedData.surname=request.form['surname']
		editedData.email=request.form['email']
		editedData.branch=request.form['branch']


		session.add(editedData)
		session.commit()
		flash("successfully Edited %s" %(editedData.name))

		return redirect(url_for('showData'))
	else:
		return render_template('edit.html',register=editedData)

@app.route("/<int:register_id>/delete",methods=['POST','GET'])
def deleteData(register_id):
	delData=session.query(Register).filter_by(id=register_id).one()

	if request.method=='POST':
		session.delete(delData)
		session.commit()
		flash("successfully Deleted %s" %(delData.name))

		return redirect(url_for('showData',register_id=register_id))
	else:
		return render_template('delete.html',register=delData)

@app.route("/")
def index():
	return render_template('index.html')

@app.route("/account", methods=['POST','GET'])
@login_required
def account():
	return render_template('account.html')



@app.route("/register", methods=['POST','GET'])
def register():
	if request.method=='POST':
		userData=User(name=request.form['name'],email=request.form['email'],password=request.form['password'])
		session.add(userData)
		session.commit()

		return redirect(url_for('index'))
	else:
		return render_template('register.html')


@login_required
@app.route("/login",methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('showData'))
	try:
		if request.method=='POST':
			user = session.query(User).filter_by(
				email=request.form['email'],
				password=request.form['password']).first()
		

			if user:
				login_user(user)
				#next_page=request.args.get('next')
				return redirect(url_for('showData'))
				#return redirect(next_page) if next_page else redirect(url_for('showData'))
			else:
				flash("login failed")
		else:
			return render_template('login.html',title="login")
	except Exception as e:
		flash("login failed....")
	else:
		return render_template('login.html',title="login")


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user_id):
	return session.query(User).get(int(user_id))

if __name__=='__main__':
	app.run(debug=True)