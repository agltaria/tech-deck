from operator import truediv
import maya.cmds as cmds
import os

# Context sensitive...                              Working based on a 'name'? i.e. for "chair", when you publish the set-piece, it exports the model into the assets/setPieces/chair
#                                                   folder as "car_v00X", numbering based on prior numbering (allow for manually overriding version numbering)

# Need to consider different kinds of assets...     Ethan's shader publishing tool will save all materials/shaders assigned to parts of the selected set-pieces geometry (validate that
#                                                   set-piece hierarchy still matches referenced set-piece?), and meta-data specifying how those shaders should be assigned within a new
#                                                   scene. Will need to save lighting scenes created with Christa's lighting tool?

# Some more notes...								Need a function to browse directory and open WIP file (does user need to manually find it, or can we automatically list WIP files from project?)
#													When opening a file, we should know where to look because we expect that you're already working inside of a Maya project

# Names of different UI parents in window
columnMain = None
buttonOpenWIP = None
buttonSaveWIP = None
buttonSavePublished = None
menuType = None
#menuOptionsType = []
menuDepartment = None
menuOptionsDepartment = []
rowShotNumber = None
labelShotNumber = None
fieldName = None
fieldShotNumber = None
fieldVersionNumber = None

# An array of each asset type
assetTypes = ['setPiece', 'set', 'layout', 'prop', 'character', 'sequence']

# Departments for each asset type
departmentsPerAsset = { # TODO: Add 'camera' as an asset?
	'setPiece' : ['model', 'surfacing'],
	'set' : ['model'],
	'layout' : ['model', 'surfacing'],
	'prop' : ['model', 'surfacing', 'rig'],
	'character' : ['model', 'surfacing', 'rig', 'animation'],
	'sequence' : ['animation', 'layout', 'lighting'] # TODO: Not technically an asset?
}

			# Iteratively step up through the directory to identify the currently open file's type, sub-type and name
				# This is a drop-down with various options: setPiece, set, prop, character, sequence
					# Assets: model, surfacing, rig, animation # SURFACING SCENES MAY NEED TO WORK WITH ETHAN'S CODE
					# sequence: layout, light, animation

def ConstructWindowMain():
	global columnMain # TODO: Check if these global declarations are neccessary?
	global buttonOpenWIP
	global buttonSaveWIP
	global buttonSavePublished
	global menuType
	global menuDepartment
	global rowShotNumber
	global labelShotNumber
	global fieldName
	global fieldShotNumber
	global fieldVersionNumber

	# Check for any existing windows or jobs from a previous time this script was run, and destroy those
	if cmds.window('publishing', exists = True):	# Delete existing UI to avoid double up, and ensure name is unique
		cmds.deleteUI('publishing')
	
	# TODO: Check for previous script jobs and kill them

	# Construct UI of main window
	cmds.window('publishing', resizeToFitChildren = True, sizeable = False)
	columnMain = cmds.columnLayout(columnWidth = 250, columnAttach = ['both', 0])

	buttonOpenWIP = cmds.button(label = 'Open WIP', command = 'OpenWorkingFile()')			# Create a button to open a WIP from the project
	
	cmds.separator(height=10)

	# UI for parameters to be set by the user (or automatically)
	cmds.rowLayout(numberOfColumns=2, columnWidth=[(1, 100), (2, 150)])						# File type (asset type)
	cmds.text(label = 'Asset Type')																# A drop-down with several options: setPiece, set, prop, character, sequence
	menuType = cmds.optionMenu('menuType', cc = 'RefreshDepartmentsMenu()') 					# Updates GUI appropriately upon changing selection
	PopulateAssetTypesMenu()
	cmds.setParent(columnMain)

	cmds.rowLayout(numberOfColumns=2, columnWidth=[(1, 100), (2, 150)])						# File sub-type (department)
	cmds.text(label = 'Department')																# A drop-down with several options that vary based on the previous drop-down:
	menuDepartment = cmds.optionMenu('menuDepartment')											# Assets: model, surfacing, rig, animation # SURFACING SCENES MAY NEED TO WORK WITH ETHAN'S CODE
	cmds.setParent(columnMain)																	# Sequence: layout, light, animation
				
	cmds.rowLayout(numberOfColumns=2, columnWidth=[(1, 100), (2, 150)])						# File name	
	cmds.text(label = 'Name')
	fieldName = cmds.textField()
	cmds.setParent(columnMain)

	rowShotNumber = cmds.rowLayout(numberOfColumns=2, columnWidth=[(1, 100), (2, 150)])		# Shot number (only shown for a sequence file)
	labelShotNumber = cmds.text(label = 'Shot no.')
	fieldShotNumber = cmds.textField()
	cmds.setParent(columnMain)

	cmds.separator(height=10)

	cmds.rowLayout(numberOfColumns=2, columnWidth=[(1, 100), (2, 150)])						# Version number (greyed out by default)
	cmds.text(label = 'Version No.')
	fieldVersionNumber = cmds.textField()
	cmds.setParent(columnMain)

	cmds.separator(height=10)

	buttonSaveWIP = cmds.button(label = 'Save WIP', command = 'SaveOpenFile()')				# Create a button that saves a new version of the current open working file
	buttonSavePublished = cmds.button(label = 'Publish', command = 'PublishOpenFile()')		# Create a button that publishes the current open working file

	# TODO: Create text element that shows a preview of the saved file name (and name of generated cache files?)
	# TODO: Create text element that intructs user to save their WIP before they can publish, if publish button is disabled

	cmds.showWindow('publishing')

	UpdateWindowMain()	# Update main window UI (i.e. greyout/ungreyout relevant options, populate paramaters with info, determine next version number)

	# TODO: Run a script job, that listens for changes made in the scene (checks if maya file has changed since open/save) and greys out 'Publish' button accordingly

def ClearWindowMain():	# Clears all text fields, clears departments drop down menu, and re-enables all drop down menus
	ClearDepartmentsMenu()
	cmds.optionMenu(menuType, e = True, enable = True)
	cmds.optionMenu(menuDepartment, e = True, enable = True)
	cmds.rowLayout(rowShotNumber, e = True, )

	# TODO: Clear text fields, re-enable text fields

def PopulateAssetTypesMenu():
	cmds.setParent(menuType, menu = True)
	for assetType in assetTypes:															# For each department specified for the asset type...
		cmds.menuItem(label = assetType)														# ...add a new menu item to the departments drop down menu
	cmds.optionMenu(menuType, e = True, select = 1)											# Select the given asset type in the asset types drop down menu

def PopulateDepartmentsMenu(nameOfAssetType):
	global labelShotNumber
	global fieldShotNumber

	cmds.setParent(menuDepartment, menu = True)
	for department in departmentsPerAsset[nameOfAssetType]:									# For each department specified for the asset type...
		menuOptionsDepartment.append(cmds.menuItem(label = department))							# ...add a new menu item to the departments drop down menu
	cmds.optionMenu(menuType, e = True, select = assetTypes.index(nameOfAssetType) + 1)		# Select the given asset type in the asset types drop down menu

	if nameOfAssetType == 'sequence':														# Insert a row for shot number if this is a sequence asset
		cmds.setParent(rowShotNumber)
		labelShotNumber = cmds.text(label = 'Shot no.')
		fieldShotNumber = cmds.textField()

def RefreshDepartmentsMenu():
	print('RefreshDepartmentsMenu')
	cmds.optionMenu(menuDepartment, e = True, enable = True)
	ClearDepartmentsMenu()
	assetType = assetTypes[cmds.optionMenu(menuType, q = True, select = True) - 1] # Fetch the name of the asset type currently selected in the asset type drop down menu
	PopulateDepartmentsMenu(assetType)

def ClearDepartmentsMenu():
	global labelShotNumber
	global fieldShotNumber

	print('ClearDepartmentsMenu')
	for element in menuOptionsDepartment:
		cmds.deleteUI(element)
	menuOptionsDepartment.clear()

	# Delete shot number field
	if labelShotNumber is not None:
		cmds.deleteUI(labelShotNumber)
		cmds.deleteUI(fieldShotNumber)
		labelShotNumber = None
		fieldShotNumber = None

def GetNameOfAssetType(directory):
	for assetType in assetTypes:
		if DoesStringArrayContain(directory, assetType):
			return assetType
	return 'invalid'

def GetNameOfDepartment(directory):
	for department in departmentsPerAsset[GetNameOfAssetType(directory)]: # This function unneccessarily gets called twice
		if DoesStringArrayContain(directory, department):
			return department
	return 'invalid'

# Update the entire window UI when we open a new file or run this script for the first time, basing values off of the currently open file
def UpdateWindowMain():
	directory = GetFilePathAsArray()				# Check directory of open file
	ClearWindowMain()								# Clear drop down menus before we populate them

	if DoesStringArrayContain(directory, 'wip'):	# Grey out and populate certain elements based on if this file exists in the WIP directory or not
		print('Update window for WIP')
		assetType = GetNameOfAssetType(directory)
		PopulateDepartmentsMenu(assetType)												# Select the given asset in the assets drop down menu, and configure departments menu
		departmentName = GetNameOfDepartment(directory)
		departmentIndex = departmentsPerAsset[assetType].index(departmentName) + 1
		cmds.optionMenu(menuDepartment, e = True, select = departmentIndex) 			# Select the given department in the departments drop down menu
		
		# TODO: Detect and handle if the above fails? It would mean that there is something wrong with the project structure.

		# Get file name, and from it: last X characters "*.vXXX.mb" for version number, asset name from file name -- write these to textfields, disable those textfields
		fileName = directory[-1]
		versionNumber = str(int(fileName[-6:-3]))
		assetName = GetFileNameAsArray()[0]
		cmds.textField(fieldName, e = True, text = assetName, enable = False)
		cmds.textField(fieldVersionNumber, e = True, text = versionNumber, enable = False)
		if assetType == 'sequence':
			shotNumber = str(int(GetFileNameAsArray()[1])) # TODO: Maybe fix; this works but relies on implicit cast from string to int (string follows format "name_no")
			cmds.textField(fieldShotNumber, e = True, text = shotNumber, enable = False)

		# TODO: Increment version number
		
		# As this is a file that exists within the WIP directory, we disable the drop down menus
		cmds.optionMenu(menuType, e = True, enable = False)
		cmds.optionMenu(menuDepartment, e = True, enable = False)

	elif DoesStringArrayContain(directory, 'publish'):
		print('Update window for publishing')
		# We should never find ourselves in the publishing directory
		# TODO: Blacklist certain words for file names? Naming files certain things like 'publish', 'wip' or 'set' will break certain logic.
	else:
		print('Update window for new/unknown')
		# Else, we assume that this is a new file and hence...
			# Populate the main window's UI with default/empty information, and make sure options ARE NOT greyed
			# Grey out the 'Publish' button, as we cannot publish an unsaved file
		PopulateDepartmentsMenu(assetTypes[0])
		cmds.button(buttonSavePublished, e = True, enable = False)
		cmds.textField(fieldVersionNumber, e = True, text = '1', enable = False)

# TODO: Low-prio // A function that translates Title Case to camelCase, and vice versa

def OpenWorkingFile():
	print('OpenWorkingFile()')

	# Opens a file browser window (initially opens scene folder from within project directory)
		# If user closes this window instead of selecting a valid file, return out of this function
		# If user selects an invalid file (e.g. outside of the WIP directory or not .mb) create a pop-up explaining the issue and return out of this function

	# TODO: Low-prio // Figure out how to get around the 'file has same name' warning this browser produces despite the fact it in no way overwrites any files
	filePath = cmds.fileDialog2(caption = 'Open WIP', fileFilter = '*.mb', fileMode = 0, startingDirectory = GetDirectoryOfWIP())

	if filePath == None:
		return

	filePathArray = GetFilePathAsArray(filePath[0])

	if not DoesStringArrayContain(filePathArray, 'wip'):
		# TODO: Have some sort of pop-up to handle this
		print('The selected file is NOT a wip scene!')
		return
	print('The selected file is a wip scene!')

	fileDirectoryArray = filePathArray
	fileDirectoryArray.pop()
	fileDirectory = '/'.join(fileDirectoryArray)

	# TODO: filePathArray is missing the actual file itself as the last element of the array, so IsFileHighest...() fails. Fix this.
	# print(filePath)
	# print(filePathArray)
	# print(IsFileHighestVersionInFolder(fileDirectory, filePathArray[-0]))

	# # TODO: If the selected file is not the most recent version, create a pop-up warning the user before proceeding
	# if not IsFileHighestVersionInFolder(filePath[0], filePathArray[-1]):
	# 	return

	# TODO: Open the selected Maya binary file (and store a record of the file's containing directory if necessary)

	# TODO: Update main window UI (i.e. greyout/ungreyout relevant options, populate paramaters with info, determine next version number)
	#UpdateWindowMain()

def IsFileHighestVersionInFolder(folderDirectory, fileName):
	foundFile = False
	print(fileName)
	fileVersion = int(fileName[-6:-3])
	
	for otherName in os.listdir(path = folderDirectory):
		if (not foundFile) and otherName == fileName:
			foundFile = True
		elif otherName.endswith('.mb') and otherName.startswith(otherName[0:-7]):
			otherVersion = int(otherName[-6:-3])
			if otherVersion > fileVersion:
				return False
	
	if (foundFile):
		return True
	return False

def GetDirectoryOfWIP():
	rootDirectory = str(cmds.workspace(q = True, rd = True))
	return rootDirectory + 'scenes/wip'

def GetNameOfSavedFile():
	#     /wip/assets/[type]/[subType]       					/[name]_[subType]_v[versionNumber].mb
	# /publish/assets/[type]/[subType]/source              		/[name]_[subType]_v[versionNumber].mb
	# /publish/assets/[type]/[subType]/cache                  	/[name]_[subType]_v[versionNumber].mb
	#     /wip/sequence/[name]/[name]_[shotNo]/[subType]       	/[name]_[shotNo]_[subType]_v[versionNumber].mb
	# /publish/sequence/[name]/[name]_[shotNo]/[subType]/source	/[name]_[shotNo]_[subType]_v[versionNumber].???
	# /publish/sequence/[name]/[name]_[shotNo]/[subType]/cache	/[name]_[shotNo]_[subType]_v[versionNumber].???
	name = cmds.textField(fieldName, q = True, text = True)
	shotNumber = cmds.textField(fieldShotNumber, q = True, text = True)
	versionNumber = str(int(cmds.textField(versionNumber, q = True, text = True)))
	assetType = assetTypes[cmds.optionMenu(menuType, q = True, select = True) - 1]
	department = departmentsPerAsset[assetType][cmds.optionMenu(menuDepartment, q = True, select = True) - 1]

	# Format version number correctly (e.g. 001, 027, 301)
	zeroesToAdd = 3 - versionNumber.len()
	while zeroesToAdd > 0:
		versionNumber = '0' + versionNumber
		zeroesToAdd -= 1

	if assetType == 'sequence':
		return name + '_' + shotNumber + '_' + department + '_v' + versionNumber + '.mb'
	else:
		return name + '_' + department + '_v' + versionNumber + '.mb'

def SaveOpenFile():
	# TODO: Make sure we're in a (valid) project?
	# TODO: For a 'new' file, check that the entered asset name and/or file name is already taken?
	
	print('SaveOpenFile()')
	# We must verify that there is only 1 group transform node in the hierarchy
	# Verify that the above is true, else create a pop-up explaining the issue and return out of this function

	# Use known information to save new version into the WIP directory (this should be fine even if directory doesn't already exist?)
		# /wip/assets/[type]/[subType]/[name]_[subType]_v[versionNumber].mb
		# /wip/sequence/[name]/[name]_[shotNo]/[subType]/[name]_[shotNo]_[subType]_v[versionNumber].mb

	# Update main window UI (i.e. greyout/ungreyout relevant options, populate paramaters with info, determine next version number)

	# cmds.file( rename=name  )
	# cmds.file( save=True, type='mayaAscii' )
	
	UpdateWindowMain()

def PublishOpenFile():
	print('PublishOpenFile()')
	# Cannot publish if the open file is not already saved, or if changes have been made since opening/saving the open file
	# Verify that the above is true, else create a pop-up explaining the issue and return out of this function

	# Use known information to save new version into the published directory (this should be fine even if directory doesn't already exist?)
		# /publish/assets/[type]/[subType]/source/[name]_[subType]_v[versionNumber].mb
		# /publish/sequence/[name]/[name]_[shotNo]/[subType]/source/[name]_[shotNo]_[subType]_v[versionNumber].???
	# Based on known information, also export alternate file types into cache folder
		# /publish/assets/[type]/[subType]/cache/[name]_[subType]_v[versionNumber].mb
		# /publish/sequence/[name]/[name]_[shotNo]/[subType]/cache/[name]_[shotNo]_[subType]_v[versionNumber].???

	# We need logic to differentiate between file/asset types and publish accordingly (.abc, .fbx)
	# TODO: Call functionality in Ethan's script to publish material cache, passing in the correct version to file names and version property in the .JSON

	# Version up wip file, to avoid publishing over the file we just published

def GetFilePathAsArray(filePath = None): # Can specify a directory, otherwise we fetch the open scene's file path
	if filePath == None:
		filePath = cmds.file(q = True, sn = True)
	delimiter = '/'
	return filePath.split(delimiter)

	# rootDirectory = cmds.workspace(q = True, rd = True)
	# directory = cmds.workspace(q = True, dir = True)
	# print('Root directory: ' + str(rootDirectory))
	# print('Directory: ' + str(directory))
	#fileSceneName = cmds.file(q = True, sn = True)
	#fileList = cmds.file(q = True, l = True)
	#print('File scene name: ' + str(fileSceneName))
	#print('File list: ' + str(fileList))

def GetFileNameAsArray():
	fileName = GetFilePathAsArray()[-1][0:-7]
	delimiter = '_'
	return fileName.split(delimiter)

def DoesStringArrayContain(stringArray, string):
	for name in stringArray:
		if name == string:
			return True

	return False

# When this script is run (from shelf), construct the main window
ConstructWindowMain()



# Snippets ###########################################################################################################################################

# workspace -q -rd;													# query the project path

#numberOfCarsField = cmds.textField(text = str(numberOfCars))

# Scrapped ###########################################################################################################################################

# def GetDirectoryOfWIP():
	# directory = GetFilePathAsArray() # Flawed, because assumes we currently have a file inside the project open
	# wip = ''
	# for element in directory:
	# 	if wip != '':
	# 		wip += '/'
	# 	wip += element
	# 	if element == 'wip':
	# 		break
	# return wip

# def UpdateReferences():
	# Verify that the open file is saved within the (WIP) directory, or else we cannot know what department the file belongs or what asset this is
	# Create pop-up and return if not valid

	# Note dependencies for a WIP asset... (should only reference PUBLISHED assets)
		# A set-piece...
			# Models > Model(s)
			# Surfacing > Model
		# A prop...
			# Models > Model(s)
			# Rig > Model
			# Surfacing > Model
		# A character...
			# Models > Model(s)
			# Animation > Rig
			# Rig > Model
			# Surfacing > Model
		# A set...
			# Model > Model(s)

	# Note dependencies for a WIP shot... (should only reference PUBLISHED assets)
		# A shot...
			# We do not need to be doing this eeeeeegghefbg84eirnbdifq9023wo4ehrinjgfe

	# Function will iterate through all references in scene and, for each reference...
		# Identify that reference's directory in publish
		# Determine if their are higher versioned versions of that asset
		# Ask user whether to change reference to newer version, or allow user to manually select a different version
# def IsOpenFileWIP():
# 	for name in reversed(GetFilePathAsArray()):
# 		if name == 'wip':
# 			return True

# 	return False
