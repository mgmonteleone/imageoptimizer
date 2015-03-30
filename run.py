__author__ = 'matthewgmonteleone'
from flask import Flask, request, make_response, redirect, send_file, abort, after_this_request

import werkzeug
import json
import os
import time
import yaml
import platform
import logging, logging.handlers
from datetime import datetime
from savetomongo import save
from classes import Fileinfo, ImageFile
from savetomongo import retrieve
import sys

# configfile = open("config.yaml", "r")
#config = yaml.load(configfile)
#apikeys = config["apikeys"]
#configmongo = config["mongo"]

syslogger = logging.getLogger('syslogger')
syslogger.setLevel(logging.INFO)

if platform.system() == "Linux":
    try:
        handler = logging.handlers.SysLogHandler(address='/dev/log')
        syslogger.addHandler(handler)
    except:
        print("Can not log to syslog, even though I am on line, maybe in a container???")

consolelog = logging.StreamHandler(sys.stdout)
syslogger.addHandler(consolelog)
UPLOAD_FOLDER = "/files/"
ALLOWED_EXTENSIONS = set(['jpeg', 'png', 'jpg', 'gif'])
app = Flask(__name__)


#Prepare The Upload Folder
syslogger.info(datetime.now().__str__() + " ......Optimizer process Started......")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/<storagemethod>/", methods=['POST'], strict_slashes=False)
def upload(storagemethod):
    """
    Takes the uploaded file (which much be sent in the 'file' field) and optimizes and stores it.
    If db is selected, the file is stored in mongodb.
    if file is selected the file is stored locally on disk.
    If store is selected, the file is stored to mongodb without optimization.
    We return a json with file information.

    :param storagemethod: db | file | store
    :return: :raise:
    """
    if storagemethod not in ['db', 'file', 'store']:
        return make_response("You need to post an image file in the 'file' field.", 400)
        abort
    sentfile = request.files.get("file")
    if file and allowed_file(sentfile.filename):
        # Intantiate and instance of an Imagefile with the sent file
        imagefile = ImageFile(sentfile)
        fileinfo = Fileinfo(
            filename=imagefile.filename, mimetype=imagefile.mimetype, filesizeoriginal=imagefile.size
            , width=imagefile.width, height=imagefile.height, filesizeoptimized=imagefile.optimizedsize
            , reference=request.url_root + UPLOAD_FOLDER + imagefile.filename
            , processtime=imagefile.imagetime, percentsaved=imagefile.savedpercent, dbreference=None)

        if storagemethod == 'file':
            # Save the optimized file to disk
            savefile = open(UPLOAD_FOLDER + filename, 'wb')
            optimized.seek(0)  # Very important, before writing to file, need to move buffer to beginning.
            savefile.write(imagefile.optimized.read())
            savefile.close()
        elif storagemethod in ('db', 'store'):
            # Save to mongo
            try:
                imagefile.optimized.seek(0)
                imagefile.original.seek(0)
                if storagemethod == 'store':  # If we just want to store the file, then we save the original
                    returned = save.saveimagetomongo(fileinfo, imagefile.original)
                else:  # if the method is db, then we store the optimized file.
                    returned = save.saveimagetomongo(fileinfo, imagefile.optimized)
                fileinfo.dbreference = str(returned.id)
                fileinfo.reference = None
            except:
                syslogger.error(datetime.now().__str__() + " ERROR: Could Not Save to Mongo")
                raise
        syslogger.info(json.dumps(fileinfo.__dict__))
        return make_response(json.dumps(fileinfo.__dict__), 200)
    else:
        return make_response("You need to post an image file and post with the file field.", 400)


@app.route("/files/<filename>", methods=['GET'])
def retrievebyname(filename):
    """
    Tries to find the file by file name on disk.
    If not found it tries to lookup the filename in mongodb.
    Redirects to /id/filename.ext to return the file nicely.
    :param filename:
    :return:
    """
    syslogger.info(datetime.now().__str__() + " Entered Retrieve")
    syslogger.info(datetime.now().__str__() + " Looking for file: " + UPLOAD_FOLDER + filename)
    try:
        thefile = open(UPLOAD_FOLDER + filename, 'rb')
        return send_file(thefile)
    except:
        syslogger.warn(datetime.now().__str__() + " Trying to find the file in the database....")
        retrieved = retrieve.getbyname(filename)
        syslogger.info(datetime.now().__str__() + " We found " + str(retrieved.id) + " in the db.")
        theid = str(retrieved.id)
        return redirect("/files/id/" + theid + "/" + filename)


@app.route("/files/id/<fileid>", methods=['GET'])
def getbyid(fileid):
    """
    Looks up the file by id, finds the filename from the database, then redirects to return the filename.
    :param fileid: the mongoid of the file to be retrieved
    :return: fileobject
    """
    syslogger.info(datetime.now().__str__() + "Entered DB Retrieve")
    syslogger.info(datetime.now().__str__() + "Looking for id: " + fileid)
    try:
        thefile = retrieve.retrievebyid(fileid)
        thefilename = thefile.filename

        syslogger.info(datetime.now().__str__() + " Got The File, lets return it....")
        return redirect("/files/id/" + fileid + '/' + thefilename, 307)

    except:
        return make_response("Image Not Found", 404)


@app.route("/files/id/<fileid>/<thefilename>", methods=['GET'])
def getbyidname(fileid, thefilename):
    """
    Returns a binary of the image file based on the sent, and the filename (we redirect to here to get nice returns.
    :rtype : response
    """
    try:
        syslogger.info(datetime.now().__str__() + " Thefilename is: " + thefilename)
        syslogger.info(datetime.now().__str__() + " The fileid is: " + fileid)
        thefile = retrieve.retrievebyid(fileid)
        syslogger.info(datetime.now().__str__() + " The mimetype is: " + thefile.contentype)
        @after_this_request
        def add_header(response):
            response.headers['X-height'] = thefile.height
            response.headers["X-width"] = thefile.width
            response.headers["X-processtime"] = thefile.processtime
            response.headers["X-percentsaved"] = thefile.percentsaved
            response.headers["X-filesizeoriginal"] = thefile.filesizeoriginal
            response.headers["X-filesizeoptimized"] = thefile.filesizeoptimized
            return response

        return send_file(thefile.binaryfile.get(), mimetype=thefile.contentype, add_etags=True)

    except:
        return make_response("There was a problem returning this file. Please try again", 500)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
