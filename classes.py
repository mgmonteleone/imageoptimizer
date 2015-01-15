
__author__ = 'mgm'
class Fileinfo(object):
    filename = None
    mimetype = "image/png"
    filesizeoriginal = None
    filesizeoptimized = None
    width = None
    height = None
    fetchuri = None
    processtime = 0


    def __init__(self, filename, mimetype,  filesizeoriginal, width, height, filesizeoptimized, fetchuri,processtime):
        self.filesizeoriginal = filesizeoriginal
        self.filesizeoptimized = filesizeoptimized
        self.mimetype = mimetype
        self.filename = filename
        self.height = height
        self.width = width
        self.fetchuri = fetchuri
        self.processtime = processtime

class InvalidUsage(Exception):
    status_code = 401

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv