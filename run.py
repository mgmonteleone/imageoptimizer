__author__ = 'matthewgmonteleone'
from PIL import Image
import os
from flask import Flask, request, redirect, url_for, make_response
from werkzeug import secure_filename

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/", methods=['POST'])
def upload():
    original = request.files.get('file')
    return make_response("hello",200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)