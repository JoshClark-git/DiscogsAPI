import discogs_client as discogs
import time
import math
def artistRunner(listy,name,res):
    accum = 0
    if lowRange == 0.1:
        res = res.releases
    print("Analysing Releases")
    for release in res:
        accum += 1
        if accum % 10 == 0:
            print(accum, "releases analysed")
        if release.data['type'] == 'master':
            if name not in [x.name.lower() for x in release.main_release.artists]:
                break
            oldCount = 0
            newRating = 0
            for version in release.versions:
                currCount = version.community.rating.count
                currAvg = version.community.rating.average
                newCount = currCount + oldCount
                if newCount != 0:
                    newRating = ((oldCount * newRating) + (currCount*currAvg))/newCount
                oldCount = newCount
            listy[release.main_release.id] = [newCount,newRating]
        else:
            if name not in [x.name.lower() for x in release.artists]:
                break
            title = release.id
            count = release.community.rating.count
            rating = release.community.rating.average
            listy[title] = [count,rating]
    return listy

def labelRunner(res) :
    listy = {}
    total = len(res)
    print("Analysing", total,"Releases")
    accum = 0
    currPercent = 0
    for result in res:
        accum += 1
        if math.floor(10 * accum/total) == currPercent:
            print(str(currPercent * 10) + "% analysed")
            currPercent += 1
        try:
            title = result.master.main_release.id
        except:
            title = result.id
        count = result.community.rating.count
        rating = result.community.rating.average
        if title not in listy:
            listy[title] = [count,rating]
        else:
            newCount = listy[title][0] + count
            if newCount != 0:
                newRating = ((listy[title][0] * listy[title][1]) + (count * rating)) / newCount
                listy[title] = [newCount,newRating]
    return listy
def styleRunner(res):
    listy = {}
    total = len(res)
    print("Analysing", total,"Releases")
    accum = 0
    currPercent = 0
    for release in res:
        accum += 1
        if math.floor(10 * accum/total) == currPercent:
            print(str(currPercent * 10) + "% analysed")
            currPercent += 1
        result = d.release(release.id)
        try:
            title = result.master.main_release.id
        except:
            title = result.id
        count = result.community.rating.count
        rating = result.community.rating.average
        if title not in listy:
            listy[title] = [count,rating]
        else:
            newCount = listy[title][0] + count
            if newCount != 0:
                newRating = ((listy[title][0] * listy[title][1]) + (count * rating)) / newCount
                listy[title] = [newCount,newRating]
    return listy       

def bayesianAvg(item,avg,confidence):
    return ((item[0] * item[1]) + (avg * confidence)) / (item[0] + confidence)
def yearAdjust(res):
    if searchType == 'label':
        yearRes = []
        if lowRange != 0.1:
            print("Adjusting", len(res.releases), "Results to Year Specifications")
            [yearRes.append(item) for item in res.releases if (item not in yearRes and (item.year>= lowRange and item.year <= highRange))]
        else:
             [yearRes.append(item) for item in res.releases if item not in yearRes]
        return yearRes
    elif lowRange != 0.1:
        if searchType == 'style':
            print("Adjusting", len(res), "Results to Year Specifications")
            yearRes = [item for item in res if (int(item.year)>= lowRange and int(item.year) <= highRange)]
        else:
            print("Adjusting", len(res.releases), "Results to Year Specifications")
            yearRes = [item for item in res.releases if (item.year>= lowRange and item.year <= highRange)]
        return yearRes
    return res
includeAlias = False
lowRange = 0.1
highRange = 3000


token = input("Input user token (https://www.discogs.com/settings/developers): ")
d = discogs.Client('ExampleApplication/0.1', user_token=token)

searchName = input("Search name: ").lower()
searchType = input("Searching Label, Artist, or Style: ").lower()
while not (searchType == 'artist' or searchType == 'label' or searchType == 'style'):
    searchType = input("Searching Label, Artist, or Style: ").lower()
if searchType == 'artist':
    includeAlias = input("Include search of aliases? (Y/N): ").lower()
    while not (includeAlias == 'n' or includeAlias == 'y'):
        includeAlias = input("Include search of aliases? (Y/N): ").lower()
if searchType == 'style':
    res = d.search(style = searchName, type = 'release')
else:
    results = d.search(searchName, type = searchType)
    index = 0
    while True:
        searchRes = input("Is {} the correct search? (Y/N): ".format(results[index])).lower()
        if searchRes == 'y':
            res = results[index]
            break
        index += 1
years = input("Year Range seperated by '-': ")
if years != '':
    while '-' not in years or ([int(yearArr[0]) > int(yearArr[1]) for yearArr in [years.split('-')]])[0]:
        years = input("Year Range seperated by '-': ")
    yearArr = years.split('-')
    lowRange = int(yearArr[0])
    highRange = int(yearArr[1])
strNumResults = input("Number of results: ")
try:
    numResults = int(strNumResults)
except:
    numResults = 20

yearRes = yearAdjust(res)

if searchType == 'artist':
    listy = artistRunner({},res.name.lower(),yearRes)
    if includeAlias == 'y':
        for aliase in res.aliases:
            print("analysing alias", aliase.name)
            listy = artistRunner(listy,aliase.name.lower(),yearAdjust(aliase))
elif searchType == 'label':
    listy = labelRunner(yearRes)
else:
    listy = styleRunner(yearRes)
            
print("Done Analysis, sorting results")
numElems = len(listy)
numRatings = sum(i[0] for i in listy.values())
avgRating = sum(i[0] * i[1] for i in listy.values())/numRatings
if numElems > 100:
    confidenceNum = sorted(listy.items(),key = lambda item: item[1][0])[int(numElems * (1-(5/numElems)))][1][0]
else:
    confidenceNum = sorted(listy.items(),key = lambda item: item[1][0])[int(len(listy) * .95)][1][0]
    
print(confidenceNum,avgRating)
finalVals = [None] * numElems
accum = 0
for item in listy.items():
    finalVals[accum] = [item[0],bayesianAvg(item[1],avgRating,confidenceNum)]
    accum += 1

print([d.release(x[0]).title for x in ([y for y in (sorted(finalVals,key = lambda item: item[1], reverse = True)[:numResults])])])
print("Done")



