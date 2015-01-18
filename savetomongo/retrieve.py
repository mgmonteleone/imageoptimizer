__author__ = 'mgm'
import yaml
from mongoengine import *
from classes import Fileinfo
from flask import make_response
import datetime

try:
    configfile = open("config.yaml", "r")
    config = yaml.load(configfile)
    configmongo = config["mongo"]
except:
    print "help"
connect(configmongo["database"], host=configmongo["host"], port=configmongo["port"])
__author__ = 'mgm'

from save import ImageFile

def retrievebyid(id):
    try:
        imagefile = ImageFile.objects(id=id).first()
        return imagefile
    except:
        return make_response("That file was not found",404)
def getbyname(thefilename):
    try:
        print(datetime.datetime.now().__str__()+' Looking for '+thefilename+' in the database')
        imagefile = ImageFile.objects(filename=thefilename).first()
        print imagefile.filename
        return imagefile
    except:
        raise IOError("The file does not exist")