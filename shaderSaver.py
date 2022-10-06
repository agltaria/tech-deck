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

    # adapted from http://bit.ly/3CtWiqT and http://bit.ly/3e8rfsc
    return scenePath[:scenePath.rfind('/') + 1].replace(wipDirectoryName, publishDirectoryName) #this will need to be changed if cmds.file() doesn't automatically create missing directories


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
    transformSelected = False


    selection = cmds.ls(dagObjects = True, objectsOnly = True, shapes = True, selection = True) # adapted from http://bit.ly/3fIe165
    if (selection == None): return
    if (len(selection) > 1): transformSelected = True #if there's issues with transformSelected, make this an if-else
    print(transformSelected)

    for s in selection:
        SaveShaderOnObject(s)


def SaveShaderOnObject(object):
    # adapted from http://bit.ly/3fIe165
    shadingGroups = cmds.listConnections(object, type = 'shadingEngine')
    if (shadingGroups == None): return
    shaders = cmds.ls(cmds.listConnections(shadingGroups), materials = True)

    destinationDirectory = SetUpPublishedDirectory()
    for s in shaders:
        # this needs version incrementing. Should be no file-overwriting!
        cmds.file(destinationDirectory + s, options = "v=0;p=17;f=0", type = "mayaBinary", preserveReferences = True, exportSelected = True)


# ===========================================================================================================
#   Main thread

UI_ShaderSaver()