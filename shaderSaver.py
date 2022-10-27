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

global targetObjectSubstring
targetObjectSubstring = "mRef_"


#   Variables
global currentVersion
global outputWindow
global checkbox
global outputWindowHeight


#   Functions
def GetPublishDirectory(destination): # returns the absolute filepath to the specified publish directory (either /material or /source)
    scenePath = cmds.file(q = True, sceneName = True) # adapted from http://bit.ly/3ygRbJ8

    # adapted from http://bit.ly/3CtWiqT and http://bit.ly/3e8rfsc
    return scenePath[:scenePath.rfind('/') + 1].replace(wipDirectoryName, publishDirectoryName) + destination


def ToVersionString(version): # takes an int, and returns a version string that matches the convention '.vXXX'
    if version < 10: return ".v00" + str(version)
    if version < 100: return ".v0" + str(version)
    return ".v" + str(version)


def GetSceneName(): # returns the name (and version) of the scene file, without the file extension
    return os.path.splitext(cmds.file(q = True, sceneName = True, shortName = True))[0] # adapted from http://bit.ly/3ygRbJ8


def FindSecondOccurrenceOfSubstring(string, substring): # returns the index at which the second occurence of a substring is found in a string
    return string.find(substring, string.find(substring) + 1) # adapted from http://bit.ly/3yK93fP



#   Methods
def LoadVersion(): # pulls the current version of the Surfacing scene from the scene name, then saves it to currentVersion
    sceneName = GetSceneName()
    versionString = sceneName[sceneName.rfind('.v') + 2 : len(sceneName)] # adapted from http://bit.ly/3EFPd97

    global currentVersion
    currentVersion = int(versionString)

    print("Shader Saver | Current Version is " + ToVersionString(currentVersion))


def UI_ShaderSaver(): # MAIN UI 
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
    global checkbox
    checkbox = cmds.checkBox(label = 'Show log output')

    cmds.showWindow('Shader_Saver')


def UI_Output(string): # DEBUG LOG UI
    print(string) # regardless if the user's enabled the debug log, we still want to print to the console
    
    if cmds.checkBox(checkbox, value = True, q = True) == False: return; # GUARD, returning if the user hasn't enabled the debug log

    global outputWindow
    outputWindow = "Shader_Saver_Log"
    global outputWindowHeight
    if cmds.window(outputWindow, exists = True) == False: # if the window DOESN'T exist yet, create it
        outputWindowHeight = 20
        cmds.window(outputWindow, widthHeight = (1000, outputWindowHeight), sizeable = False, resizeToFitChildren = True)
        cmds.columnLayout(columnAttach = ("both", 5), rowSpacing = 10, columnWidth = 1000)

    # we know the window now exists, add the extra height, new line of text and show the window
    outputWindowHeight += 22
    cmds.window(outputWindow, edit = True, height = outputWindowHeight)
    cmds.text(string, align = "left")
    cmds.showWindow(outputWindow)



def SaveObjectShaders(): # Main-ish method. Identifies the relevant object in the scene, gets the materials applied to their 'Shape' children,
                         # sets up the JSON dictionary object, exports the shaders, saves the JSON, backs up the scene, and increments the open
                         # scene version. Phew!

    # Below: Fetch the current version in case the User changes scenes without restarting the tool 
    LoadVersion()
    
    # Below: Finding the right object in the scene
    allShapes = cmds.ls(dagObjects = True, objectsOnly = True, shapes = True, long = True) # list of everything, everywhere, all at once
    
    targetParent = None
    for s in allShapes:
        if s.__contains__(targetObjectSubstring): # 'filtering' the everything-list by whether or not it has "mRef_" in the name 
            targetParent = s[1 : FindSecondOccurrenceOfSubstring(s, "|mRef")] # found the geometry, no need to keep iterating, but also slice 
            break                                                             # it down to just the 'parent' name
    
    targetParent = "|" + targetParent + "|" # Maya craps itself if there's multiple objects with the same name :(
    selection = cmds.listRelatives(targetParent, children = True, fullPath = True) # 'selecting' the parent means we can iterate over the 
    cmds.select(selection)                                                         # children really easily

    if len(selection) < 1 or selection == None: # GUARD in case there's no object found or something's gone pear-shaped
        print("Shader Saver | No valid object found! Returning...")
        return

    # Below: Exporting the materials, and storing the references in the to-be-JSON data structures
    shaderPairlist = [] # this will become geometry_shader_pairs in the JSON
    id = 1001 
    for s in selection: # iterating over all the children of the parent object
        shader = SaveShaderOnObject(cmds.listRelatives(s, children = True))
        shape = s[FindSecondOccurrenceOfSubstring(s, "|") + 1 : len(s)]

        singlePair = { # set up the 'pair' dictionary
            "ID": id,
            "shape": shape,
            "shader": shader[shader.rfind("/" + publishDirectoryName) : len(shader)]
        }
        shaderPairlist.append(singlePair) #...and add it to the running array

        id += 1

    # Below: Extracting the referenced model in this scene to prevent mismatches and problems in the Lighting scene
    referencedModelPath = cmds.referenceQuery(selection[0], filename = True)
    compatibleModel = referencedModelPath[referencedModelPath.rfind("/" + publishDirectoryName) : len(referencedModelPath)]

    # Below: Bundle everything into the final JSON object
    jsonOutput = {
        "geometry_shader_pairs": shaderPairlist,
        "created_with": GetSceneName(),
        "compatible_model" : compatibleModel
    }

    # Below: Export the JSON
    # adapted from http://bit.ly/3EDPvgX
    global currentVersion
    jsonFilepath = GetPublishDirectory("/material/") + GetSceneName() + ".json"
    with open(jsonFilepath, "w", encoding = "utf-8") as writtenFile:
        writtenFile.write(json.dumps(jsonOutput, ensure_ascii = False, indent = 4))

    UI_Output("Shader Saver | JSON saved: " + jsonFilepath)

    # Increment the current version 
    currentVersion += 1
    UI_Output("Shader Saver | Incremented Current Version to " + ToVersionString(currentVersion))

    scenePath = cmds.file(q = True, sceneName = True)

    # Below: If required, create the /source folder for the scene backup
    savedSourceDirectory = GetPublishDirectory("source/")
    if os.path.isdir(savedSourceDirectory) == False: # annoyingly, the material export Maya command automatically creates folders, but the scene export command doesn't!
        os.mkdir(savedSourceDirectory)
        UI_Output("Shader Saver | Created directory: " + savedSourceDirectory)

    # Below: Export the scene backup
    sourceOutputPath = GetPublishDirectory("/source/") + GetSceneName() + ".mb"
    cmds.file(rename = sourceOutputPath)
    cmds.file(save = True, type = "mayaBinary")
    UI_Output("Shader Saver | Source Scene saved: " + cmds.file(q = True, sceneName = True))
    
    # Below: Increment the version of the current scene (may potentially clash with the universal publishing tool)
    cmds.file(rename = scenePath[:scenePath.rfind(".v")] + ToVersionString(currentVersion) + ".mb")
    UI_Output("Shader Saver | Open Scene version incremented: " + GetSceneName())

    cmds.select(selection) # reset the User's past selection


def SaveShaderOnObject(object): # Takes a single Shape object, gets the material applied to it and exports it, returning the filename
    # Below: honestly I'm not too sure how this works, note the 'adapted from', but this pulls the shaders from the given (singular) Shape and exports it
    # adapted from http://bit.ly/3fIe165
    shadingGroups = cmds.listConnections(object, type = 'shadingEngine')
    if shadingGroups == None: # GUARD in case no shading groups are found (very unlikely, but hey)
        print("Shader Saver | No shading groups found for object " + object)
        return

    shaders = cmds.ls(cmds.listConnections(shadingGroups), materials = True) # not all items in a shadingGroup are materials???
    version = ToVersionString(currentVersion)

    destinationDirectory = GetPublishDirectory("material/")
    for s in shaders: # should only be one, but I think I found a niche case with multiple or something...anyway it's not gonna break
        cmds.select(s)
        filename = destinationDirectory + s + version + ".mb"
        if os.path.exists(filename) == False: # If the material hasn't already been exported... (to prevent duplicates)
            output = cmds.file(destinationDirectory + s + version, options = "v=0;p=17;f=0", type = "mayaBinary", preserveReferences = True, exportSelected = True, saveReferencesUnloaded = True)
            UI_Output("Shader Saver | Material saved: " + output)
            return output

        return filename



# ===========================================================================================================
#   Main thread

UI_ShaderSaver()