import maya.cmds as cmds

windowsPath = ""
linuxPath = ""
#def checkDep():
    #Read file name to determine which department to build scene for

#def loadAssets():


#read version number
def readFileVersion(file):
    fileVer = file[-2:]
    verNum = int(fileVer)
    return verNum

#compare current file ver with latest file in folder
def isLatest(currentVer, file):
    #get folder of asset
    if currentVer > readFileVersion(file):
        return True
    return False

def updateSingle():
    objects = []
    #checking how many objects are selected
    for selection in cmds.ls(sl=True):
        objects.append(selection) 
    if len(objects) > 1:
        if cmds.window('alert', exists = True):
            cmds.deleteUI('alert')
        cmds.window('alert', title = "Warning", w = 300, h = 25)
        info = cmds.columnLayout(co = ('both', 10))
        cmds.text("Please select only one asset.")
        cmds.showWindow('alert')
        raise Exception("Please select only one asset.")
    else:
        return

def updateAll():
    return
    #for each asset in outliner
    
        #check if version number is biggest
        #if not, update asset
    #catch for errors

def sceneBuilder():
    if cmds.window('sceneBuilder', exists = True):
        cmds.deleteUI('sceneBuilder')

    cmds.window('sceneBuilder', resizeToFitChildren = True, sizeable = False)
    info = cmds.columnLayout(co = ('both', 10))

    updateButtons = cmds.rowColumnLayout(parent = info, numberOfRows = 1)
    cmds.button(label = 'Update asset', command = 'updateSingle()')
    cmds.separator(w = 10, st = 'none')
    cmds.button(label = 'Update all', command = 'updateAll()')
    cmds.showWindow('sceneBuilder')


sceneBuilder()