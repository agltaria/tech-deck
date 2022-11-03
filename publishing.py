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
menuDepartment = None
menuOptionsDepartment = []
rowShotNumber = None
labelShotNumber = None
fieldName = None
fieldShotNumber = None
fieldVersionNumber = None
textSave = None
textPublish = None

# Variables
nextVersionNumber = -1 # A record of what the next saved version should be, generally 1 more than the hightest version in that folder
prevFileName = '' # A record, used when refreshing the UI to determine if the file has changed or not

# An array of each asset type
assetTypes = ['setPiece', 'set', 'prop', 'character', 'sequence']

# Reserved names that files 'names' cannot match
reservedNames = ['wip', 'publish', 'assets', 'sequence', 'source', 'cache']

# Departments for each asset type (dictionary)
departmentsPerAsset = { # TODO: Add 'camera' as an asset?
	'setPiece' : ['model', 'surfacing'],
	'set' : ['model'],
	'layout' : ['model', 'surfacing'],
	'prop' : ['model', 'surfacing', 'rig'],
	'character' : ['model', 'surfacing', 'rig', 'anim'], # Character use anim, but sequence uses animation? Allow both?
	'sequence' : ['animation', 'layout', 'lighting'] # Not technically an asset?
}

def ConstructWindowMain():
	global columnMain
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
	global textSave
	global textPublish

	# Check for any existing windows or jobs from a previous time this script was run, and destroy those
	if cmds.window('publishing', q = True, exists = True):	# Delete existing UI to avoid double up, and ensure name is unique
		cmds.deleteUI('publishing') # This should also kill any previous script jobs (as they should be children of this window)

	# Construct UI of main window
	cmds.window('publishing', title = 'Publish Tool', resizeToFitChildren = True, sizeable = False)
	columnMain = cmds.columnLayout(columnWidth = 300, columnAttach = ['both', 10])

	cmds.rowLayout(height = 20)
	cmds.setParent(columnMain)
	cmds.text(label = 'This tool saves correctly named/versioned')
	cmds.text(label = 'files into the project\'s WIP and Publish')
	cmds.text(label = 'directories, and lets you open WIP files')
	cmds.rowLayout(height = 20)
	cmds.setParent(columnMain)

	buttonOpenWIP = cmds.button(label = 'Open WIP', command = 'OpenWorkingFile()')			# Create a button to open a WIP from the project
	
	cmds.separator(height=10)

	# UI for parameters to be set by the user (or programmatically)
	cmds.rowLayout(numberOfColumns=2, columnWidth=[(1, 100), (2, 180)])						# File type (asset type)
	cmds.text(label = 'Asset Type')																# A drop-down with several options: setPiece, set, prop, character, sequence
	menuType = cmds.optionMenu('menuType', cc = 'RefreshDepartmentsMenu()') 					# Updates GUI appropriately upon changing selection
	PopulateAssetTypesMenu()
	cmds.setParent(columnMain)

	cmds.rowLayout(numberOfColumns=2, columnWidth=[(1, 100), (2, 180)])						# File sub-type (department)
	cmds.text(label = 'Department')																# A drop-down with several options that vary based on the previous drop-down:
	menuDepartment = cmds.optionMenu('menuDepartment', cc = 'UpdateSavePublishTexts()')			# Assets: model, surfacing, rig, animation # SURFACING SCENES MAY NEED TO WORK WITH ETHAN'S CODE
	cmds.setParent(columnMain)																	# Sequence: layout, light, animation
				
	cmds.rowLayout(numberOfColumns=2, columnWidth=[(1, 100), (2, 180)])						# File name	
	cmds.text(label = 'Name')
	fieldName = cmds.textField(changeCommand = 'UpdateSavePublishTexts()')
	cmds.setParent(columnMain)

	rowShotNumber = cmds.rowLayout(numberOfColumns=2, columnWidth=[(1, 100), (2, 150)])		# Shot number (only shown for a sequence file)
	labelShotNumber = cmds.text(label = 'Shot no.')
	fieldShotNumber = cmds.textField(changeCommand = 'UpdateSavePublishTexts()')
	cmds.setParent(columnMain)

	cmds.separator(height=10)

	cmds.rowLayout(numberOfColumns=2, columnWidth=[(1, 100), (2, 180)])						# Version number (greyed out by default)
	cmds.text(label = 'Version No.')
	fieldVersionNumber = cmds.textField()
	cmds.setParent(columnMain)

	cmds.separator(height=10)

	buttonSaveWIP = cmds.button(label = 'Save WIP', command = 'SaveOpenFile()')				# Create a button that saves a new version of the current open working file
	textSave = cmds.text(label = 'Will save as ...')										# Create dynamic caption

	cmds.separator(height=10)

	buttonSavePublished = cmds.button(label = 'Publish', command = 'PublishOpenFile()')		# Create a button that publishes the current open working file
	textPublish = cmds.text(label = 'Will publish as ...')									# Create dynamic caption

	cmds.rowLayout(height = 15)

	cmds.showWindow('publishing')

	UpdateWindowMain()	# Update main window UI (i.e. greyout/ungreyout relevant options, populate paramaters with info, determine next version number)

	# The logic to disable/reenable some UI should be called via a script job when:
	cmds.scriptJob(event = ['SelectionChanged', UpdateSavePublishTexts], parent = 'publishing')		# ...file 'modified?' changes from false to true (THIS IS A QUESTIONABLE EVENT TO LISTEN TO)
	cmds.scriptJob(event = ['SceneOpened', HandleNewSceneOpened], parent = 'publishing')				# ...the open scene changes, but perhaps not when WE change the scene programmatically

	# TODO: Is there some way for this tool to prevent saving via Maya's own 'Save' and "Save as..."?

def HandleNewSceneOpened():
	prevFileName = '' # If we didn't reset this and user was to reopen the same file, tool would no realise a file had been newly opened
	UpdateWindowMain()

def GetStartEndFrames(): # Returns a list of 2 elements: earliest found frame, and latest found frame. If search inconclusive, returns None.
	startFrame = 999999999
	endFrame = -999999999
	count = 0
	countHasFrames = 0
	transforms = cmds.ls(type = 'transform')
	for transform in transforms:
		keyframes = cmds.keyframe(transform, q = True, time = (-999999, 999999))
		if keyframes != None:
			min_max = sorted(keyframes)
			if min_max[0] < startFrame:
				startFrame = min_max[0]
			if min_max[-1] > endFrame:
				endFrame = min_max[-1]
			countHasFrames += 1
		count += 1
	#print('Start/End frames: ' + str(startFrame) + ', ' + str(endFrame) + '. Transforms found: ' + str(count) + ' (with keyframes: ' + str(countHasFrames) + ')')
	if startFrame < 999999999 and endFrame > -999999999:
		return [ startFrame, endFrame ]
	return None

def ClearWindowMain():	# Clears all text fields, clears departments drop down menu, and re-enables all drop down menus
	ClearDepartmentsMenu()
	cmds.optionMenu(menuType, e = True, enable = True)
	cmds.optionMenu(menuDepartment, e = True, enable = True)
	cmds.rowLayout(rowShotNumber, e = True, )

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
		fieldShotNumber = cmds.textField(changeCommand = 'UpdateSavePublishTexts()')

	UpdateSavePublishTexts()

def RefreshDepartmentsMenu():
	cmds.optionMenu(menuDepartment, e = True, enable = True)
	ClearDepartmentsMenu()
	assetType = assetTypes[cmds.optionMenu(menuType, q = True, select = True) - 1] # Fetch the name of the asset type currently selected in the asset type drop down menu
	PopulateDepartmentsMenu(assetType)

def ClearDepartmentsMenu():
	global labelShotNumber
	global fieldShotNumber

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
	global nextVersionNumber
	global prevFileName
	directory = GetFilePathAsArray()				# Check directory of open file
	ClearWindowMain()								# Clear drop down menus before we populate them

	# TODO: The following conditional is flawed, as it assumes a file recorded as existing in WIP when opened hasn't been since deleted (pretty obscure, though)
	if DoesStringArrayContain(directory, 'wip'): # Grey out and populate certain elements based on if this file exists in the WIP directory or not
		assetType = GetNameOfAssetType(directory)
		departmentName = GetNameOfDepartment(directory)

		# Detect and handle if the above fails - it would mean that there is something wrong with the project structure and/or the opened file wasn't created by this tool
		if assetType == 'invalid' or departmentName == 'invalid': # TODO: Files within a correctly formatted path - that does NOT match that files name - will not save into that path
			UpdateWindowMainForNew()
			return
		
		PopulateDepartmentsMenu(assetType)												# Select the given asset in the assets drop down menu, and configure departments menu
		departmentIndex = departmentsPerAsset[assetType].index(departmentName) + 1		# Note that characters use 'anim', but sequences use 'animation'
		cmds.optionMenu(menuDepartment, e = True, select = departmentIndex) 			# Select the given department in the departments drop down menu

		# Get file name, and from it: last X characters "*.vXXX.mb" for version number, asset name from file name -- write these to textfields, disable those textfields
		fileName = directory[-1]
		versionNumber = str(int(fileName[-6:-3]))
		assetName = GetFileNameAsArray()[0]
		cmds.textField(fieldName, e = True, text = assetName, enable = False)
		cmds.textField(fieldVersionNumber, e = True, text = versionNumber, enable = False)
		if assetType == 'sequence':
			shotNumber = str(int(GetFileNameAsArray()[1]))
			cmds.textField(fieldShotNumber, e = True, text = shotNumber, enable = False)
		SetNextVersionNumber()

		# As this is a file that exists within the WIP directory, we disable the drop down menus
		cmds.optionMenu(menuType, e = True, enable = False)
		cmds.optionMenu(menuDepartment, e = True, enable = False)

		# Enable 'publish' button when appropriate. It's enabled by default, but only re-enabled via code at specific points (without the following, opening a new WIP will not re-enable the button)
		if GetNameOfSavedFile(False) != prevFileName:
			prevFileName = GetNameOfSavedFile(False)
			cmds.button(buttonSavePublished, e = True, enable = True)
	elif DoesStringArrayContain(directory, 'publish'): # We should never find ourselves in the publishing directory
		UpdateWindowMainForNew()
		cmds.confirmDialog( title='Opened a published file',
		message='The currently open file is a published version. Published versions shouldn\'t be modified, so this tool will treat this file as an unrecognised/new scene.',
		button=['Okay'], defaultButton='Okay', cancelButton='Okay', dismissString='Okay')
	else: # Else, we assume that this is a new file and hence...
		UpdateWindowMainForNew()

	UpdateSavePublishTexts()

def UpdateWindowMainForNew():
	global nextVersionNumber
	global prevFileName
	directory = GetFilePathAsArray()											# Check directory of open file
	
	PopulateDepartmentsMenu(assetTypes[0])										# Populate the main window's UI with default/empty information, and make sure options ARE NOT greyed
	cmds.textField(fieldName, e = True, text = '', enable = True)
	cmds.textField(fieldVersionNumber, e = True, text = '0', enable = False)

	# Set version number to 1
	nextVersionNumber = 1

def UpdateSavePublishTexts():
	# Update caption beneath save button
	isModified = cmds.file(q = True, modified = True)
	# if (GetNameOfSavedFile(False) != prevFileName):
	# 	isModified = False
	isNameValid = IsNameValid(cmds.textField(fieldName, q = True, text = True))
	isSequence = assetTypes[cmds.optionMenu(menuType, q = True, select = True) - 1] == 'sequence' #GetFileNameAsArray()[0] == 'sequence'
	isShotNumberValid = False
	if isSequence:
		isShotNumberValid = IsShotNumberValid(cmds.textField(fieldShotNumber, q = True, text = True))
	if isNameValid and (not isSequence or (isSequence and isShotNumberValid)):
		if (isModified):
			cmds.text(textSave, e = True, label = 'Will save as ' + GetNameOfSavedFile() + '.mb')
			cmds.button(buttonSaveWIP, e = True, enable = True)
		else:
			cmds.text(textSave, e = True, label = 'Cannot save if no changes have been made')
			cmds.button(buttonSaveWIP, e = True, enable = False)
	else:
		cmds.text(textSave, e = True, label = 'Cannot save until a valid name is specified')
		cmds.button(buttonSaveWIP, e = True, enable = False)

	# Update caption beneath publish button
	isPublishEnabled = cmds.button(buttonSavePublished, q = True, enable = True) # Important, ensures publish remains disabled until a new/unknown asset is first saved
	isFileNew = len(cmds.textField(fieldVersionNumber, q = True, text = True)) <= 0
	if not isFileNew:
		isFileNew = int(cmds.textField(fieldVersionNumber, q = True, text = True)) <= 0
	if (isModified or isFileNew):#or not isPublishEnabled):
		cmds.text(textPublish, e = True, label = 'Cannot publish until changes are saved')
		cmds.button(buttonSavePublished, e = True, enable = False)
	else:
		cmds.text(textPublish, e = True, label = 'Will publish as ' + GetFilePathAsArray()[-1])
		cmds.button(buttonSavePublished, e = True, enable = True)

# TODO: A function that translates Title Case to camelCase, and vice versa (and displays any shortened words, such as 'anim', at their full length)

def IsNameValid(name):
	if len(name) <= 0:							# Name cannot be empty
		return False

	if '_' in name:								# Name cannot contain an underscore
		return False
	
	for illegalName in reservedNames:			# Name cannot match any reserved names
		if name == illegalName:
			return False

	for illegalName in assetTypes:				# Name cannot match any asset types
		if name == illegalName:
			return False

	for illegalNames in departmentsPerAsset:	# Name cannot match any department names
		for illegalName in illegalNames:
			if name == illegalName:
				return False
	
	return True

def IsShotNumberValid(shotNumber):
	if len(shotNumber) <= 0:					# Shot number cannot be empty
		return False

	if not shotNumber.isnumeric():				# Shot number must only contain numbers
		return False
	
	return True

def SetNextVersionNumber():
	global nextVersionNumber

	fileDirectoryArray = GetFilePathAsArray()
	fileDirectoryArray.pop()
	fileDirectory = '/'.join(fileDirectoryArray)

	nextVersionNumber = int(GetHighestVersionInFolder(fileDirectory)[-6:-3]) + 1


def OpenWorkingFile():
	# Opens a file browser window (initially opens scene folder from within project directory)
		# If user closes this window instead of selecting a valid file, return out of this function
		# If user selects an invalid file (e.g. outside of the WIP directory or not .mb) create a pop-up explaining the issue and return out of this function

	filePath = cmds.fileDialog2(caption = 'Open WIP', fileFilter = '*.mb', fileMode = 1, startingDirectory = GetDirectoryOfWIP())

	if filePath == None:
		return

	filePathArray = GetFilePathAsArray(filePath[0])

	if not DoesStringArrayContain(filePathArray, 'wip'):
		cmds.confirmDialog( title='Invalid File', message='The file you selected is not in the project\'s WIP directory. Please select a valid file.',
		button=['Okay'], defaultButton='Okay', cancelButton='Okay', dismissString='Okay')
		return

	fileDirectoryArray = filePathArray.copy() # Get path to containing directory, so that we may look through it for other versioned files
	fileDirectoryArray.pop()
	fileDirectory = '/'.join(fileDirectoryArray)

	proceedOption = 'Yes'
	if not IsFileHighestVersionInFolder(fileDirectory, filePathArray[-1]): # If the selected file is not the most recent version, create a pop-up warning the user before proceeding
		proceedOption = cmds.confirmDialog( title='Confirm', message='The file you selected is not the most recent version of this asset. Are you sure you still want to open it?',
		button=['Yes','No','Open highest version'], defaultButton='Yes', cancelButton='No', dismissString='No')

	if proceedOption == 'No':
		return

	if proceedOption == 'Open highest version':
		filePath = GetHighestVersionInFolder(fileDirectory)

	cmds.file(filePath, open = True, force = True)		# Open the selected Maya binary file
	prevFileName = ''									# If we didn't reset this and user was to reopen the same file, tool would no realise a file had been newly opened
	UpdateWindowMain()									# Update main window UI (i.e. greyout/ungreyout options, populate paramaters, determine next version number)

def IsFileHighestVersionInFolder(folderDirectory, fileName):
	foundFile = False
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

def GetHighestVersionInFolder(folderDirectory): # Some duplicate code, could likely just replace the above
	foundFileName = '' # File name of highest versioned file
	fileVersion = -1 # Highest found version number
	
	for otherName in os.listdir(path = folderDirectory):
		if otherName.endswith('.mb') and otherName.startswith(otherName[0:-7]):
			otherVersion = int(otherName[-6:-3])
			if otherVersion > fileVersion:
				fileVersion = otherVersion
				foundFileName = otherName
	#print(folderDirectory + '/' + foundFileName)
	return folderDirectory + '/' + foundFileName

def GetDirectoryOfWIP():
	rootDirectory = str(cmds.workspace(q = True, rd = True))
	return rootDirectory + 'scenes/wip'

def GetDirectoryOfPublish():
	rootDirectory = str(cmds.workspace(q = True, rd = True))
	return rootDirectory + 'scenes/publish'

def GetNameOfSavedFile(useNextVersionNumber = True):
	name = cmds.textField(fieldName, q = True, text = True)
	versionNumber = str(int(nextVersionNumber))
	if not useNextVersionNumber:
		versionNumber = cmds.textField(fieldVersionNumber, q = True, text = True) # We want the OPEN FILE's version when publishing, not the NEXT version number
	assetType = assetTypes[cmds.optionMenu(menuType, q = True, select = True) - 1]
	department = departmentsPerAsset[assetType][cmds.optionMenu(menuDepartment, q = True, select = True) - 1]

	zeroesToAdd = 3 - len(versionNumber) # Format version number correctly (e.g. 001, 027, 301)
	while zeroesToAdd > 0:
		versionNumber = '0' + versionNumber
		zeroesToAdd -= 1

	if assetType == 'sequence':
		shotNumber = cmds.textField(fieldShotNumber, q = True, text = True)
		zeroesToAdd = 3 - len(shotNumber) # Format shot number correctly (e.g. 001, 027, 301)
		while zeroesToAdd > 0:
			shotNumber = '0' + shotNumber
			zeroesToAdd -= 1
		return name + '_' + shotNumber + '_' + department + '.v' + versionNumber
	else:
		return name + '_' + department + '.v' + versionNumber

def GetPathOfSavedFile():
	name = cmds.textField(fieldName, q = True, text = True)
	assetType = assetTypes[cmds.optionMenu(menuType, q = True, select = True) - 1]
	department = departmentsPerAsset[assetType][cmds.optionMenu(menuDepartment, q = True, select = True) - 1]

	if assetType == 'sequence':
		shotNumber = cmds.textField(fieldShotNumber, q = True, text = True)
		zeroesToAdd = 3 - len(shotNumber) # Format shot number correctly (e.g. 001, 027, 301)
		while zeroesToAdd > 0:
			shotNumber = '0' + shotNumber
			zeroesToAdd -= 1
		return 'sequence/' + name + '/' + name + '_' + shotNumber + '/' + department
	else:
		return 'assets/' + assetType + '/' + name + '/' + department

def SaveOpenFile():
	# Should not save if there isn't a single parent node
	if not IsThereASingleRootObject():
		response = cmds.confirmDialog( title='Invalid Scene', message='There is more than one root node (containing geometry) in your scene hierarchy. Are you sure you want to save?',
		button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No')
		if response != 'Yes':
			return

	newFilePath = GetDirectoryOfWIP() + '/' + GetPathOfSavedFile() + '/' + GetNameOfSavedFile() + '.mb'		# Use known information to concatenate relevant directory

	CreateDirectoryIfNotExist(GetDirectoryOfWIP() + '/' + GetPathOfSavedFile()) 							# Check destination exists, else create a directory for the path specified
   
	cmds.file(rename = newFilePath)																			# Save new version into the specified WIP directory
	cmds.file(save = True, force = True, type = 'mayaBinary')

	cmds.button(buttonSavePublished, e = True, enable = True)												# Re-enable the publish button
	
	UpdateWindowMain() # Update main window UI (i.e. greyout/ungreyout relevant options, populate paramaters with info, determine next version number)

def PublishOpenFile():
	proceedOption = ''
	# Should not publish if there isn't a single parent node (we should be able to assume that this wil never be true, however)
	if not IsThereASingleRootObject():
		response = cmds.confirmDialog( title='Invalid Scene', message='There is more than one root node (containing geometry) in your scene hierarchy. Are you sure you want to publish?',
		button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No')
		if response != 'Yes':
			return
	
	# Create a pop-up stating that the open WIP has already been published if that is the case, then return
	if IsThisSceneAlreadyPublished():
		proceedOption = cmds.confirmDialog( title='Already Published', message='Published files already exist for this version. There is no need to publish again.',
		button=['Okay','Publish anyway'], defaultButton='Okay', cancelButton='Okay', dismissString='Okay')
		if proceedOption == 'Okay':
			return

	startEndFrames = GetStartEndFrames() # Putting this here before progress pop-up, so that we can tell user what files are being cached
	generatedFilesText = '.mb, .fbx'
	if startEndFrames != None:
		generatedFilesText += ', .abc'
	CreateProgressWindow('Publish in progress...', generatedFilesText)

	# TODO: Implement a dynamically disabled publish button, rather than a pop-up warning
	
	newFilePath = GetDirectoryOfPublish() + '/' + GetPathOfSavedFile() + '/'	# Use known information to concatenate relevant directory
	newFileName = GetNameOfSavedFile(False)

	# Create directories if they do not yet exist
	CreateDirectoryIfNotExist(newFilePath + 'source')
	CreateDirectoryIfNotExist(newFilePath + 'cache')
	CreateDirectoryIfNotExist(newFilePath + 'cache/fbx')
	CreateDirectoryIfNotExist(newFilePath + 'cache/abc')
	CreateDirectoryIfNotExist(newFilePath + 'cache/obj')	# We don't currently publish anything into this folder
	CreateDirectoryIfNotExist(newFilePath + 'cache/usd')	# We don't currently publish anything into this folder
   
	# Save all files into published folders 'source' and 'cache'
	cmds.file((newFilePath + 'source/' + newFileName + '.mb'), force = True, options = 'v=0', type = 'mayaBinary', preserveReferences = True, exportAll = True)			# Save .mb
	if startEndFrames != None:
		cmds.AbcExport(j = '-frameRange ' + str(int(startEndFrames[0])) + ' ' + str(int(startEndFrames[1])) 
			+ ' -dataFormat ogawa -file ' + newFilePath + 'cache/abc/' + newFileName + '.abc')																			# Save .abc
	cmds.file((newFilePath + 'cache/fbx/' + newFileName + '.fbx'), force = True, options = 'v=0', type = 'FBX export', preserveReferences = True, exportAll = True)		# Save .fbx

	# TODO: Call functionality in Ethan's script to publish material cache, passing in the correct version to file names and version property in the .JSON

	DestroyProgressWindow()
	UpdateWindowMain()

def CreateProgressWindow(message, message2):
	if cmds.window('progress', q = True, exists = True):
		cmds.deleteUI('progress')
	cmds.window('progress', resizeToFitChildren = True, sizeable = False)
	newColumn = cmds.columnLayout(columnWidth = 150, columnAttach = ['both', 0])
	cmds.rowLayout(height = 15)
	cmds.setParent(newColumn)
	cmds.text(label = str(message))
	cmds.rowLayout(height = 10)
	cmds.setParent(newColumn)
	cmds.text(label = 'Creating file types:')
	cmds.text(label = str(message2))
	cmds.rowLayout(height = 15)
	cmds.showWindow('progress')

def DestroyProgressWindow():
	if cmds.window('progress', q = True, exists = True):
		cmds.deleteUI('progress')

def IsThisSceneAlreadyPublished():
	filePath = GetDirectoryOfPublish() + '/' + GetPathOfSavedFile() + '/source/' + GetNameOfSavedFile(False) + '.mb'	# Use known information to concatenate relevant directory
	isExist = os.path.exists(filePath)
	return isExist

def IsThereASingleRootObject():
	meshInScene = cmds.ls(dagObjects = True, long = True, type = 'mesh')
	nameOfRoot = ''
	for name in meshInScene:
		meshPath = name.split('|')
		if nameOfRoot == '':
			nameOfRoot = meshPath[1]
		elif nameOfRoot != meshPath[1]:
			return False
	return True

def CreateDirectoryIfNotExist(directory): # Check destination exists, and create a directory for the path specified if doesn't
	isExist = os.path.exists(directory)
	if not isExist:
		os.makedirs(directory)

def GetFilePathAsArray(filePath = None): # Can specify a directory, otherwise we fetch the open scene's file path
	if filePath == None:
		filePath = cmds.file(q = True, sn = True)
	delimiter = '/'
	return filePath.split(delimiter)

def GetFileNameAsArray():
	fileName = GetFilePathAsArray()[-1][0:-7]
	delimiter = '_'
	return fileName.split(delimiter)

def DoesStringArrayContain(stringArray, string):
	for name in stringArray:
		if name == string:
			return True

	return False

ConstructWindowMain() # When this script is run (from shelf), construct the main window

# FILE NAMING/SAVING SCHEME ##########################################################################################################################

#     /wip/assets/[type]/name/[subType]       				/[name]_[subType]_v[versionNumber].mb
# /publish/assets/[type]/name/[subType]/source              /[name]_[subType]_v[versionNumber].mb
# /publish/assets/[type]/name/[subType]/cache				/[name]_[subType]_v[versionNumber].mb
#     /wip/sequence/[name]/[name]_[shotNo]/[subType]       	/[name]_[shotNo]_[subType]_v[versionNumber].mb
# /publish/sequence/[name]/[name]_[shotNo]/[subType]/source	/[name]_[shotNo]_[subType]_v[versionNumber].???
# /publish/sequence/[name]/[name]_[shotNo]/[subType]/cache	/[name]_[shotNo]_[subType]_v[versionNumber].???

# SNIPPETS ###########################################################################################################################################

# workspace -q -rd;													# query the project path

#numberOfCarsField = cmds.textField(text = str(numberOfCars))

# rootDirectory = cmds.workspace(q = True, rd = True)
# directory = cmds.workspace(q = True, dir = True)
# print('Root directory: ' + str(rootDirectory))
# print('Directory: ' + str(directory))
#fileSceneName = cmds.file(q = True, sn = True)
#fileList = cmds.file(q = True, l = True)
#print('File scene name: ' + str(fileSceneName))
#print('File list: ' + str(fileList))

# customPth = '/net/username/test/testscene.mb'
# cmds.file(rename = customPth)
# cmds.file(s=True,f=True, typ='mayaBinary')

# cmds.file( rename=name  )
# cmds.file( save=True, type='mayaAscii' )

# AbcExport -j "-frameRange 1 20 -dataFormat ogawa -file C:/Users/edwar/Downloads/Assessment2_GroupX/cache/alembic/publishABC.abc";
# file -force -options "v=0;" -type "FBX export" -pr -ea "C:/Users/edwar/Downloads/Assessment2_GroupX/assets/chairTest.fbx";
# file -force -options ""     -type "FBX export" -pr -ea "C:/Users/edwar/Downloads/Assessment2_GroupX/assets/chairTest.fbx"; # This one
# file -force -options "v=0;" -typ "FBX export" -pr -es "C:/Users/edwar/Downloads/Assessment2_GroupX/assets/test.fbx";
# file -force -options "v=0;" -type "mayaBinary" -pr -ea "C:/Users/edwar/Downloads/Assessment2_GroupX/assets/publishMB.mb";
# file -force -options "v=0;" -type "FBX export" -pr -ea "C:/Users/edwar/Downloads/Assessment2_GroupX/assets/publishFBX.fbx";

# SCRAPPED ###########################################################################################################################################

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

# Iteratively step up through the directory to identify the currently open file's type, sub-type and name
	# This is a drop-down with various options: setPiece, set, prop, character, sequence
		# Assets: model, surfacing, rig, animation # SURFACING SCENES MAY NEED TO WORK WITH ETHAN'S CODE
		# sequence: layout, light, animation