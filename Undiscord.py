# Undiscord, by ShrootBuck
# Version 0.1


# Imports

from time import sleep
from tkinter import filedialog
import tkinter as Tkinter
import os


# Variables

ConsoleColors = {
    "Green":		"\033[92m",
    "Yellow":		"\033[93m",
    "Blue":		"\033[94m",
    "Pink":		"\033[95m",
    "Cyan":		"\033[96m",
    "Red":		"\033[91m",
    "Bold":		"\033[1m",
    "Underline":	"\033[4m"
}


# Functions

def Debug(Message,  Prefix="DEBUG", ColorMessage=False, IsInput=False, *Colors):

    # Add all styling
    for Value in Colors:
        FormattedMessage = ConsoleColors[Value]

    # Add the actual message and color terminator
    if (ColorMessage):
        FormattedMessage = FormattedMessage + \
            "[" + Prefix + "]:\t" + Message + "\033[0m"
    else:
        FormattedMessage = FormattedMessage + \
            "[" + Prefix + "]:\t" + "\033[0m" + Message

    # Behavior determined on whether it's an input or not
    if (IsInput):
        return input(FormattedMessage)
    else:
        print(FormattedMessage)


def HangProcess():
    while (True):
        sleep(1000)


def ClearConsole():
    Command = "clear"
    if os.name in ("nt", "dos"):  # Windows uses cls
        Command = "cls"
    # Execute command
    os.system(Command)


def PromptFileUpload():
    Root = Tkinter.Tk()
    Root.withdraw()  # We don't actually need a UI from TK
    return filedialog.askopenfilename()


# Attempt to convert it to an integer-represented value
UserSelection = None
IntParseSuccess = False  # I know, bad way of handling this, don't talk to me about it

while (IntParseSuccess == False):
    UserSelection = Debug(
        "From where should Undiscord delete messages?\n\t\t[1]:\tAll\n\t\t[2]:\tServers\n\t\t[3]:\tDMs\n\t\t[4]:\tNone\n:", "OPTIONS", False, True, "Cyan")
    # Try parsing
    try:
        UserSelection = int(UserSelection)
    except ValueError:
        ClearConsole()
        Debug("Please select a valid option!", "ERROR", True, False, "Red")

match UserSelection:
    case 2:
        print("e")
