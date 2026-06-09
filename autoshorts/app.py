from flask import Flask,render_template,request
from pipeline.renderer import render_short
import os


app = Flask(__name__)


@app.route("/")
def home():
    return render_template(
        "index.html"
    )


@app.route("/upload",methods=["POST"])
def upload():

    file=request.files["video"]


    path="uploads/"+file.filename

    file.save(path)


    render_short(
        path,
        10,
        40,
        "shorts_output/output.mp4"
    )


    return "Short created successfully"


app.run(debug=True)