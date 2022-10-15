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



#   Functions
def ToVersionString(version):
    if version < 10: return ".v00" + str(version)
    if version < 100: return ".v0" + str(version)
    return ".v" + str(version)


def GetValidVersionsForObject(object):
    if object == None: return [] # GUARD in case nothing is selected
    
    output = []
    scenePath = cmds.file(q = True, sceneName = True)
    searchDirectory = scenePath[:scenePath.rfind(scenesDirectoryName) + len(scenesDirectoryName)] + jsonTemplatePath.replace("<assetName>", object[0].replace("mRef_", ""))
    
    

    return output



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

    availableVersions = GetValidVersionsForObject(cmds.ls(selection = True))
    cmds.optionMenu(label = 'Available Versions:')
    for v in availableVersions:
        cmds.menuItem(label = ToVersionString(v[1:len(v)]))

    cmds.button(label = 'Load and Apply Object\'s Shaders', align = 'center')
    cmds.separator(h = 30)
    cmds.button(label = 'Update, Load and Apply All Shaders', align = 'center')

    cmds.showWindow('Shader_Loader')


# ===========================================================================================================
#   Main thread

UI_ShaderLoader()