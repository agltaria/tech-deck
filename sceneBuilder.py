import maya.cmds as cmds

#def checkDep():
    #Read file name to determine which department to build scene for

#def loadAssets():
    

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

        #update selected asset
    #else error message

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
    cmds.button(label = 'Update all')
    cmds.showWindow('sceneBuilder')


sceneBuilder()