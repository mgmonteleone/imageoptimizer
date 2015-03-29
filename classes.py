__author__ = 'mgm'
import os
from cStringIO import StringIO
from PIL import Image
from time import time
import dns.resolver
class Fileinfo(object):
    filename = None
    mimetype = "image/png"
    filesizeoriginal = None
    filesizeoptimized = None
    width = None
    height = None
    reference = None
    processtime = 0
    percentsaved = None
    dbreference = None


    def __init__(self, filename, mimetype, filesizeoriginal, width, height, filesizeoptimized, reference, processtime,
                 percentsaved, dbreference):
        self.filesizeoriginal = filesizeoriginal
        self.filesizeoptimized = filesizeoptimized
        self.mimetype = mimetype
        self.filename = filename
        self.height = height
        self.width = width
        self.reference = reference
        self.processtime = processtime
        self.percentsaved = percentsaved
        self.dbreference = dbreference

class ImageFile():
    mimetype = str()
    filename = str()
    extension = str()
    original = None
    originalimage = StringIO()
    height = int()
    width = int()
    size = int()
    optimized = StringIO()
    imagetime = int()
    optimizedsize = int()
    savedpercent = float()

    def __init__(self, file):
        """
        Upon initialization take the passed file object, and extract data, create an optimized file.
        :type self: object
        """
        start_time = time.time()
        # Get the original file information
        self.mimetype = file.mimetype
        self.filename = file.filename
        self.extension = self.filename.rsplit('.', 1)[1]
        # Create a StringIO object for working with the original file
        self.originalimage = Image.open(StringIO(file.read()))
        # Now that this is an image, lets get the image info
        self.height = self.originalimage.size[1]
        self.width = self.originalimage.size[0]
        self.size = len(self.original)
        # Create a blank StringIO object for the optimized image.
        self.optimized = StringIO()
        if self.extension == "jpg":
            self.extension = "jpeg"  # bug workaround
        self.optimized.seek(0)
        # Save the original image to the optimized buffer, applying optimization.
        self.originalimage.save(self.optimized, self.extension, optimize=True)
        self.imagetime = time.time() - start_time
        # Get information about the optimized file
        self.optimized.seek(0,os.SEEK_END)
        self.optimizedsize = self.optimized.tell()
        self.savedpercent = round(((1.0 - (float(float(self.optimizedsize)/float(self.size))))*100), 1)


class SrvRecord(object):
    service = None
    target = None
    port = None

    def __init__(self, service):
        try:
        #  servicename = service + os.environ.get("consulsuffix")
            servicename = service + ".service.dc1.consul"
        except:
            print "----------A environment variable [consulsuffix] is required to bootstrap-----------"
            raise
        r = dns.resolver.Resolver()
        r.timeout = 2
        r.lifetime = 2
        srv = r.query(servicename, 'SRV')[0]
        self.target = srv.target
        self.port = srv.port
        self.service = service

    def avail(self):
        """
        The number of the server resources available

        :return:int: Count of service instances available
        """
        import dns.resolver
        try:
            servicename = self.service + os.environ.get("consulsuffix")
        except:
            print "----------A environment variable [consulsuffix] is required to bootstrap-----------"
            raise
        r = dns.resolver.Resolver()
        r.timeout = 2
        r.lifetime = 2
        count = len(r.query(servicename, 'SRV'))
        return count

    def __str__(self):
        return "Service: " + str(self.service) + " target: " + str(self.target) + " port: " + str(self.port)