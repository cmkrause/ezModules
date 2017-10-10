import string
import random
import itertools
import re

def pctDifference(x1, x2):
    return abs(x1 - x2) / ((x1 + x2) / 2)

def minElementDifference(data):
    ## For a list like [12, 5, 14], returns 2
    ## (the smallest difference between all pairs of values in the list)
    data = sorted(data, reverse = True)
    return min([value - data[index] for index, value in enumerate(data[:-1], 1)])

def maxElementDifference(data):
    ## for a list like [5, 12, 17], returns 12
    ## (the difference between the maximum and minimum values of the list)
    return max(data) - min(data)

# From https://stackoverflow.com/a/28289906
def frange(start, stop, step):
    x = start
    while x < stop:
        yield x
        x += step

# Adapted from http://stackoverflow.com/a/2257449/6214388
def randomString(size=32, chars=string.ascii_uppercase + string.ascii_lowercase):
    return ''.join(random.choice(chars) for i in xrange(size))

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

# Adapted from http://stackoverflow.com/a/2130035
def chunkList(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

# Adapted from http://stackoverflow.com/a/1277047
def cleanseString(inputString):
    pattern = re.compile('[\W_]+')
    return pattern.sub('', inputString)
    

if __name__ == "__main__":
    print randomString()

    print chunkList(range(1000), 3)
