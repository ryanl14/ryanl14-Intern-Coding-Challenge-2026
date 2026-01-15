import csv
import json
import math

fileCSV = "SensorData1.csv"
# fileCSV = "Samples/SampleData1.csv"

fileJSON = "SensorData2.json"
# fileJSON = "Samples/SampleData2.json"

fields = []
rows = {}

# Read CSV file
with open(fileCSV, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    fields = next(csvreader)
    for row in csvreader:
        rows[row[0]] = row[1::]

#  The sensors have an accuracy of 100 meters, meaning that the reported location is within 100 meters of the actual anomaly location.


# wgs 84
# semi-major axis 
a = 6378137.0
# semi-minor axis 
b = 6356752.314245
# ^^ pulled from wikipedia tbh

# math helper functions
def getN(lat):
    return a**2 / math.sqrt(a**2 * math.cos(lat)**2 + b**2 * math.sin(lat)**2)

def getX(lat, lon, N):
    return N * math.cos(lat) * math.cos(lon)

def getY(lat, N):
    return (b**2 / a**2) * N * math.sin(lat)

def getZ(lat, lon, N):
    return N * math.cos(lat) * math.sin(lon)

res = {}
with open(fileJSON, 'r') as jsonfile:
    data = json.load(jsonfile)
    for i in data:
        lat1 = math.radians(i["latitude"])
        lon1 = math.radians(i["longitude"])
        N = getN(lat1)
        x  = getX(lat1, lon1, N)
        y  = getY(lat1, N)
        z  = getZ(lat1, lon1, N)

        for key in rows:
            lat2 = math.radians(float(rows[key][0]))
            lon2 = math.radians(float(rows[key][1]))
            N2 = getN(lat2)
            x2 = getX(lat2, lon2, N2)
            y2 = getY(lat2, N2)
            z2 = getZ(lat2, lon2, N2)

            # this distance is direct line distance through the earth... maybe not the best...
            # but if we are looking for 100m accuracy should not be far off curvature distance
            dist = math.sqrt((x2 - x)**2 + (y2 - y)**2 + (z2 - z)**2)
            if dist <= 100:
                res[key] = i["id"]

                # Remove matched row to prevent duplicate matches, also break out of loop
                # unknown if we should be looking for closest matches or just first match
                rows.pop(key)
                break

with open("CommonSignalsOutput.json", 'w') as outfile:
    json.dump(res, outfile, indent=4)