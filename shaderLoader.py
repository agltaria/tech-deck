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


def GetValidVersionsForObject(object):
    if object == None: return [] # GUARD in case nothing is selected
    
    output = []
    scenePath = cmds.file(q = True, sceneName = True)
    assetName = object[0].replace("mRef_", "")
    searchDirectory = scenePath[:scenePath.rfind(scenesDirectoryName) + len(scenesDirectoryName)] + jsonTemplatePath.replace("<assetName>", assetName)
    
    version = 1
    while os.path.exists(searchDirectory + assetName + "_surface" + ToVersionString(int(version)) + ".json"):
        output.append(version)
        version += 1

    return output



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


def ApplyShadersToObject(object, versionString):
    print(object)
    print(versionString)


# ===========================================================================================================
#   Main thread

StoreSelection()
UI_ShaderLoader()