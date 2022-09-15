from itertools import count
from datetime import datetime
import maya.cmds as cmds
import mtoa.core as arn
import random

# Context sensitive...                              Working based on a 'name'? i.e. for "chair", when you publish the set-piece, it exports the model into the assets/setPieces/chair
#                                                   folder as "car_v00X", numbering based on prior numbering (allow for manually overriding version numbering)

# Need to consider different kinds of assets...     Ethan's shader publishing tool will save all materials/shaders assigned to parts of the selected set-pieces geometry (validate that
#                                                   set-piece hierarchy still matches referenced set-piece?), and meta-data specifying how those shaders should be assigned within a new
#                                                   scene. Will need to save lighting scenes created with Christa's lighting tool?

# Some more notes...								Need a function to browse directory and open WIP file (does user need to manually find it, or can we automatically list WIP files from project?)
#													When opening a file, we should know where to look because we expect that you're already working inside of a Maya project



######################################################################### PSEUDOCODE BEGIN #########################################################################

def constructWindowMain():
	# Check for any existing windows or jobs from a previous time this script was run, and destroy those

	# Construct UI of main window
		# Create a button to open a WIP from the project
			# openWorkingFile()

		# Create a number of parameters that can be set by the user (or are set automatically). 
			# File type
				# This is a drop-down with various options: setPiece, set, prop, character, sequence
			# File sub-type
				# This is a drop-down with various options, depending on type...
					# Assets: model, surfacing, rig, animation
					# sequence: layout, light, animation
			# File name
				# Additionally, if this is a sequence, shot number
			# Version number
				# Greyed out by default, 

		# Create a button that saves a new version of the current open working file
			# saveOpenFile()
		# Create a button that publishes the current open working file
			# publishOpenFile()

	# Update main window UI (i.e. greyout/ungreyout relevant options, populate paramaters with info, determine next version number)
	updateWindowMain()

	# Run a script job, that listens for changes made in the scene (checks if maya file has changed since open/save) and greys out 'Publish' button accordingly

	# Probably don't need to do this button...
		# Update current references
			# updateReferences()

def updateWindowMain():
	# Check directory of open File
		# If the file lies within the wip directory...
			# Iteratively step up through the directory to identify the currently open file's type, sub-type and name
			# Iterate over files in current directory, comparing their names to determine the highest version number, and set NEXT version number to one above that
			# Populate the main window's UI with this newfound information, and grey out those options
		# Else, we assume that this is a new file and hence...
			# Populate the main window's UI with default/empty information, and make sure options ARE NOT greyed
			# Grey out the 'Publish' button, as we cannot publish an unsaved file

def openWorkingFile():
	# Opens a file browser window (initially opens scene folder from within project directory)
		# If user closes this window instead of selecting a valid file, return out of this function
		# If user selects an invalid file (e.g. outside of the WIP directory or not .mb) create a pop-up explaining the issue and return out of this function

	# If the selected file is not the most recent version, create a pop-up warning the user before proceeding

	# Open the selected Maya binary file (and store a record of the file's containing directory if necessary)

	# Update main window UI (i.e. greyout/ungreyout relevant options, populate paramaters with info, determine next version number)
	updateWindowMain()

def updateReferences():
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

def saveOpenFile():
	# We must verify that there is only 1 group transform node in the hierarchy
	# Verify that the above is true, else create a pop-up explaining the issue and return out of this function

	# Use known information to save new version into the WIP directory (this should be fine even if directory doesn't already exist?)
		# /wip/assets/[type]/[subType]/[name]_[subType]_v[versionNumber].mb
		# /wip/sequence/[name]/[name]_[shotNo]/[subType]/[name]_[shotNo]_[subType]_v[versionNumber].mb

	# Update main window UI (i.e. greyout/ungreyout relevant options, populate paramaters with info, determine next version number)
	updateWindowMain()

def publishOpenFile():
	# Cannot publish if the open file is not already saved, or if changes have been made since opening/saving the open file
	# Verify that the above is true, else create a pop-up explaining the issue and return out of this function

	# Use known information to save new version into the published directory (this should be fine even if directory doesn't already exist?)
		# /publish/assets/[type]/[subType]/source/[name]_[subType]_v[versionNumber].mb
		# /publish/sequence/[name]/[name]_[shotNo]/[subType]/source/[name]_[shotNo]_[subType]_v[versionNumber].???
	# Based on known information, also export alternate file types into cache folder
		# /publish/assets/[type]/[subType]/cache/[name]_[subType]_v[versionNumber].mb
		# /publish/sequence/[name]/[name]_[shotNo]/[subType]/cache/[name]_[shotNo]_[subType]_v[versionNumber].???

	# We need logic to differentiate between file/asset types and publish accordingly (.abc, .fbx)

	# Version up wip file, to avoid publishing over the file we just published



# When this script is run (from shelf), construct the main window
constructWindowMain()

########################################################################## PSEUDOCODE END ##########################################################################