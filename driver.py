# Random ideas/notes
# Cool to have multiple sprites for the flag so it can wave a bit (animation)
from fractions import Fraction
import types
import sys
import os
import numpy
from PIL import Image
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import json
import level
import copy
import math
from pygame.locals import *

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

import re
import parser
import math
import unicodedata

# Global variables here
levels = []
currentMove = ''
currentLevel = 0

ballx = 0
bally = 0
dx = 0
dy = 0
inMotion = False
resetting = False
restartLevel = False
restartNegative = False
showEndText = False

# Utility functions go here
def loadLevels(filename):
    with open(filename, 'r') as inFile:
        levelData = json.load(inFile)
        inFile.close()

    for i in range (0, len(levelData["levels"])):
        thisLevel = level.Level.from_json(levelData["levels"][i])
        levels.append(thisLevel)

#check if two numbers are close
def checkClose(num, target):
    ep = 0.00001
    if isinstance(num, str):
        num = parse(num)
    if num > target - ep and num < target + ep:
        return True
    else:
        return False

def checkSpecialNumber(num):
    stringRepresentations = [unicodedata.lookup("GREEK SMALL LETTER PI"), "e", "√2", "√3"]
    specials = [math.pi, math.e, math.sqrt(2), math.sqrt(3)]
    
    multipleRange = 10
    c = 0
    for s in specials:        
        for m in range(-multipleRange, multipleRange + 1):
            if m != 0:
                if(checkClose(num, m * s)):
                    if(m == 1):
                        return stringRepresentations[c]
                    elif(m == -1):
                        return "-" + stringRepresentations[c]
                    else:
                        return "{}".format(m) + stringRepresentations[c]
        c += 1

    return None
        

def getUserInput(lvl, equ):   
    equ = equ.replace(' ', '') #get rid of any whitespace
    if lvl.type == "complex":
        #replace the i's with j's so python can parse
        equ = equ.replace('i','j')

       
        try:
            #convert user input to a complex number
            enteredNum = complex(equ)
        except:
            print('Invalid complex input, please try again!')
            return None
        
        #check that the number entered is still in the list of options.
        for num in lvl.numbers:
            if complex(num.replace('i','j')) == enteredNum: #true when user entered a valid number
                lvl.numbers.remove(equ.replace('j','i'))
                return enteredNum
        
        #didn't find match in valid numbers list
        print('Invalid input, please try again! C')
        return None



    # make sure the user entered only valid numbers
    enteredNums = re.split(' |\+|\-|\*|/|\^|sqrt|\(|\)', equ)
    validNums = lvl.numbers[:] # create copy of valid numbers to make sure you can only use them the number of times allowed
    print(lvl.numbers)
    for i in range(0, len(enteredNums)):
        if not enteredNums[i] == '':
            if not enteredNums[i] in validNums:
                print('Invalid input, please try again! 1')
                return None
            validNums.remove(enteredNums[i])

    # make sure the user entered only valid operations
    enteredOps = re.split(' |\d+|\(|\)|pi|e', equ)
    for i in range(0, len(enteredOps)):
        if not enteredOps[i] == '' and not enteredOps[i] in lvl.operations:
            print('Invalid input, please try again!')
            return None

    # make sure the equation can actually evaluate to something
    value = parse(equ)
    if value != None:
        print('Entered value: ' + str(value))
        lvl.numbers = validNums # consumes used numbers
    return value

def parse(equ):
    equ = equ.replace('^','**')
    equ = equ.replace('sqrt','math.sqrt')
    equ = equ.replace('pi','math.pi')
    equ = equ.replace('e','math.e')
    try:
        return eval(parser.expr(equ).compile())
    except:
        print('Invalid input, please try again!')
        return None

# Starting pygame stuff
pygame.init()
fieldSizeX = 500
fieldSizeY = 500

uiSizeX = 200
uiSizeY = 100

screenSizeX = fieldSizeX + uiSizeX
screenSizeY = fieldSizeY + uiSizeY

standardPadding = 14
# (current) Game boundary
minX, minY, maxX, maxY = -10, -10, 10, 10


#colors
black = (0,0,0)
white = (255,255,255)

# Set up the drawing window
screen = pygame.display.set_mode([screenSizeX, screenSizeY])

# loading assets
fieldImg = pygame.transform.scale(pygame.image.load("field.png"), (fieldSizeX, fieldSizeY))
fieldRect = fieldImg.get_rect()

fieldCheckeredImg = pygame.transform.scale(pygame.image.load("field_checkered.png"), (fieldSizeX, fieldSizeY))
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
    if isinstance(x, str):
        x = parse(x)
    if isinstance(y, str):
        print(parse(y))
        y = parse(y)
    screenX = x * fieldSizeX / (maxX - minX + 1)  + fieldSizeX / 2
    screenY = -y * fieldSizeY / (maxY - minY + 1) + fieldSizeY / 2
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
    global inMotion
    
    numFrames = 60 #animate movement over 60 frames (2 seconds prob)
    destX = ballx + dx
    destY = bally + dy

    print('destination: ' + str(destY))

    startX = ballx
    startY = bally

    #would probably be good to solve an ODE to calcuclate ball path that looks good (realistic friction) and ends up at the right location.
    

    
    inMotion = True
    #animate with linear motion for now:
    for frame in range(numFrames + 1):
        t = (frame / numFrames) * 8 + 2
        
        #linear movement
        #ballx = startX + t * dx
        #bally = startY + t * dy

        ballx = startX + (1/.4) * (-dx/(t) + .5*dx)
        bally = startY + (1/.4) * (-dy/(t) + .5*dy)

        drawField(level)
        pygame.display.flip()
        clock.tick(30)

    #account for round off errors
    ballx = destX
    bally = destY

    inMotion = False
    
    drawField(level)

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


def drawNumberAt(number, x, y, imaginary=False):
    drawTextAt(str(number) + ('i' if imaginary else ''), x, y)
    

def drawGridLines(minX, maxX, minY, maxY, mode):
    numLabels = 21 #20 labels each way
    spacingX = fieldSizeX / numLabels
    spacingY = fieldSizeY / numLabels

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
        

    else:
        for i in range (minX, maxX + 1):
            labelsX.append(i)

        for i in range (minY, maxY + 1):
            labelsY.append(i)

    if mode == "real":
        print()

    if mode == "rational":
        print()
    
    if mode == "complex":
        print()
    
    
    for l in labelsX:
        if l != 0:
            drawNumberAt(l, l, 0)
    
    for l in labelsY:        
        drawNumberAt(l, 0, l, mode == "complex")
    
    
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
    #draw_line_dashed(screen, black, (0, fieldSizeY / 2), (fieldSizeX, fieldSizeY / 2), dash_length=10)
    #print(labelsX)
    #draw_line_dashed(surf, black, (minX, maxY - minY), (maxX, maxY - minY), dash_length=2, scaling=10)

    # Y axis
    #draw_line_dashed(screen, black, (fieldSizeX / 2, 0), (fieldSizeX / 2, fieldSizeY), dash_length=10)
    

    #draw_line_dashed(surf, black, (maxX - minX, minY), (maxX - minX, maxY), dash_length=2)
    

def drawField(level):
    mode = level.type
    #print(mode)
    #global flagRect
    # Fill the background with white
    screen.fill(white)

    # Draw blank field
    screen.blit(fieldImg, fieldRect)
    
    drawGridLines(-10, 10, -10, 10, mode)

    # Draw flag
    flagX = level.goal["x"]
    if isinstance(flagX, str):
        flagX = parse(flagX)
    flagY = level.goal["y"]
    if isinstance(flagY, str):
        flagY = parse(flagY)

    drawAt(flagImg, flagRect, flagX, flagY)
    xcoord = str(Fraction(flagX).limit_denominator())
    if checkSpecialNumber(flagX) != None:
        xcoord = checkSpecialNumber(flagX)
    ycoord = str(Fraction(flagY).limit_denominator())
    if checkSpecialNumber(flagY) != None:
        ycoord = checkSpecialNumber(flagY)
    flagPosString = xcoord + " " + ycoord + ('i' if mode == "complex" else '')
    drawTextAt(flagPosString, flagX+.5, flagY+3)
    

    # Draw ball
    drawAt(ballImg, ballRect, ballx, bally)
    if not inMotion:
        xcoord = str(Fraction(ballx).limit_denominator())
        if checkSpecialNumber(ballx) != None:
            xcoord = checkSpecialNumber(ballx)
        ycoord = str(Fraction(bally).limit_denominator())
        if checkSpecialNumber(bally) != None:
            ycoord = checkSpecialNumber(bally)

        ballPosString = xcoord + " " + ycoord + ('i' if mode == "complex" else '')
        drawTextAt(ballPosString, ballx+.5, bally+.5)


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
    
    #print('ball y = ', bally)
    #print('flagy = ', flagY)
    return False

# Main loop here
# Run until the user asks to quit

#used for setting fps
clock = pygame.time.Clock()



#INPUT BOX IS TOP LEFT UI ELEMENT ON LEFT SIDE PANEL
# input text box stuff
base_font = pygame.font.Font(None, 32)
user_text = ''  
# create rectangle
inputBoxOffsetX = fieldSizeX + standardPadding
inputBoxOffsetY = standardPadding
textInputBoxWidth = 140
textInputBoxHeight = 32
input_rect = pygame.Rect(inputBoxOffsetX, inputBoxOffsetY, textInputBoxWidth, textInputBoxHeight)
# basic font for user typed
base_font = pygame.font.Font(None, 32)
user_text = ''
#default_text = 'Input : '
default_text=''

# color_active stores color(lightskyblue3) which
# gets active when input box is clicked by user
color_active = pygame.Color('lightskyblue3')
  
# color_passive store color(chartreuse4) which is
# color of input box.
color_passive = pygame.Color('chartreuse4')
color = color_passive
active = True

#LEVEL NUMBER BOX IS BELOW INPUT BOX
#box displaying level number
# create rectangle
levelBoxOffsetX = inputBoxOffsetX
levelBoxOffsetY = standardPadding + inputBoxOffsetY + textInputBoxHeight
levelBoxWidth = 140
levelBoxHeight = 32
level_rect = pygame.Rect(levelBoxOffsetX, levelBoxOffsetY, levelBoxWidth, levelBoxHeight)

#NUMBERS BOX IS TOP LEFT ELEMENT BELOW FIELD.
numbersBoxOffsetX = standardPadding
numbersBoxOffsetY = standardPadding + fieldSizeY
numbersBoxWidth = fieldSizeX - 2*standardPadding
numbersBoxHeight = levelBoxHeight
numbers_rect = pygame.Rect(numbersBoxOffsetX, numbersBoxOffsetY, numbersBoxWidth, numbersBoxHeight)
numbers_default_text = 'Available Numbers: '

#OPERATIONS BOX IS BELOW NUMBERS BOX
operationsBoxOffsetX = numbersBoxOffsetX
operationsBoxOffsetY = standardPadding + numbersBoxOffsetY + numbersBoxHeight
operationsBoxWidth = numbersBoxWidth
operationsBoxHeight = levelBoxHeight
operations_rect = pygame.Rect(operationsBoxOffsetX, operationsBoxOffsetY, operationsBoxWidth, operationsBoxHeight)
operations_default_text = 'Available Operations: '

#INFO TEXT BOX:
infoBoxOffsetX = standardPadding
infoBoxOffsetY = standardPadding
infoBoxWidth = screenSizeX - standardPadding * 2
infoBoxHeight = screenSizeY - standardPadding * 2
info_rect = pygame.Rect(infoBoxOffsetX, infoBoxOffsetY, infoBoxWidth, infoBoxHeight)
info_default_text = ''


k = 120
dark_background = pygame.Color(k,k,k)

def updateTextBox():
    if active:
        color = color_active
    else:
        color = color_passive
    
    text_surface = base_font.render(default_text + user_text, True, (255, 255, 255))
    
    # set width of textfield so that text cannot get
    # outside of user's text input
    input_rect.w = max(150, text_surface.get_width()+10)

    # draw rectangle and argument passed which should
    # be on screen
    pygame.draw.rect(screen, color, input_rect)

    # render at position stated in arguments
    screen.blit(text_surface, (input_rect.x+5, input_rect.y+5))

def updateLevelBox(num):
    global level_rect
    boxText = 'Level ' +  str(num)
    text_surface = base_font.render(boxText, True, (255, 255, 255))
    
    # set width of textfield so that text cannot get
    # outside of user's text input
    #level_rect.w = max(100, text_surface.get_width()+10)
    #level_rect = text_surface.get_rect(center=(levelBoxOffsetX+levelBoxWidth / 2, levelBoxOffsetY + levelBoxHeight / 2))
    level_rect.w = text_surface.get_width() +10
    level_rect.h = text_surface.get_height() + 10
    # draw rectangle and argument passed which should
    # be on screen
    
    pygame.draw.rect(screen, dark_background, level_rect)

    # render at position stated in arguments
    screen.blit(text_surface, (level_rect.x+5, level_rect.y+5))

def updateNumbersBox(numbers):
    numlist = ''
    for n in numbers:
        parsed = parse(n)
        specialCheck = checkSpecialNumber(parsed)
        if specialCheck != None:
            parsed = specialCheck
        numlist += str(parsed) + ', '
    numlist = numlist[:-2]

    text_surface = base_font.render(numbers_default_text + numlist, True, (255, 255, 255))
    
    # draw rectangle and argument passed which should
    # be on screen
    #numbers_rect.h = text_surface.get_height() + 10
    pygame.draw.rect(screen, dark_background, numbers_rect)

    # render at position stated in arguments
    screen.blit(text_surface, (numbers_rect.x+5, numbers_rect.y+5))

def updateOperationsBox(operations):
    text = ''
    if len(operations) == 0:
        text = 'None'
    else:
        for o in operations:
            text += o + ', '
        text = text[:-2]

    text_surface = base_font.render(operations_default_text + text, True, (255, 255, 255))
    
    # draw rectangle and argument passed which should
    # be on screen
    #operations_rect.h = text_surface.get_height() + 10
    pygame.draw.rect(screen, dark_background, operations_rect)

    # render at position stated in arguments
    screen.blit(text_surface, (operations_rect.x+5, operations_rect.y+5))


#https://stackoverflow.com/questions/42014195/rendering-text-with-multiple-lines-in-pygame
def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    max_width -= standardPadding
    max_height -= standardPadding
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.

def updateInfoBox(info):
    #text_surface = base_font.render(info_default_text + info, True, (255, 255, 255))
    text_surface = base_font.render('', True, (255, 255, 255))
    
    # draw rectangle and argument passed which should
    # be on screen
    #operations_rect.h = text_surface.get_height() + 10
    pygame.draw.rect(screen, dark_background, info_rect)

    # render at position stated in arguments
    #screen.blit(text_surface, (info_rect.x+5, info_rect.y+5))
    font = pygame.font.SysFont('Arial', 48)
    blit_text(screen, info, (20, 20), font)

curLevel = prevLevel = -1
running = True
loadLevels('levels.json')
nextLevel = True
level = None
while running:

    deltas = None

    if(level != None):
        drawField(level)

    if not showEndText and resetting:
        level = copy.deepcopy(levels[currentLevel])
        #reset ball location
        ballx = 0
        bally = 0        
        resetting = False

    #popups
    if showEndText:
        updateInfoBox(levels[currentLevel].endText)

    if nextLevel:
        updateInfoBox(levels[currentLevel].startText)

    if restartLevel:
        updateInfoBox('You ran out of moves! Try again.')
    
    if restartNegative:
        updateInfoBox('What did you do?! Where did the ball even go? Try again, and think positive this time.')


    # Did the user click the window close button?
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            nextLevel = False
            restartLevel = False
            restartNegative = False
            showEndText = False
            if input_rect.collidepoint(event.pos):
                active = True
            else:
                active = False
                

        if event.type == pygame.KEYDOWN:
            #if the user hits a key to exit the info screen, don't enter that into the input box.
            if nextLevel:
                nextLevel = False
                break
            #check input after enter is pressed
            if event.key == pygame.K_RETURN:
                deltas = getUserInput(level, user_text)
                print('hit enter')
                user_text = ""

            # Check for backspace
            elif event.key == pygame.K_BACKSPACE:
                
                # get text input from 0 to -1 i.e. end.
                user_text = user_text[:-1]

            # Unicode standard is used for string
            # formation
            else:
                user_text += event.unicode
    
    if curLevel != currentLevel and not showEndText:
        curLevel = currentLevel
        resetting = True
        nextLevel = True
    
    #don't draw this over the level info
    if(not nextLevel and not restartLevel and not restartNegative and not showEndText):
        # draw current level data
        updateTextBox()
        updateLevelBox(curLevel)
        updateNumbersBox(level.numbers)
        updateOperationsBox(level.operations)
        #drawGridLines(-10, 10, -10, 10, level.type)

    # Flip (update) the display
    pygame.display.flip()
    doneLevel = False

    if not doneLevel:
        if deltas != None:        
            
            if(isinstance(deltas, complex)):
                dx = deltas.real
                dy = deltas.imag
            else:
                dy = deltas 

            #display this move
            if(dx != 0 or dy != 0): #we don't move on the first level
                animateBallMovement(level)

            #check if we're done with this level
            doneLevel = checkFinishedLevel(level)
            print('done level = ', doneLevel)
            user_text = ""
            if doneLevel:
                currentLevel += 1
                showEndText = True
            elif len(level.numbers) == 0 and not inMotion:
                restartLevel = True
                resetting = True
            elif level.type == "natural" and (ballx < 0 or bally < 0) and not inMotion:
                restartNegative = True
                resetting = True
   
    clock.tick(10)
    


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

#nicer grid code:
# draw = True
#     for x in range(0, fieldSizeX, int(fieldSizeX/maxX/2)):
#         for y in range(0, fieldSizeY, int(fieldSizeY/maxY/2)):
#             if draw:
#                 pygame.draw.rect(screen, (9,140,9), [x, y, (fieldSizeX/maxX/2), (fieldSizeY/maxY/2)])
#             draw = not draw
#         draw = not draw