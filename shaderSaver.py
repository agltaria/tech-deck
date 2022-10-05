# TD A3 Shader Saver - 13892385
# 
# Select an object, and this tool will save all the shader relationships. 
# Shader Loader will load them in another scene
# ============================================================================================================

import maya.cmds as cmds

#   Properties
global setPieceDirectoryName
setPieceDirectorName = "setPiece"

global wipDirectoryName
wipDirectoryName = "wip"

global publishDirectoryName
publishDirectoryName = "publish"


#   Variables



#   Functions
def SetUpPublishedDirectory():
    scenePath = cmds.file(q = True, sceneName = True) # adapted from http://bit.ly/3ygRbJ8
    # workingDirectory = scenePath.replace()
    # setPieceDirectory = setPieceDirectorName + "/"
    
    # # adapted from http://bit.ly/3C6lC61 and http://bit.ly/3e8rfsc
    # return scenePath[:(scenePath.find(setPieceDirectory) + len(setPieceDirectory))] 

    return scenePath.replace(wipDirectoryName, publishDirectoryName)


#   Methods
def UI_ShaderSaver():
    if cmds.window('Shader_Saver', exists = True): cmds.deleteUI('Shader_Saver')

    cmds.window('Shader_Saver', widthHeight = (200, 240), sizeable = False, resizeToFitChildren = True)
    cmds.columnLayout(columnAttach = ('both', 5), rowSpacing = 10, columnWidth = 220)

    cmds.text(' ')
    cmds.text('SHADER SAVER')
    cmds.text(' ')
    cmds.text('Saves & publishes all shaders and')
    cmds.text('shader-geometry references to be loaded')
    cmds.text('by Shader Loader in a Lighting scene')
    cmds.separator(h = 30)

    cmds.button(label = 'Save Object\'s Shaders', align = 'center', command = 'SaveObjectShaders()')
    cmds.button(label = 'Save All Shaders', align = 'center')

    cmds.showWindow('Shader_Saver')


def SaveObjectShaders():
    selectedShape = cmds.ls(dagObjects = True, objectsOnly = True, shapes = True, selection = True)

    SaveShaderOnObject(selectedShape)


def SaveShaderOnObject(object):
    # adapted from http://bit.ly/3fIe165
    shadingGroups = cmds.listConnections(object, type = 'shadingEngine')
    shaders = cmds.ls(cmds.listConnections(shadingGroups), materials = True)

    destinationDirectory = SetUpPublishedDirectory()
    print(destinationDirectory)
    # foreach in shaders
    


# ===========================================================================================================
#   Main thread

UI_ShaderSaver()