# imageoptimizer
## What happens when we get frustrated with Kraken.io

Using an already polised and proven service is always best, but what happens when you have production requirements which do not allow for uncontrolled downtimes and slowness...

When then you have to go it alone, and make your own service.

This RESTfull service receives POSTS of image files, lossly optimizes them, and then makes them available.

## Features
* Lossless optimization of JPEG, PNG, GIF
* Depending on the enpoint, either returns a url to return the image from, or a mongoid for using the image directly from the configured database, or for retrieving.
* upon getting by id, nicely redirects, so you get a filename, instead of an ugly id...
* Pretty darn fast.

## Endpoints
* POST
    * /file - stores the optimized file to filesystem, and returns you the URL to retrieve it from.
    *  /db - stores the file in Mongodb, and returns a mongoid, either to integrate and directly get the file from mongo, or to retrieve by id.
* GET
   *  /files/[name of file] - retrieves the optimized image by filename (same as original passed filename)
   *  /files/[mongoid] - retrieves file by mongoid (returned from the post). This endpoint actually redirects to /files/[mongoid][filename] to allow the retrieval with pretty filename.
