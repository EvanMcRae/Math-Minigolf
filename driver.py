# Random ideas/notes
# Cool to have multiple sprites for the flag so it can wave a bit (animation)
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import json
import level
from pygame.locals import *

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

import re
import parser


# Global variables here
levels = []
currentMove = ''
currentLevel = 0

ballx = 0
bally = 0
dx = 0
dy = 0


# Utility functions go here
def loadLevels(filename):
    with open(filename, 'r') as inFile:
        levelData = json.load(inFile)
        inFile.close()

    for i in range (0, len(levelData["levels"])):
        thisLevel = level.Level.from_json(levelData["levels"][i])
        levels.append(thisLevel)

def getUserInput(lvl, equ):
    print('Enter an equation with the provided numbers and operations:')
   
    # make sure the user entered only valid numbers
    enteredNums = re.split(' |\+|\-|\*|/|\^', equ)
    validNums = lvl.numbers # create copy of valid numbers to make sure you can only use them the number of times allowed
    for i in range(0, len(enteredNums)):
        if not enteredNums[i] in validNums:
            print('Invalid input, please try again!')
            return None
        validNums.remove(enteredNums[i])

    # make sure the user entered only valid operations
    enteredOps = re.split('\d+', equ)
    for i in range(0, len(enteredOps)):
        if not enteredOps[i] == '' and not enteredOps[i] in lvl.operations:
            print('Invalid input, please try again!')
            return None

    # make sure the equation can actually evaluate to something
    equ = equ.replace('^','**')
    try:
        formula = parser.expr(equ).compile()
    except:
        print('Invalid input, please try again!')
        return None
    
    value = eval(formula)
    print('Entered value: ' + str(value))
    lvl.numbers = validNums # consumes used numbers
    return value

# Starting pygame stuff
pygame.init()
resx = 800
resy = 800

# (current) Game boundary
minX, minY, maxX, maxY = -10, -10, 10, 10

#colors
black = (0,0,0)
white = (255,255,255)

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

def getScreenCoords(x,y):
    screenX = x * resx / (maxX - minX + 1)  + resx / 2
    screenY = -y * resy / (maxY - minY + 1) + resy / 2
    return (screenX, screenY)

def getScreenCoordsTup(tup):    
    return getScreenCoords(tup[0], tup[1])

# Scales a tuple coordinate by some factor
def scaleCoords(tup, scale):
    return (tup[0] * scale, tup[1] * scale)

# Adapted from https://codereview.stackexchange.com/questions/70143/drawing-a-dashed-line-with-pygame
import numpy  as np
def draw_line_dashed(surface, color, start_pos, end_pos, width = 1, dash_length = 10, exclude_corners = True, scaling=1):

    #start_pos = getScreenCoords(start_pos[0], start_pos[1])
    #end_pos = getScreenCoords(end_pos[0], end_pos[1])
    
    # convert tuples to numpy arrays
    start_pos = np.array(start_pos)
    end_pos   = np.array(end_pos)

    # get euclidian distance between start_pos and end_pos
    length = np.linalg.norm(end_pos - start_pos)

    # get amount of pieces that line will be split up in (half of it are amount of dashes)
    #dash_amount = int(length / dash_length)
    dash_amount = 2 #makes a solid line
    # x-y-value-pairs of where dashes start (and on next, will end)
    dash_knots = np.array([np.linspace(start_pos[i], end_pos[i], dash_amount) for i in range(2)]).transpose()
    # print(dash_knots)
    # for coord in dash_knots:
    #     coord[0] = coord[0] * scaling
    #     coord[1] = coord[1] * scaling
    # print(dash_knots)
    pygame.draw.line(surface, color, start_pos, end_pos, width) 
    # return [pygame.draw.line(surface, color, tuple(dash_knots[n]), tuple(dash_knots[n+1]), width)
    #         for n in range(int(exclude_corners), (dash_amount - int(exclude_corners)), 8)]


# Draws img at x and y location on screen. Treats 0,0 as the center of the screen.
def drawAt(img, rect, x,y):
    screenX, screenY = getScreenCoords(x,y)

    offsetX = rect.width / 2
    offsetY = rect.height / 2
    rect = rect.move(screenX - offsetX, screenY - offsetY)
    screen.blit(img, rect)


# We might want to make this apart of the ball class
def animateBallMovement(level):
    global ballx
    global bally
    numFrames = 60 #animate movement over 60 frames (2 seconds prob)
    destX = ballx + dx
    destY = bally + dy

    startX = ballx
    startY = bally

    #would probably be good to solve an ODE to calcuclate ball path that looks good (realistic friction) and ends up at the right location.
    #If that's too difficult, something that looks DECENT is: 
    # k = 2.9
    # x coord = 1/(t^k)
    # t = [2, 10]. t is the time step of the animation.
    # We could scale this as needed, using



    #animate with linear motion for now:
    for frame in range(numFrames + 1):
        t = frame / numFrames
        ballx = startX + t * dx
        bally = startY + t * dy
        drawField(level)
        pygame.display.flip()
        clock.tick(30)

    #account for round off errors
    ballx = destX
    bally = destY

    print()


# Draws the text on the screen such that the center of the text's bounding box
def drawTextAt(text, x, y, size=20):
    font = pygame.font.SysFont('arial', size)
    renderedText = font.render(text, True, (0, 0, 0))

    #get the offset so that the coordinate we input is the center of what we're drawing
    offsetX = renderedText.get_width() / 2
    offsetY = renderedText.get_height() / 2
    
    coords = getScreenCoords(x, y)
    offsetCoords = (coords[0] - offsetX, coords[1] - offsetY)    
    screen.blit(renderedText, offsetCoords)


def drawNumberAt(number, x, y):
    drawTextAt(str(number), x, y)
    

def drawGridLines(minX, maxX, minY, maxY, mode):
    numLabels = 21 #20 labels each way
    spacingX = resx / numLabels
    spacingY = resy / numLabels

    labelsX = []
    labelsY = []

    #Override mode until we get other things working better
    mode = "integer"
    

    if mode == "natural":
        numLabels = 11
        for i in range (maxX + 1):
            labelsX.append(i)

        for i in range (maxY + 1):
            labelsY.append(i)
        

    if mode == "integer":
        for i in range (minX, maxX + 1):
            labelsX.append(i)

        for i in range (minY, maxY + 1):
            labelsY.append(i)

    if mode == "real":
        print()

    if mode == "rational":
        print()
    
    if mode == "imaginary":
        print()
    
    
    for l in labelsX:
        if l != 0:
            drawNumberAt(l, l, 0)
    
    for l in labelsY:        
        drawNumberAt(l, 0, l)
    
    
    for xcoord in labelsX:
        for ycoord in labelsY:          

            #draw vertical line
            start = (xcoord, 0)
            end = (xcoord, ycoord)            
            pygame.draw.line(screen, black, getScreenCoordsTup(start), getScreenCoordsTup(end), 1) 
            #print('start: ', getScreenCoordsTup(start))

            #draw horizontal line
            start = (0, ycoord)
            end = (xcoord, ycoord)            
            pygame.draw.line(screen, black, getScreenCoordsTup(start), getScreenCoordsTup(end), 1) 


    # The coords inputted to draw_line_dashed (hopefully) get converted to screenspace automagically
    # X axis
    #draw_line_dashed(screen, black, (0, resy / 2), (resx, resy / 2), dash_length=10)
    #print(labelsX)
    #draw_line_dashed(surf, black, (minX, maxY - minY), (maxX, maxY - minY), dash_length=2, scaling=10)

    # Y axis
    #draw_line_dashed(screen, black, (resx / 2, 0), (resx / 2, resy), dash_length=10)
    

    #draw_line_dashed(surf, black, (maxX - minX, minY), (maxX - minX, maxY), dash_length=2)
    

def drawField(level):
    mode = level.type
    #global flagRect
    # Fill the background with white
    screen.fill(white)

    # Draw blank field
    screen.blit(fieldImg, fieldRect)
    
    drawGridLines(-10, 10, -10, 10, "natural")

    # Draw flag
    flagX = level.goal["x"]
    flagY = level.goal["y"]

    drawAt(flagImg, flagRect, flagX, flagY)
    drawTextAt("flag", flagX, flagY + flagRect.height / 1.5)
    

    # Draw ball
    drawAt(ballImg, ballRect, ballx, bally)
    drawTextAt("", flagX, flagY + ballRect.height / 1.5)


def printLevelInfo(lvl):
    # very temporary
    print('Level ' + str(lvl.number) + ':')
    print(lvl.startText)
    print('Operations: ' + str(lvl.operations)[1:-1])
    print('Numbers: ' + str(lvl.numbers)[1:-1])

    print('Goal location: ',end='')

    #if(lvl.type == "natural" or lvl.type == "integer"):
    print("({}, {})".format(lvl.goal["x"], lvl.goal["y"]))



#checks if the ball is within a small neighborhood of the goal. This is for checking floating point goal locations
def checkFinishedLevel(level):
    ep = 0.00001
    flagX = level.goal["x"]
    flagY = level.goal["y"]

    if ballx > flagX - ep and ballx < flagX + ep and bally > flagY - ep and bally < flagY + ep:
        return True
    print('ball y = ', bally)
    print('flagy = ', flagY)
    return False

# Main loop here
# Run until the user asks to quit

#used for setting fps
clock = pygame.time.Clock()

# input text box stuff
base_font = pygame.font.Font(None, 32)
user_text = ''  
# create rectangle
input_rect = pygame.Rect(200, 200, 140, 32)
# basic font for user typed
base_font = pygame.font.Font(None, 32)
user_text = ''
  
# create rectangle
input_rect = pygame.Rect(200, 200, 140, 32)
# color_active stores color(lightskyblue3) which
# gets active when input box is clicked by user
color_active = pygame.Color('lightskyblue3')
  
# color_passive store color(chartreuse4) which is
# color of input box.
color_passive = pygame.Color('chartreuse4')
color = color_passive
active = False
def updateTextBox():
    if active:
        color = color_active
    else:
        color = color_passive
    
    # draw rectangle and argument passed which should
    # be on screen
    pygame.draw.rect(screen, color, input_rect)
  
    text_surface = base_font.render(user_text, True, (255, 255, 255))
    
    # render at position stated in arguments
    screen.blit(text_surface, (input_rect.x+5, input_rect.y+5))
      
    # set width of textfield so that text cannot get
    # outside of user's text input
    input_rect.w = max(100, text_surface.get_width()+10)


running = True
loadLevels('levels.json')
while running:
    level = levels[currentLevel]

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                else:
                    active = False
    
        if event.type == pygame.KEYDOWN:

            # Check for backspace
            if event.key == pygame.K_BACKSPACE:

                # get text input from 0 to -1 i.e. end.
                user_text = user_text[:-1]

            # Unicode standard is used for string
            # formation
            else:
                user_text += event.unicode
    
    printLevelInfo(level)
    
    #reset ball location
    ballx = 0
    bally = 0

    # draw current level data
    drawField(level)
    updateTextBox()
    #drawGridLines(-10, 10, -10, 10, level.type)

    # Flip (update) the display
    pygame.display.flip()
    doneLevel = False

    if not doneLevel:
        # in the future we need to change dx or dy depending on how the user enters input

        #deltas = getUserInput(level)
        #prompt for input until we get something good
        #if deltas == None:
            #drawField(level)
        deltas = None
            #deltas = getUserInput(level)
            
        if deltas != None:                
            #we want this later.
            #dx, dy = deltas    

            #for now we do this
            dy = deltas 

            #display this move
            animateBallMovement(level)

            #check if we're done with this level
            doneLevel = checkFinishedLevel(level)
            print('done level = ', doneLevel)

    else:
        #if <ball at correct location>
        currentLevel += 1
        #wait()
        
    clock.tick(30)
    


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
z = complex(x,y)

print(z)

z += 10

print(z)


#nicer grid code:
# draw = True
#     for x in range(0, resx, int(resx/maxX/2)):
#         for y in range(0, resy, int(resy/maxY/2)):
#             if draw:
#                 pygame.draw.rect(screen, (9,140,9), [x, y, (resx/maxX/2), (resy/maxY/2)])
#             draw = not draw
#         draw = not draw