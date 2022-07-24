from PIL import Image, ImageDraw
import random
import math
from pathlib import Path

print("Recommended values: 130 generations, 3 starting hyphae.")
generations = int(input("Number of generations: "))
initHyphae = int(input("Starting hyphae: "))
lineLen = 5
imgDims = (1000,1000)
endPointsNum = 580

allLines = []
openEnds = []

#Gets the y-value of angle2 on a bell curve that peaks at angle1 (used for moveList weights)
bellCurve = lambda angle1, angle2: 200*math.e**((-(angle2-angle1)**2)/1000)

#Gets the rate of branching for given initHyphae and generations values. Based entirely around how many endPoints you think there should be in the final state.
#Trust me on this. Spent hours calculating how to find an equation for the rate that would make it always the optimal amount.
branchRate = round(1/(((endPointsNum/initHyphae)**(1/(generations-1)))-1))

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

background = Image.new(mode="RGBA", size=imgDims, color="black")
frames = []

print("-------------------------------------")
print(f"Mycelium will branch approximately {abs(initHyphae-endPointsNum)} times")
print(f"Branch rate of {branchRate}.")
print("-------------------------------------")


#Make the first lines
for i in range(0, initHyphae):
    #Get end coords then draw the hyphae
    startCoords = (round(imgDims[0]/2), round(imgDims[0]/2))
    endCoords, angle = getCoordsSingle(0, startCoords, True)
    ImageDraw.Draw(background).line([startCoords, endCoords], fill=(255,255,round(255-(i/generations)*255),255), width=hyphaeThickness(initHyphae, i))
    openEnds.append([(endCoords), angle])

frames.append(background.copy())

#Draw lines from openEnds for however many generations were specified
for i in range(0, generations):
    openEndsDup = [i for i in openEnds] #Create a duplicate to not fuck with the for loop
    for startCoords in openEndsDup:
        openEnds.remove(startCoords)

        if random.choice(range(0,branchRate)) == 2:
            LRcoords, LRangles = getCoordsBranch(startCoords[1], startCoords[0])
            
            #Draw and record both the left and right lines
            for j in range(0, 2):
                ImageDraw.Draw(background).line([startCoords[0], LRcoords[j]], fill=(255,255,round(255-(i/generations)*255),255), width=hyphaeThickness(generations, i))
                allLines.append([startCoords[0], LRcoords[j]])
                openEnds.append([LRcoords[j], LRangles[j]])
                
        else:
            endCoords, angle = getCoordsSingle(startCoords[1], startCoords[0], False)
            ImageDraw.Draw(background).line([startCoords[0], endCoords], fill=(255,255,round(255-(i/generations)*255),255), width=hyphaeThickness(generations, i))
            allLines.append([startCoords[0], endCoords])
            openEnds.append([endCoords, angle])
    
    #% completion update
    if (i/generations)*100 % 2 == 0:
        print(f"{(i/generations)*100}%")
    frames.append(background.copy())

#Make the last frame longer, so when posted online it doesnt auto-loop
durationList = [100 for i in range(0,len(frames)-1)]
durationList.append(2000)

frames[0].save(f'{Path.cwd()}\\mycGif.gif', save_all=True, append_images=frames[1:], optimize=False, duration=durationList, loop=0)
input("Done!")
