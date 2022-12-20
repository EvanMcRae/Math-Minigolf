# Random ideas/notes
# Cool to have multiple sprites for the flag so it can wave a bit (animation)

import pygame
import json
import level
from pygame.locals import *

# Global variables here
levels = []
currentMove = ''
currentLevel = 0

ballx = 0
bally = 0

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
resx = 800
resy = 800
# Set up the drawing window
screen = pygame.display.set_mode([resx, resy])

# loading assets
fieldImg = pygame.transform.scale(pygame.image.load("field.png"), (resx, resy))
fieldRect = fieldImg.get_rect()

fieldCheckeredImg = pygame.transform.scale(pygame.image.load("field_checkered.png"), (resx, resy))
fieldCheckeredRect = fieldCheckeredImg.get_rect()

holeImg = pygame.image.load("hole.png")
holeRect = holeImg.get_rect()

flagImg = pygame.image.load("flag.png")
flagRect = flagImg.get_rect()

flagNoHoleImg = pygame.image.load("flag_no_hole.png")
flagNoHoleRect = flagNoHoleImg.get_rect()

ballImg = pygame.image.load("ball.png")
ballRect = ballImg.get_rect()

holeImg = pygame.image.load("hole.png")
holeRect = holeImg.get_rect()

# Pygame related functions here
def wait():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()                
            if event.type == KEYDOWN and event.key == K_f:
                return

# Draws img at x and y location on screen. Treats 0,0 as the center of the screen.
def drawAt(img, rect, x,y):
    screenX = x + resx / 2
    screenY = -y + resy / 2
    offsetX = rect.width / 2
    offsetY = rect.height / 2
    rect = rect.move(screenX - offsetX, screenY - offsetY)
    screen.blit(img, rect)


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
    print(level)
    global flagRect
    # Fill the background with white
    screen.fill((255, 255, 255))

    # Draw blank field
    screen.blit(fieldImg, fieldRect)
    
    # Draw flag
    drawAt(flagImg, flagRect, level.goal["x"], level.goal["y"])

    # Draw ball
    drawAt(ballImg, ballRect, ballx, bally)

   






# Main loop here
# Run until the user asks to quit

#used for setting fps
clock = pygame.time.Clock()

running = True
loadLevels('levels.json')
while running:
    

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with white
    screen.fill((255, 255, 255))

    # draw current  level data
    drawField(levels[currentLevel])
    
    # Draw a solid blue circle in the center
    #pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)

    # Flip (update) the display
    pygame.display.flip()

    

    print(levels[currentLevel].startText)
    getUserInput()
    #clock.tick(5) #5 fps

    wait()


# Done! Time to quit.
pygame.quit()




#before main loop

# load assets, levels, etc


# levelCounterHere
# #main loop
# get the level we're on.
# Display level in background (blurred).
# Show start text.
# Close start text after an amount of time or user input
# unblur background

# display level information (what moves are available and where goal is.)
# wait for user input
# process input
# display result of input (if its valid. If not, go back to wait for user input)
# If they have more moves, go back to wait for user input.

# Once out of moves, display end text for an amount of time or until user input.

import parser
from math import sin

formula = "1x,2y"
code = parser.expr(formula).compile()
x = 10
print(eval(code))

# importing "cmath" for complex number operations
import cmath

# Initializing real numbers
x = 5
y = 3

# converting x and y into complex number
z = complex(x,y);

print(z)

z += 10

print(z)