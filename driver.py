# Random ideas/notes
# Cool to have multiple sprites for the flag so it can wave a bit (animation)

import pygame
import json
import level


# Global variables here
levels = []
currentMove = ''
currentLevel = 0

# Utility functions go here
def loadLevels(filename): # provide levels.json here
    with open(filename, 'r') as inFile:
        levelData = json.load(inFile)
        inFile.close()

    for i in range (0, len(levelData["levels"])):
        thisLevel = level.Level.from_json(levelData["levels"][i])
        levels.append(thisLevel)

def parseInput(input):
    print()

def getUserInput():
    print()



# Starting pygame stuff
pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([500, 500])
fieldImg = pygame.image.load("field.png")
fieldCheckeredImg = pygame.image.load("field_checkered.png")
holeImg = pygame.image.load("hole.png")
flagImg = pygame.image.load("flag.png")
flagNoHoleImg = pygame.image.load("flag_no_hole.png")
ballImg = pygame.image.load("ball.png")
holeImg = pygame.image.load("hole.png")

# Pygame related functions here

# We might want to make this apart of the ball class
def animateBallMovement(destination):
    #would probably be good to solve an ODE to calcuclate ball path that looks good (realistic friction) and ends up at the right location.
    #If that's too difficult, something that looks DECENT is: 
    # k = 2.9
    # x coord = 1/(t^k)
    # t = [2, 10]. t is the time step of the animation.
    # We could scale this as needed, using
    print()

def drawField(level):
    #do something
    print()




# Main loop here
# Run until the user asks to quit
running = True
loadLevels('levels.json')
while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with white
    screen.fill((255, 255, 255))

    # Draw a solid blue circle in the center
    pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)

    # Flip the display
    pygame.display.flip()

    # Use current level data
    drawField(levels[currentLevel])

    print(levels[currentLevel].startText)
    getUserInput()


# Done! Time to quit.
pygame.quit()