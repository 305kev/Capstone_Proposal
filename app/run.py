# RM NOTE: to run, run the following command from the ./app directory
# export FLASK_APP=run.py && python -m flask run

from flask import Flask, url_for, render_template, request, jsonify
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

#NOTES FOR KEVIN
# here, try loading your pickled model into a variable, then when you run the flask application, it should be available in the function below

@app.route('/')
def root():
	return render_template("index.html")

@app.route("/get_results", methods=["POST"])
def get_results():
	#NOTES FOR KEVIN
	# here, do something to prove that the model has been loaded in memory when you started the application, and persists in memory, get results will be called everytime that you hit search on the front-end, i recommend printing out something here that proves that your pickled data is loaded, and does not have to be loaded again; once we know this, we'll be safe to assume that we won't have to wait the extra 2 - 3 minutes when we demo

	print (request.form)
	return "ok"
