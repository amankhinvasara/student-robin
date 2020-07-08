import psycopg2
import json
import datetime
import random
import string

def curse():
	DATABASE_URL = "postgres://gabndxim:JL5TacPEmYtgaibI9qM-pwBJ40W3glDp@ruby.db.elephantsql.com:5432/gabndxim"
	global conn
	conn = psycopg2.connect(DATABASE_URL,sslmode='require')

	global cur
	cur = conn.cursor()
	conn.autocommit = True
	return (cur,conn)

def create_students_table():
	cur.execute("""CREATE TABLE students (student_username varchar PRIMARY KEY, student_pw varchar,
			student_first_name varchar,student_last_name varchar, student_email varchar UNIQUE, student_phone bigint,
			student_school varchar, student_grade smallint, student_courses varchar);""")
def create_parents_table():
	cur.execute("""CREATE TABLE parents (parent_id serial PRIMARY KEY, parent_username varchar, parent_pw varchar, parent_first_name varchar,
			parent_last_name varchar, parent_phone integer, parent_email varchar, student_id int, payment_status varchar, plan_id int);""")
def create_assignments_table():
	cur.execute("""CREATE TABLE assignments (assignment_id serial PRIMARY KEY, assignment_name varchar, assignment_source varchar, assignment_url varchar,
				course_id int, assignment_duration TIME, assignment_skills varchar);""")


def register_student(in_dict):

	cur,conn = curse()

	if type(in_dict) is not dict:
		raise TypeError



	keys = ["student_username", "student_pw",
			"student_first_name","student_last_name", "student_email", "student_phone", "student_courses"
			"student_school", "student_grade","student_dob"]
			
	in_keys = in_dict.keys()
	for key in keys:
		if key not in in_keys:
			in_dict[key] = None

	try:
		cur.execute("""INSERT INTO students (student_username, student_pw,
			student_first_name,student_last_name, student_email, student_phone,
			student_school, student_grade, student_courses, student_dob) VALUES (%(student_username)s, %(student_pw)s,
			%(student_first_name)s, %(student_last_name)s, %(student_email)s, %(student_phone)s,
			%(student_school)s, %(student_grade)s, %(student_courses)s, %(student_dob)s);""",in_dict)
		conn.close()
		return 200
	
	except psycopg2.errors.UniqueViolation:
		return "Account already exists with this email account or username"



def register_parent(in_dict):

	cur,conn = curse()

	if type(in_dict) is not dict:
		raise TypeError

	keys = ["parent_username","parent_pw","parent_first_name","parent_last_name",
			"parent_phone","parent_email", "payment_status", "plan_id", "paid", "end_total_cost", "student_username"]
	
	in_keys = in_dict.keys()
	for key in keys:
		if key not in in_keys:
			in_dict[key] = None

	try:
		cur.execute("""INSERT INTO parents (parent_username,parent_pw,parent_first_name,parent_last_name,
				parent_phone,parent_email, payment_status, plan_id, paid, end_total_cost, student_username)
				VALUES (%(parent_username)s,%(parent_pw)s,%(parent_first_name)s,%(parent_last_name)s,
				%(parent_phone)s,%(parent_email)s, %(payment_status)s, %(plan_id)s, %(paid)s, %(end_total_cost)s,
				%(student_username)s);""",in_dict)
		cur,conn = curse()
		return 200
	except psycopg2.errors.UniqueViolation:
		conn.close()
		return "Account already created with that username or email"

	except psycopg2.errors.ForeignKeyViolation as error:
		error_msg = str(error)
		if "student_username" in error_msg:
			return "No student was found with that username"
		elif "plan_id" in error_msg:
			return f"No plan was found with ID {in_dict['plan_id']}. Please contact robineducationalorg@gmail.com"

		return "Foreign Key Violation"

def create_assignment(in_dict):

	cur,conn = curse()

	if type(in_dict) is not dict:
		raise TypeError

	keys = ["assignment_name", "assignment_source", "assignment_url",
				"course_id", "assignment_duration" ,"assignment_skills","points"]
	in_keys = in_dict.keys()
	for key in keys:
		if key not in in_keys:
			in_dict[key] = None


	try:
		cur.execute("""INSERT INTO assignments (assignment_name, assignment_source, assignment_url,
				course_id, assignment_duration , assignment_skills) VALUES (%(assignment_name)s,
				%(assignment_source)s, %(assignment_url)s, %(course_id)s, %(assignment_duration)s , %(assignment_skills)s);""",in_dict)
		conn.close()
	except psycopg2.errors.ForeignKeyViolation as error:
		error_msg = str(error)
		if "course_id" in error:
			conn.close()
			return f"Course with id {in_dict['course_id']} has not been created"

def create_course(course_name,fw_id):
	cur,conn = curse()
	if type(fw_id) is not int:
		raise TypeError
	try:
		cur.execute("INSERT INTO courses (course_name, course_framework_id) VALUES (%s,%s);", (course_name,fw_id))
		conn.close()
	except psycopg2.errors.UniqueViolation:
		conn.close()
		return f"Course with name '{course_name}' already exists"


class Student:
		def __init__(self,row_list):
			self.row_dict = {}
			keys = ["student_username", "student_pw", "student_first_name","student_last_name", "student_email", "student_phone",
			"student_school", "student_grade", "student_courses","student_assignments","student_dob"]
			for key in keys:
				self.row_dict[key] = row_list[keys.index(key)]
			
			# change courses into list type 
			course_str = self.row_dict["student_courses"]
			courses = course_str.split(",")
			self.row_dict["student_courses"] = courses

			#change assignments into list
			str_assign = self.row_dict["student_assignments"]

			if str_assign is None:
				self.row_dict["student_assignments"] = None
			else:
				assign_dict = json.loads(str_assign)
				assign_list = [assign_dict[key] for key in assign_dict.keys()]
				self.row_dict["student_assignments"] = assign_list


		def print_row(self):
			for key in self.row_dict.keys():
				print(key+" ----------- "+str(self.row_dict[key]))



def student_info(student_username):

	cur,conn = curse()

	cur.execute("SELECT * FROM students WHERE student_username=%s;",(student_username,))

	all_rows = cur.fetchall()

	conn.close()

	if len(all_rows)==0 or len(all_rows[0])==0:
		return None

	return Student(all_rows[0])

def assign(assignment_name,student_username,due_date):

	cur,conn = curse()

	# first pull student's current info, take the dictionary
	student = student_info(student_username)
	assignments = student.row_dict["student_assignments"]

	cur.execute("""SELECT assignment_name, assignment_score FROM assignments WHERE assignment_name=%s;""",(assignment_name,))
	matches = cur.fetchall()
	
	# check if that assignment even exists
	if len(matches) == 0:
		return "Unable to find matching assignment"

	# add ass_name and score to the students dictionary
	ass_name = matches[0][0]
	ass_score = matches[0][1]

	if assignments is None:
		assignments[ass_name] = [{"complete":False,"assignment_name":ass_name,"potential_points":ass_score,"score":None,"due_date":due_date,"assigned_date":datetime.datetime.now()}]
	elif type(assignments) is dict:
		assignments[ass_name] = assignments[ass_name].append({"complete":False,"assignment_name":ass_name,"potential_points":ass_score,"grade":None,"due_date":due_date,"assigned_date":datetime.datetime.now()})

	new_str = json.dumps(assignments)

	cur.execute("UPDATE students SET student_assignments = %s WHERE student_username=%s;",(new_str,student_username))

	conn.close()


def mark_as_complete(student_username,assignment_name,grade):

	cur,conn = curse()

	# first pull student's current info, take the dictionary
	student = student_info(student_username)
	assignments = student.row_dict["student_assignments"]

	# check that assignment has been assigned to student
	if assignment_name not in assignments.keys():
		return f"assignment {assignment_name} has not been assigned to student {student_username}"

	# load info ab latest assignment with that name
	assignment_info = assignments[assignment_name][-1]

	assignment_info["complete"] = True
	assignment_info["grade"] = grade

	assignments[assignment_name][-1] = assignment_info

	new_str = json.dumps(assignments)

	cur.execute("UPDATE students SET student_assignments = %s WHERE student_username=%s;",(new_str,student_username))

	conn.close()


def opposite(char):
	letters = list(string.ascii_lowercase)
	if char in letters:
		return letters[25-letters.index(char)]
	else:
		return char


def encode(student_username):

	crap_list = [")","(","*","#","^","&","~"]

	old_list = list(student_username)
	new_list = []
	count=0
	for char in old_list:
		new_list.append(opposite(char))
		count+=1
		if count==3:
			new_list.append(random.choice(crap_list))
			count=0

	return "".join(new_list)

def decode(student_username):

	crap_list = [")","(","*","#","^","&","~"]
	for poop in crap_list:
		student_username = student_username.replace(poop,"")
	
	new_list = []
	for char in list(student_username):
		new_list.append(opposite(char))

	return "".join(new_list)


class User:
	def __init__(self,username,user_type):
		self.user_type = user_type
		self.user_id = username
		if user_type == "student":
			self.student_obj = student_info(username)
			if self.student_obj is None:
				self.is_authenticated = False
			else:
				self.is_authenticated = True
		elif user_type == "parent":
			raise KeyError
			self.parent_obj = student_info(username)
			if self.student_obj is None:
				self.is_authenticated = False
			else:
				self.is_authenticated = True
		self.is_active = True
		self.is_anonymous = False

	def get_id(self):
		return self.user_id
	def get(self):
		return self


def is_student(username):
	cur,conn = curse()
	cur.execute("SELECT * FROM students WHERE student_username=%s;",(username,))
	matches = cur.fetchall()
	conn.close()
	if matches is None or len(matches) == 0:
		return None
	else:
		return User(username,"student")




sample_in = {"student_username":"trial1", "student_pw":"trialpw1", "student_first_name":"Aman","student_last_name":"Khinvasara",
			 "student_email":"amankhinvasara@gmail.com", "student_phone":4085692914, "student_school":"Saint Francis",
			 "student_grade":12, "student_courses":"0001,0003"}

parent_sample_in = {"parent_username":"tractor","parent_pw":"dreams","parent_first_name":"Sona","parent_last_name":"Khinvasara",
				"parent_phone":4085692914,"parent_email":"tushsona@hotmail.com", "payment_status":"paid", "plan_id":3, "paid":0, "end_total_cost":1000,
				"student_username":"Squish"}

as_sample_in = {"assignment_name":"trial assignment","assignment_source":"Khan Academy","assignment_url":"robineducation.org",
				"course_id":0}




#cur, conn = curse()

#conn.close()