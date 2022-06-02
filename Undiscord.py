# Undiscord, by ShrootBuck
# Version 0.1


# Imports

import time
from zipfile import ZipFile
from tkinter import filedialog
import tkinter as Tkinter
import os


# Functions


def Debug(Message, Prefix="DEBUG", IsInput=False):
    FormattedMessage = "[" + Prefix + "]:\t" + Message

    # Behavior determined on whether it's an input or not
    if IsInput:
        return input(FormattedMessage)
    else:
        print(FormattedMessage)


def HangProcess():
    while True:
        time.sleep(1000)


def ClearConsole():
    Command = "clear"
    if os.name in ("nt", "dos"):  # Windows uses cls
        Command = "cls"
    # Execute command
    os.system(Command)


def PromptFileUpload(
    AllowedFiles, Title="Please select a file.", InitialDirectory=os.getcwd()
):
    Root = Tkinter.Tk()
    Root.withdraw()  # We don't actually need a UI from TK
    return filedialog.askopenfilename(
        initialdir=InitialDirectory, title=Title, filetypes=AllowedFiles
    )


def ExtractZip(FileName, Destination=None, Password=None):
    with ZipFile(FileName, "r") as ZipObject:
        ZipObject.extractall(Destination, None, Password)


# Get the Auth Token
AuthorizationToken = Debug("Enter your Discord authorization token:", "OPTIONS", True)


# Attempt to convert it to an integer-represented value
UserSelection = None
IntParseSuccess = False  # I know, bad way of handling this, don't talk to me about it

while IntParseSuccess == False:
    UserSelection = Debug(
        "From where should Undiscord delete messages?\n\t\t[1]:\tAll\n\t\t[2]:\tServers\n\t\t[3]:\tDMs\n\t\t[4]:\tNone\n:",
        "OPTIONS",
        True,
    )
    # Try parsing
    try:
        UserSelection = int(UserSelection)
        IntParseSuccess = True
    except ValueError:
        ClearConsole()
        Debug(
            "Please select a valid option!",
            "ERROR",
            False,
        )


# Unzip the data package
Debug("Please import your Discord data package.", "OPTIONS", False)
time.sleep(1)  # Funky
ArchivePath = PromptFileUpload(
    [("ZIP Files", "*.zip")], "Please import your Discord data package."
)

try:
    ExtractZip(ArchivePath, "temp")
except Exception as e:
    print(e)

time.sleep(10)
match UserSelection:
    case 2:
        print("e")
