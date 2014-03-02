import sys
import time

db_file = "../data/dbFile.txt"
sites_file = "../data/sites.txt"

if len(sys.argv) == 1:
    print "Usage: "+sys.argv[0]+" <search_string>"
    sys.exit(0)

search_string = sys.argv[1]

a = time.time()


f = open(db_file, "r")

lines = 0
occurences = 0
data = []

for line in f:
    lines+=1
    if search_string in line:
        occurences+=1
        data.append(line)

print "Lines: "+str(lines)
print "Occurences: "+str(occurences)

b = time.time()

print "Elapsed: "+str(b-a)