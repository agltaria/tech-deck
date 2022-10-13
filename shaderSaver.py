# TD A3 Shader Saver - 13892385
# 
# Select an object, and this tool will save all the shader relationships. 
# Shader Loader will load them in another scene
# ============================================================================================================

import maya.cmds as cmds
import json
import os

#   Properties
global setPieceDirectoryName
setPieceDirectorName = "setPiece"

global wipDirectoryName
wipDirectoryName = "wip"

global publishDirectoryName
publishDirectoryName = "publish"


#   Variables
global currentVersion


#   Functions
def GetPublishDirectory():
    scenePath = cmds.file(q = True, sceneName = True) # adapted from http://bit.ly/3ygRbJ8

    # adapted from http://bit.ly/3CtWiqT and http://bit.ly/3e8rfsc
    return scenePath[:scenePath.rfind('/') + 1].replace(wipDirectoryName, publishDirectoryName) + "material/"

    # apparently there's supposed to be a '/source' folder alongside material.....what's it for???


def GetVersionString():
    global currentVersion
    if currentVersion < 10: return ".v00" + str(currentVersion)
    if currentVersion < 100: return ".v0" + str(currentVersion)
    return ".v" + str(currentVersion)


def GetSceneName():
    return os.path.splitext(cmds.file(q = True, sceneName = True, shortName = True))[0] # adapted from http://bit.ly/3ygRbJ8


#   Methods
def PreloadVersion():
    global currentVersion
    currentVersion = 1


def UI_ShaderSaver():
    if cmds.window('Shader_Saver', exists = True): cmds.deleteUI('Shader_Saver')

    cmds.window('Shader_Saver', widthHeight = (200, 210), sizeable = False, resizeToFitChildren = True)
    cmds.columnLayout(columnAttach = ('both', 5), rowSpacing = 10, columnWidth = 220)

    cmds.text(' ')
    cmds.text('SHADER SAVER')
    cmds.text(' ')
    cmds.text('Saves & publishes all shaders and')
    cmds.text('shader-geometry references to be loaded')
    cmds.text('by Shader Loader in a Lighting scene')
    cmds.separator(h = 30)

    cmds.button(label = 'Save Object\'s Shaders', align = 'center', command = 'SaveObjectShaders()')

    cmds.showWindow('Shader_Saver')


def SaveObjectShaders():       
    selection = cmds.ls(dagObjects = True, objectsOnly = True, shapes = True, selection = True, long = True) # adapted from http://bit.ly/3fIe165
    
    if (selection == None): return
    if (len(selection) <= 1): 
        print("No group selected! Returning...")

    list = []
    id = 1001
    for s in selection:
        shader = SaveShaderOnObject(s)

        dictionary = {
            "ID": id,
            "shape": s,
            "shader": shader
        }
        list.append(dictionary)

        id += 1

    jsonOutput = {
        "geometry_shader_pairs": list,
        "created_with": GetSceneName()
    }

    # adapted from http://bit.ly/3EDPvgX
    with open(GetPublishDirectory() + GetSceneName() + GetVersionString() + ".json", "w", encoding = "utf-8") as writtenFile:
        writtenFile.write(json.dumps(jsonOutput, ensure_ascii = False, indent = 4))

    global currentVersion
    currentVersion += 1

    cmds.select(selection)


def SaveShaderOnObject(object):
    # adapted from http://bit.ly/3fIe165
    shadingGroups = cmds.listConnections(object, type = 'shadingEngine')
    if (shadingGroups == None): return

    shaders = cmds.ls(cmds.listConnections(shadingGroups), materials = True)
    version = GetVersionString()

    destinationDirectory = GetPublishDirectory()
    for s in shaders:
        # this needs version incrementing. Should be no file-overwriting!
        cmds.select(s)
        return cmds.file(destinationDirectory + s + version, options = "v=0;p=17;f=0", type = "mayaBinary", preserveReferences = True, exportSelected = True, saveReferencesUnloaded = True)



# ===========================================================================================================
#   Main thread

PreloadVersion()
UI_ShaderSaver()