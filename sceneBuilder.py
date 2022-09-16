import maya.cmds as cmds

#def checkDep():
    #Read file name to determine which department to build scene for

#def loadAssets():
    

#def updateSingle():
    #if one asset selected:
        #update selected asset
    #else error message

#def updateAll():
    #for each asset in outliner
        #check if version number is biggest
        #if not, update asset
    #catch for errors




def sceneBuilder():
    if cmds.window('sceneBuilder', exists = True):
        cmds.deleteUI('sceneBuilder')

    cmds.window('sceneBuilder', resizeToFitChildren = True, sizeable = False)
    info = cmds.columnLayout(co = ('both', 10))

sceneBuilder()