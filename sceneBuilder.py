import os
import os.path
import maya.cmds as cmds

global shotSelected #holds current selected shot
global assetSelected #holds selected asset


#currentProjectDirectory = cmds.workspace(q = True, dir = True)

global animationShotFolder
global layoutShotFolder
global lightingShotFolder

global setToLoad
global setPieceToLoad
global rigToLoad
global propRigToLoad
global charAnimToLoad
global propAnimToLoad

sequenceToLoad = ""
sequenceToLoad2 = ""
global shotToLoad
global shotToLoad2
camToLoad = ""
animationToLoad = ""
isShotSelected = False

isSet = False
isCharRig = False
isPropRig = False
isAnim = False
isCamera = False

def getPublishDirectory():
    publishDirectory = cmds.workspace(q = True, dir = True) + "scenes/publish"
    return publishDirectory


def returnSequences():
    return getPublishDirectory() + "/sequence"

def returnAssets():
    return getPublishDirectory() + "/assets"

def getAssetList(folder):
    return getAllFolders(returnAssets() + folder)
    
def getSequenceList(folder):
    return getAllFolders(returnSequences() + folder)

def selectSequenceFolder():
    global shotSelected
    global animationShotFolder
    global layoutShotFolder
    global lightingShotFolder

    shotSelected = cmds.fileDialog2(fileMode = 3, dir = returnSequences())
    shotSelect = cmds.textField('shotSelect', edit = True, text = str(os.path.basename(shotSelected[0]))) #updates textfield
    animationShotFolder = shotSelected[0] + '/animation/source/'
    layoutShotFolder = shotSelected[0] + '/layout/source/'
    lightingShotFolder = shotSelected[0] + '/lighting/source/' 
    return shotSelected[0]

def loadShot(folder, *args):
    for file in os.listdir():
        if file.endswith(".mb"):
            print(os.path.join(folder, file))
    return

def selectAssetFolder():
    global assetSelected
    assetSelected = cmds.fileDialog2(fileMode = 3, dir = returnAssets())

def checkLayout():
    if(isSet and isCharRig and isPropRig):
        loadLayout = cmds.button("LoadLayout", edit = True, enable = 1, label = "Load layout scene")

def checkAnim():
    return
def loadLayout():
    if(isSet):
        loadSet()
    if(isCharRig):
        loadCharRig()
    if(isPropRig):
        loadPropRig()
    
def loadAnim():
    if(isSet):
        loadSet()
    if(isCharRig):
        loadCharRig()
    if(isPropRig):
        loadPropRig()
    if(isCamera):
        loadCamera()

def loadLighting():
    if(isSet):
        loadSet()
    if(isCamera):
        loadCamera()
    if(isAnim):
        loadAnimation()

def loadLayoutOld():
    global layoutShotFolder
    global shotSelected

    files = []
    files2 = []
    alembic = ""
    latestFile = ""
    for file in os.listdir(layoutShotFolder):
        if file.endswith(".mb"):
            files.append(file)
            latestFile = file
    for i in files:
        if(isLatest(i, latestFile)):
            latestFile = i

    alembicPath = shotSelected[0] + "/layout/cache/alembic/"
    for file in os.listdir(alembicPath):
        if file.endswith(".abc"):
            files2.append(file)
            alembic = file
    for i in files2:
        if(isLatest(i, alembic)):
            alembic = i
    cmds.file(alembicPath + alembic, reference = True)
    path = layoutShotFolder + latestFile
    cmds.file(path, reference = True)

def loadAnimationOld():
    global animationShotFolder
    global shotSelected
    files = []
    files2 = []
    latestFile = ""
    alembic = ""
    for file in os.listdir(animationShotFolder):
        if file.endswith(".mb"):
            files.append(file)
            latestFile = file
    for i in files:
        if(isLatest(i, latestFile)):
            latestFile = i

    path = animationShotFolder + latestFile
    alembicPath = shotSelected[0] + "/animation/cache/alembic/"
    for file in os.listdir(alembicPath):
        if file.endswith(".abc"):
            files2.append(file)
            alembic = file
    for i in files2:
        if(isLatest(i, alembic)):
            alembic = i
    cmds.file(alembicPath + alembic, reference = True)
    cmds.file(path, reference = True)

def loadLightingOld():
    global lightingShotFolder
    global shotSelected
    files = []
    files2 = []
    latestFile = ""
    alembic = ""
    for file in os.listdir(lightingShotFolder):
        if file.endswith(".mb"):
            files.append(file)
            latestFile = file
    for i in files:
        if(isLatest(i, latestFile)):
            latestFile = i

    cmds.file(lightingShotFolder + latestFile, reference = True)

def loadSingleAsset():
    files = []
    latestFile = ""
    assetPath = ""
    global assetSelected
    if("/set/" in assetSelected):
        assetPath = assetSelected + "/model"
        for file in os.listdir(assetPath):
            if file.endswith(".mb"):
                files.append(file)
                latestFile = file
        for i in files:
            if(isLatest(i, latestFile)):
                latestFile = i
    elif("/setPiece/" in assetSelected):
        assetPath = assetSelected + "/model/source/"
        for file in os.listdir(assetPath):
            if file.endswith(".mb"):
                files.append(file)
                latestFile = file
        for i in files:
            if(isLatest(i, latestFile)):
                latestFile = i
    
    cmds.file(assetPath, reference = True)

def loadAsset(newRefPath, currentRefNode):
    cmds.file(newRefPath, loadReference = currentRefNode)
    return

def createRef(filePath):
    cmds.file(filePath, reference = True)

def isLatest(currentFile, directoryFile): #compare current file version with files in directory
    if readFileVersion(currentFile) >= readFileVersion(directoryFile):
        return True
    else:
        return False

#read version number
def readFileVersion(fileName):
    fileVer = fileName.split('.')[1]
    verNum = int(fileVer[-3:])
    return verNum

def getFileName(file):
    name = cmds.referenceQuery(file, f = True, shortName = True)   
    return name

def getAllFolders(dir): #get all folders in a directory
     return [folders for folders in os.listdir(dir) if os.path.isdir(os.path.join(dir, folders))]

def getRelevantFiles(filesInDir, selectedFile): #gets all file versions and filters out any other files that may be in the main folder
    relevantFiles = []
    fileNameToSplit = os.path.basename(selectedFile)
    indexDot = fileNameToSplit.index('.')
    fileName = fileNameToSplit[:indexDot]
    for file in filesInDir:
        if fileName in file:
            relevantFiles.append(file)
    return relevantFiles

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



def loadSet():
    files = []
    latestFile = ""
    for file in os.listdir(str(setToLoad)):
        if file.endswith(".mb"):
            files.append(file)
            latestFile = file
    for i in files:
        if(isLatest(i, latestFile)):
            latestFile = i
    createRef(setToLoad + "/" + latestFile)

def loadSetPiece():
    files = []
    latestFile = ""
    for file in os.listdir(str(setPieceToLoad)):
        if file.endswith(".mb"):
            files.append(file)
            latestFile = file
    for i in files:
        if(isLatest(i, latestFile)):
            latestFile = i
    createRef(setPieceToLoad + "/" + latestFile)

def loadCharRig():
    files = []
    latestFile = ""
    for file in os.listdir(str(rigToLoad)):
        if file.endswith(".mb"):
            files.append(file)
            latestFile = file
    for i in files:
        if(isLatest(i, latestFile)):
            latestFile = i
    createRef(rigToLoad + "/" + latestFile)

def loadPropRig():
    files = []
    latestFile = ""
    for file in os.listdir(str(propRigToLoad)):
        if file.endswith(".mb"):
            files.append(file)
            latestFile = file
    for i in files:
        if(isLatest(i, latestFile)):
            latestFile = i
    createRef(propRigToLoad + "/" + latestFile)

def loadAnimation():
    files = []
    latestFile = ""
    for file in os.listdir(str(animationToLoad)):
        if file.endswith(".abc"):
            files.append(file)
            latestFile = file
    for i in files:
        if(isLatest(i, latestFile)):
            latestFile = i
    createRef(animationToLoad + "/" + latestFile)

def loadCamera():
    files = []
    latestFile = ""
    for file in os.listdir(str(camToLoad)):
        if file.endswith(".abc"):
            files.append(file)
            latestFile = file
    for i in files:
        if(isLatest(i, latestFile)):
            latestFile = i
    createRef(camToLoad + "/" + latestFile)

def changeSet(value):
    global setToLoad
    global isSet
    setToLoad = returnAssets() + "/set/" + value + "/model"
    if(value != ""):
        loadSet = cmds.button("LoadSet", edit = True, enable = 1)
        isSet = True
    else:
        loadSet = cmds.button("LoadSet", edit = True, enable = 0)
        isSet = False
    return setToLoad

def changeSetPiece(value):
    global setPieceToLoad
    setPieceToLoad = returnAssets() + "/setPiece/" + value + "/model/source"
    if(value != ""):
        loadSetPiece = cmds.button("LoadSetPieceButton", edit = True, enable = 1)
    else:
        loadSetPiece = cmds.button("LoadSetPieceButton", edit = True, enable = 0)
    return

def changeCharRig(value):
    global rigToLoad
    global isCharRig
    rigToLoad = returnAssets() + "/character/" + value + "/rig"
    if(value != ""):
        loadRig = cmds.button("LoadCharRig", edit = True, enable = 1)
        isCharRig = True
    else:
        loadRig = cmds.button("LoadCharRig", edit = True, enable = 0)
        isCharRig = False
    return

def changePropRig(value):
    global propRigToLoad
    global isPropRig
    propRigToLoad = returnAssets() + "/prop/" + value + "/rig/source"
    if(value != ""):
        loadPropRig = cmds.button("LoadPropRig", edit = True, enable = 1)
        isPropRig = True
    else:
        loadPropRig = cmds.button("LoadPropRig", edit = True, enable = 0)
        isPropRig = False
    return

def changeCharAnim(value):
    global charAnimToLoad
    charAnimToLoad = returnAssets() + "/"

def changeSequence(value):
    global sequenceToLoad
    global isCamera
    sequenceToLoad = returnSequences() + "/" + value
    if(value != ""):
        availableShots = cmds.optionMenu("availableShots", cc = changeShot, enable = 1, edit = True)
        isCamera = True
        setShots()
    else:
        availableShots = cmds.optionMenu("availableShots", enable = 0, edit = True, q = True, itemListLong = True)
        if(availableShots):
            cmds.deleteUI(availableShots)
        availableShots = cmds.optionMenu("availableShots", cc = changeShot, enable = 0, parent = "loadShot")
        isCamera = False
    return

def changeSequence2(value):
    global sequenceToLoad2
    global isAnim
    sequenceToLoad2 = returnSequences() + "/" + value
    if(value != ""):
        availableShots2 = cmds.optionMenu("availableShots2", cc = changeShot2, enable = 1, edit = True)
        setShots2()
        isAnim = True
    else:
        availableShots2 = cmds.optionMenu("availableShots2", enable = 0, edit = True, q = True, itemListLong = True)
        if(availableShots2):
            cmds.deleteUI(availableShots2)
        availableShots2 = cmds.optionMenu("availableShots2", cc = changeShot2, enable = 0, parent = "loadShot2")
        isAnim = False
    return

def setShots():
    cmds.menuItem(label = "")
    for folder in getAllFolders(sequenceToLoad):   
        cmds.menuItem(folder, label = folder, parent = "availableShots")

def setShots2():
    cmds.menuItem(label = "")
    for folder in getAllFolders(sequenceToLoad2):   
        cmds.menuItem(folder, label = folder, parent = "availableShots2")

def changeShot(value):
    global shotToLoad
    global camToLoad
    shotToLoad = sequenceToLoad + "/" + value
    animationToLoad = shotToLoad + "/animation/cache/alembic"
    camToLoad = shotToLoad + "/layout/cache/alembic"
    if(value != ""):
        loadCamButton = cmds.button("LoadCamera", edit = True, enable = 1)
        isCamera = True
    else:
        loadCamButton = cmds.button("LoadCamera", edit = True, enable = 0)
        isCamera = False
    
    return

def changeShot2(value):
    global shotToLoad2
    global animationToLoad
    shotToLoad2 = sequenceToLoad2 + "/" + value
    animationToLoad = shotToLoad2 + "/animation/cache/alembic"
    if(value != ""):
        loadAnimButton = cmds.button("LoadAnimation", edit = True, enable = 1)
        isAnim = True
    else:
        loadAnimButton = cmds.button("LoadAnimation", edit = True, enable = 0)
        isAnim = False
    return
    
def sceneBuilder():
    if cmds.window('sceneBuilder', exists = True):
        cmds.deleteUI('sceneBuilder')

    cmds.window('sceneBuilder', resizeToFitChildren = True, sizeable = False)
    info = cmds.columnLayout(co = ('both', 10))
    cmds.text("SCENE BUILDER")
    cmds.text("Please ensure your project is set to the correct directory.")

    cmds.separator(h = 10)
    cmds.text("Load layout")
    
    loadSet = cmds.rowColumnLayout(parent = info, numberOfRows = 1)
    cmds.text("Set:")
    availableSets = cmds.optionMenu(cc = changeSet)
    cmds.menuItem(label = "")
    for folder in getAssetList("/set"):
        cmds.menuItem(folder, label = folder)
    cmds.separator(w = 10, st = 'none')
    cmds.button("LoadSet", command = 'loadSet()', label = "Load set", enable = 0)
    
    loadRig = cmds.rowColumnLayout(parent = info, numberOfRows = 1)
    cmds.text("Character Rig: ")
    availableCharRigs = cmds.optionMenu(cc = changeCharRig)
    cmds.menuItem(label = "")
    for folder in getAssetList("/character"):   
        cmds.menuItem(folder, label = folder)
    cmds.separator(w = 10, st = 'none')
    cmds.button("LoadCharRig", command = 'loadCharRig()', label = "Load character rig", enable = 0)

    loadPropRig = cmds.rowColumnLayout(parent = info, numberOfRows = 1)
    cmds.text("Prop Rig: ")
    availablePropRigs = cmds.optionMenu(cc = changePropRig)
    cmds.menuItem(label = "")
    for folder in getAssetList("/prop"):   
        cmds.menuItem(folder, label = folder)
    cmds.separator(w = 10, st = 'none')
    cmds.button("LoadPropRig", command = 'loadPropRig()', label = "Load prop rig", enable = 0)

    cmds.separator(h = 10)
    cmds.separator(parent = info, w = 100)
    cmds.separator(h = 10)

    cmds.text(parent = info, label = "Load animation")
    seqSelect = cmds.rowColumnLayout(parent = info, numberOfRows = 1)
    cmds.text("Sequence: ")
    availableSequences = cmds.optionMenu("availableSequences", cc = changeSequence)
    cmds.menuItem(label = "")
    for folder in getAllFolders(returnSequences()):   
        cmds.menuItem(label = folder)
    
    loadShot = cmds.rowColumnLayout("loadShot", parent = info, numberOfRows = 1)
    cmds.text("Shot: ")
    availableShots = cmds.optionMenu("availableShots", cc = changeShot, enable = 0)
    cmds.menuItem("")
    loadShotButtons = cmds.rowColumnLayout("loadShotButtons", parent = info, numberOfRows = 1)
    loadCamButton = cmds.button("LoadCamera", command = 'loadCamera()', enable = 0, label = "Load camera")
    cmds.separator(w = 10, st = 'none')
    
    cmds.separator(h = 10)
    cmds.separator(parent = info, w = 100)
    cmds.separator(h = 10)

    cmds.text(parent = info, label = "Load lighting")
    
    
    seqSelect2 = cmds.rowColumnLayout("seqSelect2", parent = info, numberOfRows = 1)
    cmds.text(label = "Sequence: ")
    availableSequences = cmds.optionMenu("availableSequences2", cc = changeSequence2)
    cmds.menuItem(label = "")
    for folder in getAllFolders(returnSequences()):   
        cmds.menuItem(label = folder)
    loadShot = cmds.rowColumnLayout("loadShot2", parent = info, numberOfRows = 1)
    cmds.text("Shot: ")  
    availableShots2 = cmds.optionMenu("availableShots2", cc = changeShot2, enable = 0)
    cmds.menuItem("")
    loadAnim = cmds.rowColumnLayout("loadAnim", parent = info, numberOfRows = 1)
    loadAnimButton = cmds.button("LoadAnimation", command = 'loadAnimation()', enable = 0, label = "Load animation")

    cmds.separator(h = 10)
    cmds.separator(parent = info, w = 100)
    cmds.separator(h = 10)

    loadButtons = cmds.rowColumnLayout("loadButtons", parent = info, numberOfRows = 1)
    loadLayout = cmds.button("LoadLayout", command = 'loadLayout()', enable = 1, label = "Load layout scene")
    cmds.separator(w = 10, st = 'none')
    loadAnim = cmds.button("LoadAnimation", command = 'loadAnim()', enable = 1, label = "Load animation scene")
    cmds.separator(w = 10, st = 'none')
    loadLighting = cmds.button("LoadLighting", command = 'loadLighting()', enable = 1, label = "Load lighting scene")
    
    cmds.separator(h = 10)
    cmds.separator(parent = info, w = 100)
    cmds.separator(h = 10)

    cmds.text(parent = info, label = "Load a setpiece")
    loadSetPiece = cmds.rowColumnLayout("loadSetPiece", parent = info, numberOfRows = 1)
    cmds.text("Setpiece: ")
    availableSetPieces = cmds.optionMenu(cc = changeSetPiece)
    cmds.menuItem(label = "")
    for folder in getAssetList("/setPiece"):   
        cmds.menuItem(folder, label = folder)
    cmds.separator(w = 10, st = 'none')
    loadSetPieceButton = cmds.button("LoadSetPieceButton", command = 'loadSetPiece()', enable = 0, label = "Load setpiece")

    cmds.separator(h = 10)
    cmds.separator(parent = info, w = 100)
    cmds.separator(h = 10)

    cmds.text(parent = info, label = "Update assets")
    updateButtons = cmds.rowColumnLayout(parent = info, numberOfRows = 1)
    cmds.button(label = 'Check for updates', command = 'checkAllForUpdates()')
    cmds.separator(w = 10, st = 'none')
    cmds.button(label = 'Update asset', command = 'updateSingle()')
    cmds.separator(w = 10, st = 'none')
    cmds.separator(w = 10, st = 'none')
    cmds.button(label = 'Update all', command = 'updateAll()')



   
    cmds.showWindow('sceneBuilder')



sceneBuilder()
#print(returnSequences())
"""
referenceList = cmds.ls(rf = True)

for reference in referenceList:
    path = cmds.referenceQuery(reference, f = True)
    folderPath = os.path.dirname(path)
    fileNameToSplit = os.path.basename(path)
    indexDot = fileNameToSplit.index('.')
    fileName = fileNameToSplit[:indexDot]
    print(fileName)

cmds.text("Select shot to load")
    cmds.rowColumnLayout(parent = info, numberOfRows = 1)
    shotSelect = cmds.textField('shotSelect', width = 200, editable = False)
    cmds.button(label = 'Select', command = 'selectSequenceFolder()')
    cmds.separator(h = 20)

    
    #for folder in getAllFolders():
    loadButtons = cmds.rowColumnLayout(parent = info, numberOfRows = 1)
    cmds.button(label = 'Load layout', command = 'loadLayout()')
    cmds.separator(w = 10, st = 'none')
    cmds.button(label = 'Load animation', command = 'loadAnimation()')
    cmds.separator(w = 10, st = 'none')
    cmds.button(label = 'Load lighting', command = 'loadLighting()')


    cmds.separator(parent = info, h = 10)
    cmds.separator(parent = info, w = 100)
    cmds.separator(parent = info, h = 10)

 cmds.text(parent = info, label = "Load an asset")
    assetSelect = cmds.rowColumnLayout(parent = info, numberOfRows = 1)
    setSelect = cmds.textField('setSelect', width = 200, editable = False)
    cmds.button(label = 'Select', command = 'selectAssetFolder()')
    cmds.separator(w = 10, st = 'none')
    cmds.button(label = 'Load', command = 'loadSingleAsset()')
    cmds.separator(h = 20)

        loadCharAnim = cmds.rowColumnLayout(parent = info, numberOfRows = 1)
    cmds.text("Character animation: ")
    availableCharRigs = cmds.optionMenu(cc = changeCharAnim)
    cmds.menuItem(label = "")
    for folder in getAssetList("/character"):   
        cmds.menuItem(folder, label = folder)
    cmds.separator(w = 10, st = 'none')
    cmds.button("Load", command = 'loadCharAnim()')

    loadPropAnim = cmds.rowColumnLayout(parent = info, numberOfRows = 1)
    cmds.text("Prop animation: ")
    availablePropRigs = cmds.optionMenu(cc = changePropAnim)
    cmds.menuItem(label = "")
    for folder in getAssetList("/prop"):   
        cmds.menuItem(folder, label = folder)
    cmds.separator(w = 10, st = 'none')
    cmds.button("Load", command = 'loadPropAnim()')

"""