import json
import level

Levels = []

# Opening JSON file
with open('levels.json', 'r') as infile:
 
    # Reading from json file
    levelData = json.load(infile)
    infile.close()

for i in range (0, len(levelData["levels"])):
    thisLevel = level.Level.from_json(levelData["levels"][i])
    Levels.append(thisLevel)

# print(type(Levels[0].goal))

for i in range(0, len(Levels)):
    print(Levels[i])
    print("\n")