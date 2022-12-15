import json
import level

levels = []

# Opening JSON file
with open('levels.json', 'r') as inFile:
 
    # Reading from json file
    levelData = json.load(inFile)
    inFile.close()

for i in range (0, len(levelData["levels"])):
    thisLevel = level.Level.from_json(levelData["levels"][i])
    levels.append(thisLevel)

for i in range(0, len(levels)):
    print(levels[i])
    print("\n")