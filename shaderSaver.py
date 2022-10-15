# TD A3 Shader Saver - 13892385
# 
# Select an object, and this tool will save all the shader relationships. 
# Shader Loader will load them in another scene
# ============================================================================================================

from select import select
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

global targetObjectSubstring
targetObjectSubstring = "mRef_"


#   Variables
global currentVersion


#   Functions
def GetPublishDirectory(destination):
    scenePath = cmds.file(q = True, sceneName = True) # adapted from http://bit.ly/3ygRbJ8

    # adapted from http://bit.ly/3CtWiqT and http://bit.ly/3e8rfsc
    return scenePath[:scenePath.rfind('/') + 1].replace(wipDirectoryName, publishDirectoryName) + destination

    # apparently there's supposed to be a '/source' folder alongside material.....that's for publishing the wip surfacing scene


def ToVersionString(version):
    if version < 10: return ".v00" + str(version)
    if version < 100: return ".v0" + str(version)
    return ".v" + str(version)


def GetSceneName():
    return os.path.splitext(cmds.file(q = True, sceneName = True, shortName = True))[0] # adapted from http://bit.ly/3ygRbJ8


def FindSecondOccurrenceOfSubstring(string, substring):
    return string.find(substring, string.find(substring) + 1) # adapted from http://bit.ly/3yK93fP



#   Methods
def PreloadVersion():
    sceneName = GetSceneName()
    versionString = sceneName[sceneName.rfind('.v') + 2 : len(sceneName)] # adapted from http://bit.ly/3EFPd97

    global currentVersion
    currentVersion = int(versionString)

    print("Shader Saver | Current Version is " + ToVersionString(currentVersion))


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
    allShapes = cmds.ls(dagObjects = True, objectsOnly = True, shapes = True, long = True)
    
    targetParent = None
    for s in allShapes:
        if s.__contains__(targetObjectSubstring):
            targetParent = s[1 : FindSecondOccurrenceOfSubstring(s, "|mRef")]
            break
    
    print(targetParent)
    selection = cmds.listRelatives(targetParent, children = True)
    print(selection)
    cmds.select(selection)

    if len(selection) < 1 or selection == None: 
        print("Shader Saver | No valid object found! Returning...")
        return

    shaderPairlist = []
    id = 1001
    for s in selection:
        shader = SaveShaderOnObject(cmds.listRelatives(s, children = True))

        singlePair = {
            "ID": id,
            "shape": s,
            "shader": shader[shader.rfind("/" + publishDirectoryName) : len(shader)]
        }
        shaderPairlist.append(singlePair)

        id += 1

    # need to include source model version to enable dependency checks in Loader
    referencedModelPath = cmds.referenceQuery(selection[0], filename = True)
    compatibleModel = referencedModelPath[referencedModelPath.rfind("/" + publishDirectoryName) : len(referencedModelPath)]

    jsonOutput = {
        "geometry_shader_pairs": shaderPairlist,
        "created_with": GetSceneName(),
        "compatible_model" : compatibleModel
    }

    # adapted from http://bit.ly/3EDPvgX
    global currentVersion
    jsonFilepath = GetPublishDirectory("/material/") + GetSceneName() + ".json"
    with open(jsonFilepath, "w", encoding = "utf-8") as writtenFile:
        writtenFile.write(json.dumps(jsonOutput, ensure_ascii = False, indent = 4))

    print("Shader Saver | JSON saved: " + jsonFilepath)

    currentVersion += 1
    print("Shader Saver | Incremented Current Version to " + ToVersionString(currentVersion))

    scenePath = cmds.file(q = True, sceneName = True)

    savedSourceDirectory = GetPublishDirectory("source/")
    if os.path.isdir(savedSourceDirectory) == False: 
        os.mkdir(savedSourceDirectory)
        print("Shader Saver | Created directory: " + savedSourceDirectory)

    sourceOutputPath = GetPublishDirectory("/source/") + GetSceneName() + ".mb"
    cmds.file(rename = sourceOutputPath)
    cmds.file(save = True, type = "mayaBinary")
    print("Shader Saver | Source Scene saved: " + cmds.file(q = True, sceneName = True))
    
    cmds.file(rename = scenePath[:scenePath.rfind(".v")] + ToVersionString(currentVersion) + ".mb")
    print("Shader Saver | Open Scene version incremented: " + GetSceneName())

    cmds.select(selection)


def SaveShaderOnObject(object):
    # adapted from http://bit.ly/3fIe165
    shadingGroups = cmds.listConnections(object, type = 'shadingEngine')
    if (shadingGroups == None): 
        print("Shader Saver | No shading grounds found for object " + object)
        return

    shaders = cmds.ls(cmds.listConnections(shadingGroups), materials = True)
    version = ToVersionString(currentVersion)

    destinationDirectory = GetPublishDirectory("material/")
    for s in shaders:
        # this needs version incrementing. Should be no file-overwriting!
        cmds.select(s)
        filename = destinationDirectory + s + version + ".mb"
        if (os.path.exists(filename) == False):
            output = cmds.file(destinationDirectory + s + version, options = "v=0;p=17;f=0", type = "mayaBinary", preserveReferences = True, exportSelected = True, saveReferencesUnloaded = True)
            print("Shader Saver | Material saved: " + output)
            return output

        return filename



# ===========================================================================================================
#   Main thread

PreloadVersion()
UI_ShaderSaver()