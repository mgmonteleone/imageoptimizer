__author__ = 'matthewgmonteleone'
from flask import Flask, request, make_response, redirect, send_file, abort
from werkzeug import secure_filename
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

import werkzeug
import json
import os
import time
import yaml
import platform
import logging,logging.handlers
from datetime import datetime
from savetomongo import save
from classes import Fileinfo, ImageFile
from savetomongo import retrieve
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
        print("Can not log to syslog, even though I am on line, maybe in a container???")

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
    if storagemethod not in ['db','file','store']:
        return make_response("You need to post an image file in the 'file' field.", 400)
        abort
    sentfile = request.files.get("file")
    if file and allowed_file(sentfile.filename):
        imagefile = ImageFile(sentfile)
        #Do not optimize if storage method is store....
        fileinfo = Fileinfo(
            filename=imagefile.filename, mimetype=imagefile.mimetype, filesizeoriginal=imagefile.size
            ,width=imagefile.width, height=imagefile.height, filesizeoptimized=imagefile.optimizedsize
            ,reference=request.url_root+UPLOAD_FOLDER+imagefile.filename
            ,processtime=imagefile.imagetime,percentsaved=imagefile.savedpercent,dbreference=None)

        if storagemethod == 'file':
            # Save the optimized file to disk
            savefile = open(UPLOAD_FOLDER+filename,'wb')
            optimized.seek(0)  # Very important, before writing to file, need to move buffer to beginning.
            savefile.write(imagefile.optimized.read())
            savefile.close()
        elif storagemethod in ('db','store'):
            # Save to mongo
            try:
                print filename
                imagefile.optimized.seek(0)
                if storagemethod == 'store':
                    returned = save.saveimagetomongo(fileinfo,imagefile.originalimage)
                else:
                    returned = save.saveimagetomongo(fileinfo,imagefile.optimized)
                fileinfo.dbreference = str(returned.id)
                fileinfo.reference = None
            except:
                syslogger.error(datetime.now().__str__()+" ERROR: Could Not Save to Mongo")
                statsd.statsd.event("Image Optimizer Error","Could not save to mongo","error",None,None,None,"normal")
                raise
        exectime = time.time() - start_time
        syslogger.info(datetime.now().__str__()+ " Excecuted in " + str(round(exectime,4)) + " secs.")
        syslogger.info(json.dumps(fileinfo.__dict__))
        try:
            statsd.statsd.histogram("optimizer.bytes_processed",fileinfo.filesizeoriginal)
            statsd.statsd.histogram("optimizer.processing_time",fileinfo.processtime)
            statsd.statsd.event(title="Optimizer Run",text="Processed an image and saved "+str(fileinfo.percentsaved)+"%!!",alert_type="info",priority="low")
        except:
            syslogger.warn(datetime.now().__str__()+" Could not send stat to datadog.")
        return make_response(json.dumps(fileinfo.__dict__),200)
    else:
        return make_response("You need to post an image file and post with the file field.",400)


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
        statsd.statsd.event("Image Optimizer Error","Could not return file","warning",None,None,None,"normal")
        return make_response("There was a problem returning this file. Please try again",500)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
