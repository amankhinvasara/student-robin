from flask import Flask, request, jsonify, session, redirect, url_for, flash, render_template
from robin_sql import *
from flask_login import LoginManager, login_required, login_user, logout_user

#from flask.ext.security import login_required

print("imports complete")

login_manager = LoginManager()

app = Flask(__name__)

cur,conn = curse()

app.secret_key = "odf34jrj089942u9n.qn0i208r/132i9u86vqbnermmlmcvij"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return is_student(user_id,cur,conn)


@app.route("/register",methods=["GET","POST"])
def reg_student():
    print("in register route")
    student_username = request.form.get("student_username")
    if student_username is None:
        return render_template("register.html",error_msg="")
    print("student_username is not None")
    student_pw = request.form.get("student_pw").strip()
    student_conf_pw = request.form.get("student_conf_pw").strip()
    if student_pw != student_conf_pw:
        return render_template("register.html",error_msg="Passwords don't match")
    student_first_name = request.form.get("student_first_name")
    student_last_name = request.form.get("student_last_name")
    student_email = request.form.get("student_email")
    student_phone = request.form.get("student_phone").replace("(","").replace(")","").replace("-","")
    student_grade = request.form.get("student_grade")
    student_school = request.form.get("student_school")

    student_courses = request.form.get("student_courses")

    in_dict = {"student_username":student_username, "student_pw":encode(student_pw),
            "student_first_name":student_first_name,"student_last_name":student_last_name, "student_email":student_email,
            "student_phone":student_phone, "student_school":student_school, "student_grade":student_grade, "student_courses":student_courses} 
    print("in_dict created")

    y = register_student(in_dict,cur,conn)

    print("register_student func completed")

    if y == 200:
        print("SUCCESS")
        flash("Succesfully Registered")
        return redirect(url_for("login"))

    else:
        return render_template("register.html",error_msg = y)

@app.route("/login",methods=["GET","POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    checkbox = request.form.get("remember")
    if username is None:
        return render_template("login.html",error_msg="")
    else:
        global user_man
        user_man = User(username,"student")
        login_user(user_man,remember=checkbox)
        if user_man.student_obj is None:
            return render_template("login.html",error_msg = "Username was not found")
        if password!=decode(user_man.student_obj.row_dict["student_pw"]):
            logout_user()
            return render_template("login.html",error_msg="incorrect password, please try again")

        return redirect(url_for('profile'))

"""
# blueprint for auth routes in our app
import auth as auth_blueprint
app.register_blueprint(auth_blueprint)"""

@app.route("/")
def hello():
    return "<h1>Hello world</h1>"

@app.route("/profile")
@login_required
def profile():
    big_string = ""
    info_dict = user_man.student_obj.row_dict
    for key in info_dict.keys():
        if key == "student_pw":
            big_string+=key+"   -------------  "+decode(info_dict[key])+"\n"
        else:
            big_string+=key+"   -------------  "+str(info_dict[key])+"\n"
    return big_string

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("https://www.robineducation.org")

if __name__=="__main__":
    app.run(debug=True,port=5000,host="0.0.0.0",threaded=True)