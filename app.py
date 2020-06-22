from flask import Flask, request, jsonify

import student_robin_sql

app = Flask(__name__)

@app.route("/",methods=["GET"])
def hello():
	return "<h1>Hello world</h1>"

if __name__=="__main__":
	app.run(debug=True,port=80,host="0.0.0.0",threaded=True)