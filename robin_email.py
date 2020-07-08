
import yagmail

def registered_student(student_email,student_first_name):
	
	subject = "Welcome to Robin Education!"

	body = f"""\nHi {student_first_name},\n
	Welcome to Robin Education! We are so excited to take flight with you! We believe that success lies in front of every student; our job is to guide you on the right path, quickly. School isn't easy, and this year is definitely not going to be any better.\n
	But you are going to excel.	We're so excited to begin working with you and helping you learn <i>how to learn</i> faster and smarter.\n
	We will review your course preferences and be in touch with a plan for each course. In the meantime, please ensure you are able to login to our <a href="http://student.robineducation.org/login" target="_blank">portal</a>. Also then ensure that your parents have registered a parent account with us at <link>. Feel free to reply to this email with any questions! Thank you for trusting us with empowering your academic success!

	Sincerely,

	Aman Khinvasara
	<span style="color: blueviolet;">Founder, CEO | Robin Education</span>
	408.205.8379"""

	with yagmail.SMTP("robin@robineducation.org","qptybbcjgdwbcxja") as yag:
		yag.send(student_email,subject,body)
