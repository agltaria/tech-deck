# TD A3 Shader Loader - 13892385
# 
# Select an object, and this tool will load all its shader relationships. 
# RELIES ON Shader Saver SAVING THEM IN PREVIOUS SCENE
# ============================================================================================================

import maya.cmds as cmds

#   Properties



#   Variables



#   Functions



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

    cmds.optionMenu(label = 'Available Versions:')
    cmds.menuItem(label = 'v001')
    cmds.menuItem(label = 'v002')

    cmds.button(label = 'Load and Apply Object\'s Shaders', align = 'center')
    cmds.separator(h = 30)
    cmds.button(label = 'Load and Apply All Shaders', align = 'center')

    cmds.showWindow('Shader_Loader')


# ===========================================================================================================
#   Main thread

UI_ShaderLoader()