__author__ = 'mgm'
import yaml
from mongoengine import *
from classes import Fileinfo, SrvRecord
import datetime
import os ,os.path
import srvlookup
if os.path.isfile("config.yaml"):
    configfile = open("config.yaml", "r")
    config = yaml.load(configfile)
    configmongo = config["mongo"]
elif os.environ(["ansibleconfig"]) == True:
    try:
        srvrecord = SrvRecord("mongos")
        configmongo = {
            "database" : "imageoptimizer",
            "host" : "localhost",
            "port" : "port"
        }
    except:
        print "Could not find my server"
connect(configmongo["database"], host=configmongo["host"], port=configmongo["port"])


class ImageFile(Document):
    binaryfile = FileField()
    type = StringField()
    contentype = StringField()
    uploaddate = DateTimeField(default=datetime.datetime.now())
    percentsaved = FloatField()
    filename = StringField()
    filesizeoriginal = IntField()
    filesizeoptimized = IntField()
    width = IntField()
    height = IntField()
    reference = StringField(default=None)
    processtime = FloatField()


def saveimagetomongo(Fileinfo, thefile):
    """

    :param Fileinfo: A fileInfo object containing all various image information
    :param thefile: a binary object of the actual file to be stored.
    :return: saved.id : The id of the saved file.
    """
    imagefile = ImageFile()
    imagefile.binaryfile.put(thefile.read())
    imagefile.contentype = Fileinfo.mimetype
    imagefile.filename = Fileinfo.filename
    imagefile.filesizeoptimized = Fileinfo.filesizeoptimized
    imagefile.filesizeoriginal = Fileinfo.filesizeoriginal
    imagefile.height = Fileinfo.height
    imagefile.width = Fileinfo.width
    imagefile.processtime = Fileinfo.processtime
    imagefile.percentsaved = Fileinfo.percentsaved
    saved = imagefile.save()
    return saved
