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
versionSelector = "ShaderLoaderVersionSelector"

global applyObjectButton
global outputWindow
global checkbox
global outputWindowHeight

global selection
global availableVersions


#   Functions
def ToVersionString(version): # takes an int, and returns a version string that matches the convention '.vXXX'
    if version < 10: return ".v00" + str(version)
    if version < 100: return ".v0" + str(version)
    return ".v" + str(version)


def GetAssetMaterialDirectory(assetName): # For a given asset name, return the absolute file path to the asset's /materials folder
    scenePath = cmds.file(q = True, sceneName = True)
    output = scenePath[:scenePath.rfind(scenesDirectoryName) + len(scenesDirectoryName)] + jsonTemplatePath.replace("<assetName>", assetName)
    return output


def GetAssetJSONFilename(assetName, version): # For a given asset name and version, return the absolute file path to the relevant .json file
    return GetAssetMaterialDirectory(assetName) + assetName + "_surface" + ToVersionString(version) + ".json"


def FindNthOccurrenceOfSubstring(string, substring, n): # Returns the index of the 'nth' occurrence of a substring in a string, where n is an integer
    # This was needed as all the objects are parented to 'setGeo' in a Lighting scene, so paths need the 3rd occurrence of '|' instead of the 2nd
    # adapted from http://bit.ly/3VIfdXA
    start = string.find(substring)

    while start >= 0 and n > 1:
        start = string.find(substring, start + len(substring))
        n -= 1

    return start


def GetValidVersionsForObject(object): # Searches for JSON files created for the given object, returning an array of valid versions found
    if object == None or len(object) <= 0: return [] # GUARD in case nothing is selected

    output = []
    assetName = object[0][object[0].rfind(targetObjectSubstring) + len(targetObjectSubstring) : len(object[0])]
    
    print("Shader Loader | Searching for " + GetAssetJSONFilename(assetName, 0)) # this could've been printed 100 times in the loop...
                                                                                 # ...not very helpful so I put it outside

    version = 1
    while os.path.exists(GetAssetJSONFilename(assetName, version)) or version <= versionSearchLimit: # versions could be skipped or not start at 1
        if os.path.exists(GetAssetJSONFilename(assetName, version)):
            # Below: if we found a potential version, load the JSON and check 'compatible_model' matches the object's referenced model
            referencedModelPath = cmds.referenceQuery(object, filename = True)
            referencedModelRelative = referencedModelPath[referencedModelPath.find("/publish") : len(referencedModelPath)]
            jsonFile = open(GetAssetJSONFilename(assetName, version))
            jsonData = json.load(jsonFile)
            compatibleModel = jsonData["compatible_model"]


            if (referencedModelRelative == compatibleModel): # if it passes, add it to the list!
                output.append(version) 
                print("Shader Loader | Found version: " + str(version))
            else:
                print("Shader Loader | Incompatible model! referenced model: " + referencedModelRelative + ", required model: " + compatibleModel)

        version += 1

    return output


def GetShaderFromObject(childObject, jsonData): # find the pair in the JSON Data that matches childObject, and return the shader half of the pair
    shapeName = childObject[childObject.rfind(":mRef_") + 1 : len(childObject)].replace("Shape", "")
    
    for p in jsonData["geometry_shader_pairs"]:
        if p["shape"] == shapeName:
            return p["shader"]

    return "" 



#   Methods
def UI_ShaderLoader(): # MAIN UI
    if cmds.window('Shader_Loader', exists = True): cmds.deleteUI('Shader_Loader')

    cmds.window('Shader_Loader', widthHeight = (200, 340), sizeable = False, resizeToFitChildren = True)
    cmds.columnLayout(columnAttach = ('both', 5), rowSpacing = 10, columnWidth = 220)

    cmds.text(' ')
    cmds.text('SHADER LOADER')
    cmds.text(' ')
    cmds.text('Loads & applies all shaders and')
    cmds.text('shader-geometry references saved by')
    cmds.text('Shader Saver in a Surfacing scene')
    cmds.separator(h = 30)

    # Below: When creating the UI, we have to get the valid versions for the current selected object to dynamically create the dropdown list
    global availableVersions
    availableVersions = GetValidVersionsForObject(cmds.ls(selection = True))
    cmds.optionMenu(versionSelector, label = 'Available Versions:')
    global versionSelectorItems
    for v in availableVersions: # if there's no available version....there's no options created!
        versionString = ToVersionString(v)
        versionSelectorItems.append(cmds.menuItem(label = versionString, parent = versionSelector)) # we have to store references to all the option entries
                                                                                                    # so we can delete them later 

    global applyObjectButton
    # this button will be disabled if the length of availableVersions was 0
    applyObjectButton = cmds.button(label = 'Load and Apply Object\'s Shaders', align = 'center', enable = (len(availableVersions) > 0), command = "ApplyShadersToSelection()")
    
    cmds.separator(h = 30)
    cmds.button(label = 'Update, Load and Apply All Shaders', align = 'center', command = 'ApplyAllShaders()')
    
    global checkbox
    checkbox = cmds.checkBox(label = "Show log output")

    cmds.showWindow('Shader_Loader')

    # start the scriptJob for updating the UI based on the selection, running every time the selection is run, and parented to this window
    cmds.scriptJob(event = ["SelectionChanged", SJ_UpdateLoaderUI], parent = "Shader_Loader", replacePrevious = True)


def UI_Output(string): # DEBUG LOG UI
    print(string) # regardless if the user's enabled the debug log, we still want to print to the console
    
    if cmds.checkBox(checkbox, value = True, q = True) == False: return; # GUARD, returning if the user hasn't enabled the debug log

    global outputWindow
    outputWindow = "Shader_Loader_Log"
    global outputWindowHeight
    if cmds.window(outputWindow, exists = True) == False: # if the window DOESN'T exist yet, create it
        outputWindowHeight = 20
        cmds.window(outputWindow, widthHeight = (1200, outputWindowHeight), sizeable = False, resizeToFitChildren = True)
        cmds.columnLayout(columnAttach = ("both", 5), rowSpacing = 10, columnWidth = 1200)

    # we know the window now exists, add the extra height, new line of text and show the window
    outputWindowHeight += 22
    cmds.window(outputWindow, edit = True, height = outputWindowHeight)
    cmds.text(string, align = "left")
    cmds.showWindow(outputWindow)


def SJ_UpdateLoaderUI(): # DYNAMIC UI SCRIPT JOB
    global availableVersions
    oldAvailableVersions = availableVersions
    availableVersions = GetValidVersionsForObject(cmds.ls(selection = True)) # fetch the new availableVersions to compare to the old one

    if availableVersions != oldAvailableVersions: # no need to change the version list if it's identical....
        global versionSelectorItems
        if len(versionSelectorItems) > 0: cmds.deleteUI(versionSelectorItems, menuItem = True) # cmds.deleteUI can delete the whole list in one go

        versionSelectorItems = []

        for v in availableVersions: # again, no versions = no options created
            versionString = ToVersionString(v)
            # the parent flag is needed to point the menuItems to the versionSelector optionMenu. Maya's 'implicit selection' is funky, so this 
            # would break without it when the Debug UI had been created and then the User changed their selection
            versionSelectorItems.append(cmds.menuItem(label = versionString, parent = versionSelector)) 

    cmds.button(applyObjectButton, edit = True, enable = (len(availableVersions) > 0)) # don't forget the button! (could probably also go in the if-statement...)


def ApplyShadersToSelection(): # method for the single-object option. Stores the selection for later, applies the shaders and then re-selects the old selection
    StoreSelection()
    ApplyShadersToObject([selection[0][:FindNthOccurrenceOfSubstring(selection[0], "|", 3)]], cmds.optionMenu(versionSelector, q = True, value = True))
    cmds.select(selection)


def ApplyAllShaders(): # method for the all-object option. Iterates over setGeo's children, applying the shaders
    setObjects = cmds.listRelatives(setGeoName, children = True, fullPath = True) # list of all the objects under setGeo
    
    for o in setObjects:
        validVersions = GetValidVersionsForObject([o])

        if len(validVersions) > 0: # no point applying lambert1 to an object!
            ApplyShadersToObject([o], ToVersionString(validVersions[len(validVersions) - 1])) # passes in the 'last' version


def StoreSelection(): # stores the user's selection for later
    global selection
    selection = cmds.ls(dagObjects = True, objectsOnly = True, shapes = True, long = True, selection = True)


def ApplyShadersToObject(object, versionString): # for the given object and version, import and apply its material
    # Below: Load the JSON file for the asset
        # we're using full paths because some objects have the same name, object[] will be the Shape, and so "Shape" needs to be removed
    assetName = object[0][object[0].rfind(targetObjectSubstring) + len(targetObjectSubstring) : len(object[0])].replace("Shape", "")
    
    shaderDirectory = GetAssetMaterialDirectory(assetName)

    version = int(versionString[2:len(versionString)])
    jsonFile = open(GetAssetJSONFilename(assetName, version))
    jsonData = json.load(jsonFile)

    UI_Output("Shader Loader | Loaded JSON: " + GetAssetJSONFilename(assetName, version))

    # Below: get the children of the object (down to the Shape), import the material if needed, and apply it
    importedShaders = [] # used to prevent duplicates from being imported
    children = cmds.listRelatives(object, children = True, fullPath = True)
    for childObject in children:
        jsonShader = GetShaderFromObject(childObject, jsonData) 

        if (importedShaders.__contains__(jsonShader) == False): # if we haven't already imported this shader, import it
            shaderPath = shaderDirectory + jsonShader[jsonShader.rfind("/") + 1 : len(jsonShader)]
            UI_Output("Shader Loader | Attempting to import shader: " + shaderPath)
            importedShader = cmds.file(
                shaderPath, 
                i = True, 
                type = "mayaBinary", 
                ignoreVersion = True, 
                renameAll = True, 
                mergeNamespacesOnClash = True,
                namespace = assetName, # using the assetName as the namespace to prevent name clashes and to keep Hypershade organised
                options = "v=0;p=17;f=0",
                preserveReferences = True,
                importTimeRange = "combine"
            )

            importedShaders.append(jsonShader)

        shader = assetName + ":" + jsonShader[jsonShader.rfind("/") + 1 : jsonShader.rfind(".v")] # cmds.file wouldn't return the imported file, 
        cmds.select(childObject)                                                                  # so we had to get it anyway
        # hardly an adaptation if it's one line, but I discovered this command from here: http://bit.ly/3U2O8ww
        cmds.hyperShade(assign = shader)

        UI_Output("Shader Loader | Successfully assigned shader " + shader + " to object " + childObject)
        
        

# ===========================================================================================================
#   Main thread

UI_ShaderLoader()