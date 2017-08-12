import urllib2, os, socket

## Tests whether or not your computer is connected to the internet
## Adapted from https://stackoverflow.com/a/33117579
def hasInternet(host = "8.8.8.8", port = 53, timeout = 3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        return False

## Simple wrapper function to facilitate downloading a file from a website
## to a local path
## Loosely based upon: https://www.blog.pythonlibrary.org/2012/06/07/python-101-how-to-download-a-file/
## Arguably, the Python module requests is better than urllib2,
## but for the sake of having fewer dependencies, whenever possible,
## built-in modules will be used
def downloadFile(url, outputPath,
                 fileName = None):

    if fileName != None:
        pathAndFileName = os.path.join(outputPath, fileName)
    else:
        pathAndFileName = os.path.join(outputPath, os.path.basename(url))

    with open(pathAndFileName, "wb") as outputFile:
        outputFile.write(urllib2.urlopen(url).read())

    return pathAndFileName
