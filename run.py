__author__ = 'matthewgmonteleone'
from flask import Flask, request, make_response, redirect, send_file, abort, Response, jsonify
from werkzeug import secure_filename
from PIL import Image
import werkzeug
import json
import os
import StringIO
import time
import yaml
import urllib

configfile = open("config.yaml", "r")
config = yaml.load(configfile)
apikeys = config["apikeys"]

UPLOAD_FOLDER = config["uploadfolder"]
ALLOWED_EXTENSIONS = set(['jpeg', 'png', 'jpg', 'gif'])
app = Flask(__name__)
from classes import Fileinfo, InvalidUsage


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/", methods=['POST'])
def upload():
    start_time = time.time()
    if request.headers.get('apikey') and request.headers.get('secret'):
        apikey = request.headers.get('apikey')
        secret = request.headers.get('secret')
        print apikeys
        if apikey in apikeys and secret in apikeys.values():
            print "ok"
        else:
            return make_response(json.dumps("dsadsad"),401)
    # thekeys = {k:v for (k,v) in apikeys.iteritems() if "apikey" in k}
    #if apikey in thekeys
    # print filtered_dict


    file = request.files.get("file")
    if file and allowed_file(file.filename):
        mimetype = file.mimetype
        filename = werkzeug.secure_filename(file.filename)
        extension = filename.rsplit('.', 1)[1]
        original = file.read()
        originalimage = Image.open(StringIO.StringIO(original))
    # get metadate
        height = originalimage.size[1]
        width = originalimage.size[0]
        size = len(original)
        optimized = StringIO.StringIO()
    #Optimize and add optimized info
        if extension == "jpg":
            extension = "jpeg"  #bug workaround
        originalimage.save(UPLOAD_FOLDER+filename, extension, optimize=True)
        optimizedsize = os.path.getsize(UPLOAD_FOLDER+filename)

    # Create File Info
        imagetime = time.time() - start_time
        fileinfo = Fileinfo(filename, mimetype, size, width, height, optimizedsize, request.url_root+filename,imagetime )
        headers = {"x.monkey": "attachment"}
        optimized.seek(0)

        returnit = send_file(optimized, mimetype=mimetype, as_attachment=True, attachment_filename=filename
                         , add_etags=True)
        returnit.headers.add('data', json.dumps(fileinfo.__dict__))
        exectime = time.time() - start_time
        print "excecuted in" + str(exectime) + " secs."
        return make_response(json.dumps(fileinfo.__dict__),200)
    else:
        return "no file"
    #return make_response(json.dumps(fileinfo.__dict__),200)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)