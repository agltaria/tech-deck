# TD A3 Shader Loader - 13892385
# 
# Select an object, and this tool will load all its shader relationships. 
# RELIES ON Shader Saver SAVING THEM IN PREVIOUS SCENE
# ============================================================================================================

import maya.cmds as cmds
import json
import os

#   Properties
global targetObjectSubstring
targetObjectSubstring = "mRef_"

global scenesDirectoryName
scenesDirectoryName = "/scenes"

global jsonTemplatePath
jsonTemplatePath = "/publish/assets/setPiece/<assetName>/surfacing/material/"

global versionSearchLimit # number of JSON version 'searches' run if a given version isn't found
versionSearchLimit = 100

global shapeDepthFromRoot # Outliner 'depth' of the shapes
shapeDepthFromRoot = 3

global setGeoName # name of the 'setGeo' parent folder
setGeoName = "setGeo"


#   Variables
global versionSelectorItems
versionSelectorItems = []

global versionSelector
global applyObjectButton

global selection
global availableVersions


#   Functions
def ToVersionString(version):
    if version < 10: return ".v00" + str(version)
    if version < 100: return ".v0" + str(version)
    return ".v" + str(version)


def GetAssetMaterialDirectory(assetName):
    scenePath = cmds.file(q = True, sceneName = True)
    output = scenePath[:scenePath.rfind(scenesDirectoryName) + len(scenesDirectoryName)] + jsonTemplatePath.replace("<assetName>", assetName)
    return output


def GetAssetJSONFilename(assetName, version):
    return GetAssetMaterialDirectory(assetName) + assetName + "_surface" + ToVersionString(version) + ".json"


def FindNthOccurrenceOfSubstring(string, substring, n): #adapted from http://bit.ly/3VIfdXA
    start = string.find(substring)

    while start >= 0 and n > 1:
        start = string.find(substring, start + len(substring))
        n -= 1

    return start


def GetValidVersionsForObject(object):
    if object == None or len(object) <= 0: return [] # GUARD in case nothing is selected

    output = []
    assetName = object[0][object[0].rfind(targetObjectSubstring) + len(targetObjectSubstring) : len(object[0])]
    
    version = 1
    while os.path.exists(GetAssetJSONFilename(assetName, version)) or version <= versionSearchLimit:       
        if os.path.exists(GetAssetJSONFilename(assetName, version)):
            referencedModelPath = cmds.referenceQuery(object, filename = True)
            referencedModelRelative = referencedModelPath[referencedModelPath.find("/publish") : len(referencedModelPath)]
            jsonFile = open(GetAssetJSONFilename(assetName, version))
            jsonData = json.load(jsonFile)
            compatibleModel = jsonData["compatible_model"]

            if (referencedModelRelative == compatibleModel):
                output.append(version) 
            else:
                print("Shader Loader | Incompatible model! referenced model: " + referencedModelRelative + ", required model: " + compatibleModel)

        version += 1

    return output


def GetShaderFromObject(childObject, jsonData):
    shapeName = childObject[childObject.rfind(":mRef_") + 1 : len(childObject)].replace("Shape", "")
    
    for p in jsonData["geometry_shader_pairs"]:
        if p["shape"] == shapeName:
            return p["shader"]

    return ""



#   Methods
def UI_ShaderLoader():
    if cmds.window('Shader_Loader', exists = True): cmds.deleteUI('Shader_Loader')

    cmds.window('Shader_Loader', widthHeight = (200, 310), sizeable = False, resizeToFitChildren = True)
    cmds.columnLayout(columnAttach = ('both', 5), rowSpacing = 10, columnWidth = 220)

    cmds.text(' ')
    cmds.text('SHADER LOADER')
    cmds.text(' ')
    cmds.text('Loads & applies all shaders and')
    cmds.text('shader-geometry references saved by')
    cmds.text('Shader Saver in a Surfacing scene')
    cmds.separator(h = 30)

    global availableVersions
    availableVersions = GetValidVersionsForObject(cmds.ls(selection = True))
    global versionSelector
    versionSelector = cmds.optionMenu(label = 'Available Versions:')
    global versionSelectorItems
    for v in availableVersions:
        versionString = ToVersionString(v)
        versionSelectorItems.append(cmds.menuItem(label = versionString))

    global applyObjectButton
    applyObjectButton = cmds.button(label = 'Load and Apply Object\'s Shaders', align = 'center', enable = (len(availableVersions) > 0), command = "ApplyShadersToSelection()")
    cmds.separator(h = 30)
    cmds.button(label = 'Update, Load and Apply All Shaders', align = 'center', command = 'ApplyAllShaders()')

    cmds.showWindow('Shader_Loader')

    cmds.scriptJob(event = ["SelectionChanged", SJ_UpdateLoaderUI], parent = "Shader_Loader", replacePrevious = True)


def SJ_UpdateLoaderUI():
    global availableVersions
    oldAvailableVersions = availableVersions
    availableVersions = GetValidVersionsForObject(cmds.ls(selection = True))

    if (availableVersions != oldAvailableVersions):
        global versionSelectorItems
        if len(versionSelectorItems) > 0: cmds.deleteUI(versionSelectorItems, menuItem = True)

        versionSelectorItems = []

        for v in availableVersions:
            versionString = ToVersionString(v)
            versionSelectorItems.append(cmds.menuItem(versionSelector, label = versionString))

    cmds.button(applyObjectButton, edit = True, enable = (len(availableVersions) > 0))


def ApplyShadersToSelection():
    StoreSelection()
    ApplyShadersToObject([selection[0][:FindNthOccurrenceOfSubstring(selection[0], "|", 3)]], cmds.optionMenu(versionSelector, q = True, value = True))
    cmds.select(selection)


def ApplyAllShaders():
    setObjects = cmds.listRelatives(setGeoName, children = True, fullPath = True)
    
    for o in setObjects:
        validVersions = GetValidVersionsForObject([o])

        if len(validVersions) > 0:
            ApplyShadersToObject([o], ToVersionString(validVersions[len(validVersions) - 1]))


def StoreSelection():
    global selection
    selection = cmds.ls(dagObjects = True, objectsOnly = True, shapes = True, long = True, selection = True)


def ApplyShadersToObject(object, versionString):
    assetName = object[0][object[0].rfind(targetObjectSubstring) + len(targetObjectSubstring) : len(object[0])].replace("Shape", "")
    
    shaderDirectory = GetAssetMaterialDirectory(assetName)

    version = int(versionString[2:len(versionString)])
    jsonFile = open(GetAssetJSONFilename(assetName, version))
    jsonData = json.load(jsonFile)

    importedShaders = []
    children = cmds.listRelatives(object, children = True, fullPath = True)
    for childObject in children:
        jsonShader = GetShaderFromObject(childObject, jsonData) 

        if (importedShaders.__contains__(jsonShader) == False):
            shaderPath = shaderDirectory + jsonShader[jsonShader.rfind("/") + 1 : len(jsonShader)]
            print(jsonShader)
            print("Attempting to open file: " + shaderPath)
            importedShader = cmds.file(
                shaderPath, 
                i = True, 
                type = "mayaBinary", 
                ignoreVersion = True, 
                renameAll = True, 
                mergeNamespacesOnClash = True,
                namespace = assetName,
                options = "v=0;p=17;f=0",
                preserveReferences = True,
                importTimeRange = "combine"
            )

            importedShaders.append(jsonShader)

        shader = assetName + ":" + jsonShader[jsonShader.rfind("/") + 1 : jsonShader.rfind(".v")]
        cmds.select(childObject)
        cmds.hyperShade(assign = shader)
        
        

# ===========================================================================================================
#   Main thread

UI_ShaderLoader()