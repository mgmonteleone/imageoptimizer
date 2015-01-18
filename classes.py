
__author__ = 'mgm'
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


    def __init__(self, filename, mimetype,  filesizeoriginal, width, height, filesizeoptimized, reference,processtime, percentsaved,dbreference):
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

