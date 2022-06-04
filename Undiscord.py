# Undiscord, by ShrootBuck
# Version 0.1


# Imports

import json
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


def ReadFromZip(ZipName, FileName):
    with ZipFile(ZipName) as ZipObject:
        with ZipObject.open(FileName) as MyFile:
            return MyFile.read()


# Get the Auth Token
AuthorizationToken = Debug("Enter your Discord authorization token:\t", "OPTIONS", True)


# Attempt to convert it to an integer-represented value
UserSelection = None
IntParseSuccess = False  # I know, bad way of handling this, don't talk to me about it

while IntParseSuccess == False:
    UserSelection = Debug(
        "From where should Undiscord delete messages?\n\t\t[1]:\tAll\n\t\t[2]:\tServers\n\t\t[3]:\tDMs\n\t\t[4]:\tNone\n:\t",
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

ZipReadFailure = True
MessageIndexJSON = "I do a little trolling."

# Ensure auto-retry
while ZipReadFailure:
    try:
        Debug("Please import your Discord data package.", "OPTIONS", False)
        ArchivePath = PromptFileUpload(
            [("ZIP Files", "*.zip")], "Please import your Discord data package."
        )
        MessageIndexJSON = ReadFromZip(ArchivePath, "messages/index.json")
        ZipReadFailure = False

    except Exception as ReadZIPException:
        Debug(ReadZIPException, "ERROR", False)
        ZipReadFailure = True  # Shouldn't be necessary, but good practice

MessageIndex = json.loads(MessageIndexJSON)

# Get the channels to purge
Channels = {"DM": [], "Server": []}

# DMs
for Index in MessageIndex:
    if MessageIndex[Index].startswith("Direct Message with"):
        Channels["DM"].append(Index)
    else:
        # Server
        Channels["Server"].append(Index)


# DM fetch: https://discord.com/api/v9/channels/ChannelID/messages?limit=100


match UserSelection:
    case 2:
        print("e")
