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


#   Variables
global versionSelector
global selection


#   Functions
def ToVersionString(version):
    if version < 10: return ".v00" + str(version)
    if version < 100: return ".v0" + str(version)
    return ".v" + str(version)


def GetAssetMaterialDirectory(assetName):
    scenePath = cmds.file(q = True, sceneName = True)
    return scenePath[:scenePath.rfind(scenesDirectoryName) + len(scenesDirectoryName)] + jsonTemplatePath.replace("<assetName>", assetName)


def GetAssetJSONFilename(assetName, version):
    return GetAssetMaterialDirectory(assetName) + assetName + "_surface" + ToVersionString(version) + ".json"


def FindSecondOccurrenceOfSubstring(string, substring):
    return string.find(substring, string.find(substring) + 1) # adapted from http://bit.ly/3yK93fP


def GetValidVersionsForObject(object):
    if object == None or len(object) <= 0: return [] # GUARD in case nothing is selected

    output = []
    assetName = object[0].replace("mRef_", "")
    
    version = 1
    while os.path.exists(GetAssetJSONFilename(assetName, version)):
        output.append(version) #TODO: add a check that the compatible model matches
        version += 1

    return output


def GetShaderFromObject(childObject, jsonData):
    shapeName = childObject[FindSecondOccurrenceOfSubstring(childObject, "|") + 1 : childObject.rfind("|")]
    
    for p in jsonData["geometry_shader_pairs"]:
        if p["shape"] == shapeName:
            return p["shader"]

    return ""



#   Methods
def StoreSelection():
    global selection
    selection = cmds.ls(dagObjects = True, objectsOnly = True, shapes = True, long = True, selection = True)


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

    availableVersions = GetValidVersionsForObject(cmds.ls(selection = True))
    global versionSelector
    versionSelector = cmds.optionMenu(label = 'Available Versions:')
    for v in availableVersions:
        versionString = ToVersionString(v)
        cmds.menuItem(label = versionString)

    cmds.button(label = 'Load and Apply Object\'s Shaders', align = 'center', enable = (len(availableVersions) > 0), command = "ApplyShadersToSelection()")
    cmds.separator(h = 30)
    cmds.button(label = 'Update, Load and Apply All Shaders', align = 'center')

    cmds.showWindow('Shader_Loader')


def ApplyShadersToSelection():
    ApplyShadersToObject(selection, cmds.optionMenu(versionSelector, q = True, value = True))
    # cmds.select(selection)


def ApplyShadersToObject(object, versionString):
    assetName = object[0][1 : FindSecondOccurrenceOfSubstring(object[0], "|")].replace("mRef_", "")
    shaderDirectory = GetAssetMaterialDirectory(assetName)

    version = int(versionString[2:len(versionString)])
    jsonFile = open(GetAssetJSONFilename(assetName, version))
    jsonData = json.load(jsonFile)

    for childObject in object:
        jsonShader = GetShaderFromObject(childObject, jsonData)        
        shaderPath = shaderDirectory + jsonShader[jsonShader.rfind("/") + 1 : len(jsonShader)]
        importedShader = cmds.file(shaderPath, 
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
        shader = assetName + ":" + jsonShader[jsonShader.rfind("/") + 1 : jsonShader.rfind(".v")]
        # cmds.select(shader)
        cmds.select(childObject)
        cmds.hyperShade(assign = shader)
        



# ===========================================================================================================
#   Main thread

StoreSelection()
UI_ShaderLoader()