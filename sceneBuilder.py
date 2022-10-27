import os
import os.path
import maya.cmds as cmds

def loadAsset(newRefPath, currentRefNode):
    cmds.file(newRefPath, loadReference = currentRefNode)
    return


#read version number
def readFileVersion(fileName):
    fileVer = fileName.split('.')[1]
    verNum = int(fileVer[-3:])
    return verNum

def getFileName(file):
    name = cmds.referenceQuery(file, f = True, shortName = True)   
    return name

def getRelevantFiles(filesInDir, selectedFile): #gets all file versions and filters out any other files that may be in the main folder
    relevantFiles = []
    fileNameToSplit = os.path.basename(selectedFile)
    indexDot = fileNameToSplit.index('.')
    fileName = fileNameToSplit[:indexDot]
    for file in filesInDir:
        if fileName in file:
            relevantFiles.append(file)
    return relevantFiles


def isLatest(currentFile, directoryFile): #compare current file version with files in directory
    if readFileVersion(currentFile) >= readFileVersion(directoryFile):
        return True
    else:
        return False

def returnLatest(currentFile): #returns name of most updated file
        filePath = cmds.referenceQuery(currentFile, f = True)
        folderPath = os.path.dirname(filePath)
        filesInDir = os.listdir(folderPath)
        files = getRelevantFiles(filesInDir, filePath) #only get files with asset name in them
        for file in files:
            if not isLatest(currentFile, file):
                return file
        return currentFile

def returnLatestPath(currentFile, latestFile):
    filePath = cmds.referenceQuery(currentFile, f = True)
    folderPath = os.path.dirname(filePath)
    path = os.path.abspath(os.path.join(folderPath, latestFile))
    return path

def updateSingle():
    objects = []
    count = []
    for selection in cmds.ls(sl=True): #checking how many objects are selected
        count.append(selection)
    if len(count) > 1:
        if cmds.window('alert', exists = True):
                cmds.deleteUI('alert')
        cmds.window('alert', title = "Warning", w = 300, h = 25)
        info = cmds.columnLayout(co = ('both', 10))
        cmds.text("Please select only one asset.")
        cmds.showWindow('alert')
        raise Exception("Please select only one asset.")
    else:
        objects.append(selection)
    check = cmds.referenceQuery(objects[0], inr = True) #is asset a reference?
    if(check == 0): #blocks off selecting a non-reference asset
        if cmds.window('alert', exists = True):
            cmds.deleteUI('alert')
        cmds.window('alert', title = "Warning", w = 300, h = 25)
        info = cmds.columnLayout(co = ('both', 10))
        cmds.text("Please select a reference asset only.")
        cmds.showWindow('alert')
        raise Exception("Please select a reference asset only.") 

    elif(check == 1):
        objects.append(selection)
        filePath = cmds.referenceQuery(objects[0], f = True)
        updatedAsset = returnLatest(filePath)
        latestPath = returnLatestPath(filePath, updatedAsset)
        loadAsset(latestPath, cmds.referenceQuery(objects[0], rfn = True))
        if cmds.window('alert', exists = True):
            cmds.deleteUI('alert')
        cmds.window('alert', title = "Warning", w = 300, h = 25)
        info = cmds.columnLayout(co = ('both', 10))
        cmds.text("Asset updated.")
        cmds.showWindow('alert')
            
def checkAllForUpdates():
    objects = []
    updatesAvailable = []
    for object in cmds.ls(rf = True):#check if object is a reference before adding
        objects.append(object)

    for object in objects:
        filePath = cmds.referenceQuery(object, f = True)
        folderPath = os.path.dirname(filePath)
        filesInDir = os.listdir(folderPath)   
        files = getRelevantFiles(filesInDir, filePath)
        for file in files:
            if not isLatest(filePath, file):
                updatesAvailable.append(filePath)

    if not updatesAvailable:
        if cmds.window('alert', exists = True):
            cmds.deleteUI('alert')
        cmds.window('alert', title = "Warning", w = 150, h = 25)
        info = cmds.columnLayout(co = ('both', 10))
        cmds.text("Up to date!")
        cmds.showWindow('alert')
    else:
        if cmds.window('alert', exists = True):
            cmds.deleteUI('alert')
        cmds.window('alert', title = "Warning", w = 150, h = 25)
        info = cmds.columnLayout(co = ('both', 10))
        cmds.text("The following assets have updates available: ")
        for file in updatesAvailable:
            text = cmds.text(str(getFileName(file)))
        cmds.showWindow('alert')


def updateAll():
    #for each asset reference in outliner
    objects = []
    for object in cmds.ls(): #check if object is a reference
        check = cmds.referenceQuery(object, inr = True) #is asset a reference?
        if(check == 1):
            objects.append(object)

    for object in objects:
        filePath = cmds.referenceQuery(object, f = True)
        updatedAsset = returnLatest(filePath)
        latestPath = returnLatestPath(filePath, updatedAsset)
        print(latestPath)
        loadAsset(latestPath, cmds.referenceQuery(object, rfn = True))
    if cmds.window('alert', exists = True):
        cmds.deleteUI('alert')
        cmds.window('alert', title = "Warning", w = 300, h = 25)
        info = cmds.columnLayout(co = ('both', 10))
        cmds.text("Assets updated.")
        cmds.showWindow('alert')

def sceneBuilder():
    if cmds.window('sceneBuilder', exists = True):
        cmds.deleteUI('sceneBuilder')

    cmds.window('sceneBuilder', resizeToFitChildren = True, sizeable = False)
    info = cmds.columnLayout(co = ('both', 10))
    cmds.text("SCENE BUILDER")
    updateButtons = cmds.rowColumnLayout(parent = info, numberOfRows = 1)
    cmds.button(label = 'Check for updates', command = 'checkAllForUpdates()')
    cmds.separator(w = 10, st = 'none')
    cmds.button(label = 'Update asset', command = 'updateSingle()')
    cmds.separator(w = 10, st = 'none')
    versions = cmds.optionMenu()

    cmds.separator(w = 10, st = 'none')
    cmds.button(label = 'Update all', command = 'updateAll()')
    cmds.showWindow('sceneBuilder')

sceneBuilder()

"""
referenceList = cmds.ls(rf = True)

for reference in referenceList:
    path = cmds.referenceQuery(reference, f = True)
    folderPath = os.path.dirname(path)
    fileNameToSplit = os.path.basename(path)
    indexDot = fileNameToSplit.index('.')
    fileName = fileNameToSplit[:indexDot]
    print(fileName)
"""