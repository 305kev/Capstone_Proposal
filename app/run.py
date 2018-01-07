from flask import Flask, url_for, render_template, request, jsonify
app = Flask(__name__)

@app.route('/')
def root():
	return render_template("index.html")

@app.route("/get_results", methods=["POST"])
def get_results():
	print request.form
	return "ok"