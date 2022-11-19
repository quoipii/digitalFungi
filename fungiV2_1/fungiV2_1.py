################################################################################################
#This version accepts masks.
#The fungi will only grow within the white pixels of a given mask.
#Add a folder titled Masks and within which enclose any masks you would like to have in the program.
#Add an entirely white mask to have a default mycelium simulation.
################################################################################################

import random, os
from pathlib import Path
import numpy as np
from PIL import Image as im
from datetime import datetime as dt

#Start timer to time the whole process
t1 = dt.now()

#The probabilities assigned to different growing angles and a function to create those angles
angleGen = lambda endAngle: [(endAngle-0.25)%2, endAngle, (endAngle+0.25)%2]

#Generates all 8 coords around the origin, along with their angles
genCoords = lambda coord: [(coord[0]+j, coord[1]+i) for i in range(-1,2) for j in range(-1,2) if not (i == 0 and j == 0)]

#Removes a given coordinate and its angle from all necessary lists
def removeMove(moves, angles, anglePr, allmoves, item):
    if item in moveCoords:
        angles.remove(moveAngles[moveCoords.index(item)])
        anglePr.remove(localAnglePr[moveCoords.index(item)])
        moves.remove(item)
    allmoves.remove(item)

#Creates an array that acts as the environment the fungi lives in
petri = np.zeros([1000, 1000])
petriX, petriY = petri.shape

#Customisable params, strtPr is the prob. that a hyphae grows straight.
initHyphae = int(input("How many initial strands should grow (1 - 8)?"))
genNum = int(input("How many generations should be done? "))
fps = int(input("What approximate FPS would you like the animation to have? "))
branchPr = float(input("What should the chance of the mycelium branching be? "))
strtPr = float(input("How random should the movement be (0.01 - most random, 0.99 - least random)? "))
initColour = 255.

#Non-customisable params
anglePr = [(1-strtPr)/2, strtPr, (1-strtPr)/2]
angleList = [0.75, 0.5, 0.25, 1., 0., 1.25, 1.5, 1.75]
frames = []
allIndicies = []

#Place a single cell in the centre
originX, originY = (round(petriX/2), round(petriY/2))
petri[originY][originX] = initColour
endList = [((originX, originY), -1)]
initMoves = genCoords((originX, originY))
unselectedMoves = [i for i in initMoves]

#Setup an image mask, mycelium will avoid non-white pixels as thought they are walls.
allMasks = '\n- '.join([fileName.split('.')[0] for fileName in os.listdir(f"{Path.cwd()}\\Masks")])
maskName = input(f'All available masks:\n- {allMasks}\nPlease select a mask: ')
petriMask = (np.array(im.open(f"{Path.cwd()}\\Masks\\{maskName}.png")) > 3)[:, :, 0]

#Generates however many initial cells were specified
for i in range(initHyphae):
    cellPos = random.choice(unselectedMoves)
    petri[cellPos[1]][cellPos[0]] = initColour
    endList.append((cellPos, angleList[genCoords((originX, originY)).index(cellPos)]))
    unselectedMoves.remove(cellPos)
endList.remove(((originX, originY), -1))
frames.append(im.fromarray(petri))

#Generates next moves for all strands over the course of n generations
colour = initColour
for generation in range(genNum):
    endListCopy = [i for i in endList]

    #Grows existing endPoints
    for cell in endListCopy:
        #Generate 3 possible move angles, alongside all 8 surrounding coords
        moveAngles = angleGen(cell[1])
        allMoveCoords = genCoords(cell[0])
        localAnglePr = [i for i in anglePr]
        moveCoords = [allMoveCoords[angleList.index(angle)] for angle in moveAngles]
        allMoveCoordsCopy = [i for i in allMoveCoords]
        
        #Only check for valid growth after 1 generation - this allows initial hyphae to grow properly
        if generation > 1:
            for coord in allMoveCoordsCopy:
                #Check if the coords are invalid or not
                if (coord[1] >= petriY or coord[0] >= petriX) or (coord[1] < 0 or coord[0] < 0) or (petri[coord[1]][coord[0]] != 0.)  or (petriMask[coord[1]][coord[0]] == False):
                    removeMove(moveCoords, moveAngles, localAnglePr, allMoveCoords, coord)

                #Check if any moveCoords are moving through a diagonal hyphae by checking up down left and right coords for cells. if a moveCoord is surrounded by cells, remove it.
                elif angleList[allMoveCoordsCopy.index(coord)] in [0.25, 0.75, 1.25, 1.75]:
                    #Gets the angle of the move if it's on a diagonal, since only diagonal moves can pass through diagonal hyphae, alongside the surrounding angles to check for cells
                    coordAngle = angleList[allMoveCoordsCopy.index(coord)]
                    greaterAngle = allMoveCoordsCopy[angleList.index((coordAngle+0.25)%2)]
                    lesserAngle = allMoveCoordsCopy[angleList.index((coordAngle-0.25)%2)]

                    try:
                        if (petri[lesserAngle[1]][lesserAngle[0]] != 0.) and (petri[greaterAngle[1]][greaterAngle[0]] != 0.):
                            removeMove(moveCoords, moveAngles, localAnglePr, allMoveCoords, coord)
                    except:
                        pass

        #If no moveCoords moves remain, pick from allMoveCoords. If none of *them* remain, do nothing and remove the endpoint.
        if len(moveCoords) != 0:
            move = random.choices(moveCoords, localAnglePr)[0]
            endList.append((move, moveAngles[moveCoords.index(move)]))
            petri[move[1]][move[0]] = colour
            allIndicies.append((move[0],move[1]))

        elif len(allMoveCoords) != 0:
            move = random.choice(allMoveCoords)
            endList.append((move, angleList[genCoords(cell[0]).index(move)]))
            petri[move[1]][move[0]] = colour      
            allIndicies.append((move[0],move[1]))      
        
        endList.remove(cell)

    #Grows branches from previous endpoints
    counter = 1
    if round(branchPr) > 1:
        counter = round(branchPr)

    if random.random() <= branchPr:
        while counter != 0 and len(allIndicies) != 0:
            valid = False
            while valid == False and len(allIndicies) != 0:
                branchCoord = random.choice(allIndicies)
                allMoves = genCoords(branchCoord)

                #Remove invalid moves.
                for move in [i for i in allMoves]:
                    if move[1] >= petriY or move[0] >= petriX or move[1] < 0 or move[0] < 0 or petri[move[1]][move[0]] != 0. or petriMask[move[1]][move[0]] == False:
                        allMoves.remove(move)

                if len(allMoves) != 0:
                    move = random.choice(allMoves)
                    petri[move[1]][move[0]] = colour     
                    endList.append((move, angleList[allMoves.index(move)]))
                    counter -= 1
                    valid = True
                else:
                    allIndicies.remove(branchCoord)

    #Take current petri dish state and convert it to a frame
    frames.append(im.fromarray(petri))

    #Update colour to become more grey as animation goes on
    colour = round(initColour - ((initColour-10)*generation/genNum))

    if generation % round(0.05*genNum) == 0:
        print(f"{round(100*generation/genNum, 2)}% complete")

#Add the last frame a couple times so that it pauses briefly on the final frame
for i in range(20):
    frames.append(frames[-1])

print("Compiling gif...")
frames[0].save(f'{Path.cwd()}\\mycelium.gif', save_all=True, append_images=frames[1:], duration=1000/fps, loop=0, format="gif")
frames[-1].convert('RGB').save(f'{Path.cwd()}\\mycelium.png')
input(f'Done in {dt.now()-t1}')
