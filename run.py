__author__ = 'matthewgmonteleone'
from flask import Flask, request, make_response
import werkzeug

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/", methods=['POST'])
def upload():
    original = request.files.get('file')
    #mimetype = file.content_type
    filename = werkzeug.secure_filename(file.name)
    return make_response(filename,200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)