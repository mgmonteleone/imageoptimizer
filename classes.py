__author__ = 'mgm'
import os

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


class SrvRecord(object):
    service = None
    target = None
    port = None

    def __init__(self, service):
        import dns.resolver
        try:
            servicename = service + os.environ.get("consulsuffix")
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