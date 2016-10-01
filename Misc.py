import string
import random
import itertools
import re

# Adapted from http://stackoverflow.com/a/2257449/6214388
def randomString(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# Originally seen on http://anothergisblog.blogspot.com/2016/08/more-on-pandas-data-loading-with-arcgis.html
# Appears to have originated from http://stackoverflow.com/a/8998040/6214388
# This implementation's efficiency is shown by benchmarks at http://pastebin.com/YkKFvm8b
def chunkIterable(iterable, chunkSize):
    """
    creates chunks of cursor row objects to make the memory
    footprint more manageable
    """
    it = iter(iterable)
    while True:
        chunk_it = itertools.islice(it, chunkSize)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield itertools.chain((first_el,), chunk_it) 

# Adapted from http://stackoverflow.com/a/1277047
def cleanseString(inputString):
    pattern = re.compile('[\W_]+')
    return pattern.sub('', inputString)
    

if __name__ == "__main__":
    print randomString()
