import win32com.client
import sys

# Main Function to Run
def createPythonShortcut(targetFile=None, targetFileDir=None, name=None, icon=None, terminal=None):

    # Allows Python File to communciate to Windows' Scripting/Automation System
    shell = win32com.client.Dispatch("WScript.Shell")

    # Finding python executable
    terminalTrue = sys.executable
    # Run Terminal or No Terminal
    termConversion = terminalTrue.split("\\")
    termConversion.pop(-1)
    termConversion.append("pythonw.exe")
    terminalFalse = "\\".join(termConversion)


    # This is Where the .lnk file is created at
    lnkFileLocation = rf"{shell.SpecialFolders("Desktop")}" + rf"\{name}.lnk"
    # This is to use a specified .ico file for icon
    iconFile = icon
    # Which file to run Argument
    argument = targetFile
    # Target File Directory
    argumentDir = targetFileDir

    # COM Object
    shortcut = shell.CreateShortCut(lnkFileLocation)

    if terminal == True:
        shortcut.TargetPath = terminalTrue
    else:
        shortcut.TargetPath = terminalFalse

    shortcut.Arguments = argument

    shortcut.WorkingDirectory = argumentDir

    shortcut.IconLocation = iconFile

    shortcut.save()

    # return lnkFileLocation, iconFile, argument, argumentDir, shortcut.TargetPath

# Testing Main Function
createPythonShortcut(r"E:\PycharmProjects\NotionAIOptimizer\DAEMON\interface.py",
                     r"E:\PycharmProjects\NotionAIOptimizer\DAEMON",
                     "DAEMON",
                     r'E:\PycharmProjects\NotionAIOptimizer\DAEMON\samurai.ico',
                     False)
