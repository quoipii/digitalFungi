from PIL import Image, ImageDraw
import random
import math
from pathlib import Path

generations = 150
initHyphae = 3
lineLen = 5
imgDims = (1000,1000)

openEnds = []

#Gets the y-value of angle2 on a bell curve that peaks at angle1 (used for moveList weights)
bellCurve = lambda angle1, angle2: 200*math.e**((-(angle2-angle1)**2)/1000)

#Makes lines go from thick to thin as they grow further
hyphaeThickness = lambda forLoopMax, forLoopPos: round(((forLoopMax-forLoopPos)+1)/(0.1*forLoopMax))

#Gets the coordinates of the next line. Makes a list of angles that the new branch could grow at. Converts those angles to coordinates around a circle of radius lineLen, then returns the result of a weighted random selection of coords
def getCoordsSingle(prevAngle, coords, isInit):
    x1, y1 = coords
    angleList = [angle for angle in range(0,360,15)]
    moveList = [(round(x1 + lineLen*math.cos(angle*(math.pi/180))) - 1, round(y1 - lineLen*math.sin(angle*(math.pi/180))) - 1) for angle in angleList]
    weightList = [round(bellCurve(angleList[moveList.index(moveCoord)], prevAngle), 1) for moveCoord in moveList]
    
    if isInit == True:
        coord = random.choice(moveList)
    else:
        coord = random.choices(moveList, weights=weightList)[0]
    return coord, angleList[moveList.index(coord)]

#Similar to getCoordsSingle, but gets coords from a bit to the left and a bit to the right of the previous angle on the bell curve. (means branches leave at opposing angles)
def getCoordsBranch(prevAngle, coords):
    x1, y1 = coords
    angleList = [angle for angle in range(0,360,15)]
    moveList = [(round(x1 + lineLen*math.cos(angle*(math.pi/180))) - 1, round(y1 - lineLen*math.sin(angle*(math.pi/180))) - 1) for angle in angleList]
    
    weightListLeft = [round(bellCurve(prevAngle, angleList[moveList.index(moveCoord)]+20), 1) for moveCoord in moveList]
    weightListRight = [round(bellCurve(prevAngle, angleList[moveList.index(moveCoord)]-20), 1) for moveCoord in moveList]
    coordLeft = random.choices(moveList, weights=weightListLeft)[0]
    coordRight = random.choices(moveList, weights=weightListRight)[0]
    return [coordLeft, coordRight], [angleList[moveList.index(coordLeft)], angleList[moveList.index(coordRight)]]

background = Image.new(mode="RGB", size=imgDims, color="white")
frames = []
print(f"Mycelium will branch approximately {((initHyphae-1)*10)*generations} times")

#Make the first lines
for i in range(0, initHyphae):
    #Get end coords then draw the hyphae
    startCoords = (round(imgDims[0]/2), round(imgDims[0]/2))
    endCoords, angle = getCoordsSingle(0, startCoords, True)
    ImageDraw.Draw(background).line([startCoords, endCoords], fill=(0,0,0,255), width=hyphaeThickness(initHyphae, i))
    openEnds.append([(endCoords), angle])

    frames.append(background.copy())

#Draw lines from openEnds for however many generations were specified
for i in range(0, generations):
    openEndsDup = [i for i in openEnds] #Create a duplicate to not fuck with the for loop
    for startCoords in openEndsDup:
        openEnds.remove(startCoords)

        if random.choice(range(0,round((initHyphae-1)*10))) == 2:
            LRcoords, LRangles = getCoordsBranch(startCoords[1], startCoords[0])
            ImageDraw.Draw(background).line([startCoords[0], LRcoords[0]], fill=(0,0,0,255), width=hyphaeThickness(generations, i))
            ImageDraw.Draw(background).line([startCoords[0], LRcoords[1]], fill=(0,0,0,255), width=hyphaeThickness(generations, i))
            openEnds.append([LRcoords[0], LRangles[0]])
            openEnds.append([LRcoords[1], LRangles[1]])

        else:
            endCoords, angle = getCoordsSingle(startCoords[1], startCoords[0], False)
            ImageDraw.Draw(background).line([startCoords[0], endCoords], fill=(0,0,0,255), width=hyphaeThickness(generations, i))
            openEnds.append([endCoords, angle])

    if (i/generations)*100 % 2 == 0:
        print(f"{(i/generations)*100}%")
    frames.append(background.copy())

#Make the last frame longer, so when posted online it doesnt auto-loop
durationList = [100 for i in range(0,len(frames)-1)]
durationList.append(2000)

frames[0].save(f'{Path.cwd()}\\mycGif.gif', save_all=True, append_images=frames[1:], optimize=False, duration=durationList, loop=0)
background.show()