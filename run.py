__author__ = 'matthewgmonteleone'
from flask import Flask, request, make_response, redirect, send_file, abort, Response, jsonify, url_for
from werkzeug import secure_filename
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

from PIL import Image
import werkzeug
import json
import os, io
import StringIO
import time
import yaml
import urllib
import platform
import logging, logging.handlers
from datetime import datetime
from savetomongo import save
from classes import Fileinfo
from savetomongo import retrieve
from mongoengine import *
import statsd
import sys

configfile = open("config.yaml", "r")
config = yaml.load(configfile)
apikeys = config["apikeys"]
configmongo = config["mongo"]

syslogger = logging.getLogger('syslogger')
syslogger.setLevel(logging.INFO)

if platform.system() == "Linux":
    try:
        handler = logging.handlers.SysLogHandler(address = '/dev/log')
        syslogger.addHandler(handler)
    except:
        print("Can not log to syslog, eventhough I am on line, maybe in a container???")

consolelog = logging.StreamHandler(sys.stdout)
syslogger.addHandler(consolelog)
UPLOAD_FOLDER =  "files/"
ALLOWED_EXTENSIONS = set(['jpeg', 'png', 'jpg', 'gif'])
app = Flask(__name__)
#try to connect to datadog...
try:
    statsd.statsd.connect(host=os.environ.get("mydockerhost"),port="8125")
except:
    syslogger.warn(datetime.now().__str__()+" Could not connect to statsd.")


#Prepare The Upload Folder
syslogger.info(datetime.now().__str__()+ " ......Optimizer process Started......")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/<storagemethod>/", methods=['POST'],strict_slashes=False)
def upload(storagemethod):
    if storagemethod not in ['db','file']:
        return make_response("You need to post an image file and post with the file field.",400)
        abort
    start_time = time.time()
    file = request.files.get("file")
    if file and allowed_file(file.filename):
        mimetype = file.mimetype
        filename = file.filename
        extension = filename.rsplit('.', 1)[1]
        original = file.read()
        originalimage = Image.open(StringIO.StringIO(original))
    # get metadata
        height = originalimage.size[1]
        width = originalimage.size[0]
        size = len(original)
        optimized = StringIO.StringIO()
    # Optimize and add optimized info
        if extension == "jpg":
            extension = "jpeg"  #bug workaround
        optimized.seek(0)
        #Save the original image to as buffer, with optimization.
        originalimage.save(optimized, extension, optimize=True)
    # Create File Info
        imagetime = time.time() - start_time
        optimized.seek(0,os.SEEK_END)
        optimizedsize = optimized.tell()
        savedpercent = round(((1.0 - (float(float(optimizedsize)/float(size))))*100),1)
        fileinfo = Fileinfo(
            filename=filename, mimetype=mimetype, filesizeoriginal=size
            ,width=width, height=height, filesizeoptimized=optimizedsize
            ,reference= request.url_root+UPLOAD_FOLDER+filename
            ,processtime=imagetime,percentsaved= savedpercent,dbreference=None )

        if storagemethod == 'file':
            # Save the optimized file to disk
            savefile = open(UPLOAD_FOLDER+filename,'wb')
            optimized.seek(0) # Very important, before writing to file, need to move buffer to beginning.
            savefile.write(optimized.read())
            savefile.close()
        elif storagemethod == 'db':
            # Save to mongo
            try:
                print filename
                optimized.seek(0)
                returned = save.saveimagetomongo(fileinfo,optimized)
                fileinfo.dbreference = str(returned.id)
                fileinfo.reference = None
            except:
                syslogger.error(datetime.now().__str__()+" ERROR: Could Not Save to Mongo")
                raise
        exectime = time.time() - start_time
        syslogger.info(datetime.now().__str__()+ " Excecuted in " + str(round(exectime,4)) + " secs.")
        syslogger.info(json.dumps(fileinfo.__dict__))
        try:
            statsd.statsd.histogram("optimizer.bytes_processed",fileinfo.filesizeoriginal)
        except:
            syslogger.warn(datetime.now().__str__()+" Could not send stat to datadog.")
        return make_response(json.dumps(fileinfo.__dict__),200)
    else:
        return make_response("You need to post an image file and post with the file field.",400)
    #return make_response(json.dumps(fileinfo.__dict__),200)
@app.route("/files/<filename>", methods=['GET'])
def retrievebyname(filename):
    syslogger.info(datetime.now().__str__()+" Entered Retrieve")
    syslogger.info(datetime.now().__str__()+" Looking for file: "+ UPLOAD_FOLDER+filename)
    try:
        thefile = open(UPLOAD_FOLDER+filename,'rb')
        return send_file(thefile)
    except:
        syslogger.warn(datetime.now().__str__()+" Trying to find the file in the database....")

        retrieved = retrieve.getbyname(filename)
        syslogger.info(datetime.now().__str__()+ " We found "+str(retrieved.id)+ " in the db.")
        theid = str(retrieved.id)
        return redirect("/files/id/"+theid+"/"+filename)
@app.route("/files/id/<fileid>", methods=['GET'])
def getbyid(fileid):
    syslogger.info(datetime.now().__str__()+"Entered DB Retrieve")
    syslogger.info(datetime.now().__str__()+"Looking for id: "+ fileid)
    try:
        thefile = retrieve.retrievebyid(fileid)
        thefilename = thefile.filename

        syslogger.info(datetime.now().__str__() + " Got The File, lets return it....")
        return redirect("/files/id/"+fileid+'/'+thefilename,307)
        #return send_file(thefile.binaryfile.get(),mimetype="image/jpeg")
    except:
        return make_response("Image Not Found",404)
@app.route("/files/id/<fileid>/<thefilename>", methods=['GET'])
def getbyidname(fileid,thefilename):
    try:
        syslogger.info(datetime.now().__str__()+" Thefilename is: "+thefilename)
        syslogger.info(datetime.now().__str__()+" The fileid is: "+fileid)
        thefile = retrieve.retrievebyid(fileid)
        syslogger.info(datetime.now().__str__()+" The mimetype is: "+thefile.contentype)
        return send_file(thefile.binaryfile.get(),mimetype=thefile.contentype)

    except:
        return make_response("There was a problem returning this file. Please try again",500)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
