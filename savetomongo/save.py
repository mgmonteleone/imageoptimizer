__author__ = 'mgm'
import yaml
from mongoengine import *
from classes import Fileinfo, SrvRecord
import datetime
import os ,os.path
import consul
import json
#Get Our Configuration From consul
#First get the name of the server from srv record
srvrecordconsul = SrvRecord("consul")
srvrecordmongo = SrvRecord("mongos")
configmongo = {
    "host" : srvrecordmongo.target.to_text(),
    "port" : srvrecordmongo.port,
}
#then get the name of the database from kv store.
print(srvrecordconsul.target)
kvstore = consul.Consul(host=srvrecordconsul.target, port=srvrecordconsul.port)
try:
    key = kvstore.kv.get("apps/imageoptimizer/dbname")
    configmongo["database"] = key[1]["Value"]
except ConnectionError:
    print "--------Could not connect to consul at" + str(srvrecordconsul.target) + " port: "+ str(srvrecordconsul.port)
    raise
print configmongo
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
