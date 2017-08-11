# from jenks import *

## -------------------------------------------------------------------------------------

# The first three functions of this script are originally from
# https://gist.github.com/drewda/1299198

# The first two functions of this script are from the code originally at
# http://danieljlewis.org/files/2010/06/Jenks.pdf
# This code was originally described at
# http://danieljlewis.org/2010/06/07/jenks-natural-breaks-algorithm-in-python/
# Neither of these websites is functional, but archived copies are available at
# https://web.archive.org/web/20100711083657/http://danieljlewis.org/2010/06/07/jenks-natural-breaks-algorithm-in-python/
# https://web.archive.org/web/20110124052102/http://danieljlewis.org/files/2010/06/Jenks.pdf

# Arguably, the code of the following question is "better" (at least more literate)
# https://gist.github.com/llimllib/4974446
# It can be thought of as better, because it is based off a modern recent implementation
# of the algorithm rather than ancient FORTRAN.  For more information, look at
# http://www.macwright.org/2013/02/18/literate-jenks.html

def getJenksBreaks( dataList, numClass ):
  dataList.sort()
  mat1 = []
  for i in range(0,len(dataList)+1):
    temp = []
    for j in range(0,numClass+1):
      temp.append(0)
    mat1.append(temp)
  mat2 = []
  for i in range(0,len(dataList)+1):
    temp = []
    for j in range(0,numClass+1):
      temp.append(0)
    mat2.append(temp)
  for i in range(1,numClass+1):
    mat1[1][i] = 1
    mat2[1][i] = 0
    for j in range(2,len(dataList)+1):
      mat2[j][i] = float('inf')
  v = 0.0
  for l in range(2,len(dataList)+1):
    s1 = 0.0
    s2 = 0.0
    w = 0.0
    for m in range(1,l+1):
      i3 = l - m + 1
      val = float(dataList[i3-1])
      s2 += val * val
      s1 += val
      w += 1
      v = s2 - (s1 * s1) / w
      i4 = i3 - 1
      if i4 != 0:
        for j in range(2,numClass+1):
          if mat2[l][j] >= (v + mat2[i4][j - 1]):
            mat1[l][j] = i3
            mat2[l][j] = v + mat2[i4][j - 1]
    mat1[l][1] = 1
    mat2[l][1] = v
  k = len(dataList)
  kclass = []
  for i in range(0,numClass+1):
    kclass.append(0)
  kclass[numClass] = float(dataList[len(dataList) - 1])
  countNum = numClass
  while countNum >= 2:#print "rank = " + str(mat1[k][countNum])
    id = int((mat1[k][countNum]) - 2)
    #print "val = " + str(dataList[id])
    kclass[countNum - 1] = dataList[id]
    k = int((mat1[k][countNum] - 1))
    countNum -= 1
  return kclass
  
def getGVF( dataList, numClass ):
  """
  The Goodness of Variance Fit (GVF) is found by taking the 
  difference between the squared deviations
  from the array mean (SDAM) and the squared deviations from the 
  class means (SDCM), and dividing by the SDAM
  """
  breaks = getJenksBreaks(dataList, numClass)
  dataList.sort()
  listMean = sum(dataList)/len(dataList)
  print listMean
  SDAM = 0.0
  for i in range(0,len(dataList)):
    sqDev = (dataList[i] - listMean)**2
    SDAM += sqDev
  SDCM = 0.0
  for i in range(0,numClass):
    if breaks[i] == 0:
      classStart = 0
    else:
      classStart = dataList.index(breaks[i])
      classStart += 1
    classEnd = dataList.index(breaks[i+1])
    classList = dataList[classStart:classEnd+1]
    classMean = sum(classList)/len(classList)
    print classMean
    preSDCM = 0.0
    for j in range(0,len(classList)):
      sqDev2 = (classList[j] - classMean)**2
      preSDCM += sqDev2
    SDCM += preSDCM
  return (SDAM - SDCM)/SDAM
  
# written by drewda
# used after running getJenksBreaks()
def classify(value, breaks):
  for i in range(1, len(breaks)):
    if value < breaks[i]:
      return i
  return len(breaks) - 1

# Added by Christopher Krause
def chunkItJenks(data, chunks):
    data = sorted(data)
    groups = []
    
    JenksBreaks = getJenksBreaks(data, chunks)
    for i in xrange(chunks):
      if i == 0:
        minBreak = JenksBreaks[i] - 1
      else:
        minBreak = JenksBreaks[i]
      maxBreak = JenksBreaks[i + 1]
      groups.append([dataValue for dataValue in data if dataValue > minBreak and dataValue <= maxBreak])
    

    return groups

if __name__ == "__main__":
    from random import randint
    data = []
    for i in xrange(30):
        data.append(0)
    for i in xrange(70):
        data.append(randint(0,50))
    print getJenksBreaks(data, 5)
    results = chunkItJenks(data, 5)
    for result in results:
        print len(result), result
