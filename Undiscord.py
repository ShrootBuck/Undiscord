# Undiscord, by ShrootBuck
# Version 0.1


# Imports

import json
import requests
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
AuthorizationToken = Debug("Enter your Discord authorization token: ", "OPTIONS", True)


# Get the User ID
UserID = Debug("Enter your Discord user ID: ", "OPTIONS", True)


# Session
MainSession = requests.session()
MainSession.headers = {"authorization": AuthorizationToken}


# Attempt to convert it to an integer-represented value
UserSelection = None
IntParseSuccess = False  # I know, bad way of handling this, don't talk to me about it

while IntParseSuccess == False:
    UserSelection = Debug(
        "From where should Undiscord delete messages?\n\t\t[1]:\tServers\n\t\t[2]:\tDMs\n:\t",
        "OPTIONS",
        True,
    )
    # Try parsing
    try:
        UserSelection = int(UserSelection)
        IntParseSuccess = True
    except ValueError:
        Debug(
            "Please select a valid option!",
            "ERROR",
            False,
        )


# Unzip the data package

ZipReadFailure = True
MessageIndexJSON = "I do a little trolling."
CurrentServerListJSON = "I do a little trolling."  # Used later

# Ensure auto-retry
while ZipReadFailure:
    try:
        Debug("Please import your Discord data package.", "OPTIONS", False)
        ArchivePath = PromptFileUpload(
            [("ZIP Files", "*.zip")], "Please import your Discord data package."
        )
        MessageIndexJSON = ReadFromZip(ArchivePath, "messages/index.json")
        CurrentServerListJSON = ReadFromZip(ArchivePath, "servers/index.json")

        ZipReadFailure = False

        ClearConsole()

    except Exception as ReadZIPException:
        Debug(ReadZIPException, "ERROR", False)
        ZipReadFailure = True  # Shouldn't be necessary, but good practice

MessageIndex = json.loads(MessageIndexJSON)
CurrentServerList = json.loads(CurrentServerListJSON)

# Get the channels to index
Channels = {"DM": [], "Server": []}

ChannelsToPurge = []

# DMs
for Index in MessageIndex:
    if MessageIndex[Index].startswith("Direct Message with"):
        Channels["DM"].append(Index)


# Servers
for Index in CurrentServerList.keys():
    Channels["Server"].append(Index)


# Easy way to break nested loops
class BreakNestedLoop(Exception):
    pass


def QueryChannelMessages(ID, IsServer=True):
    Messages = []
    Data = {"Offset": 0}

    # Begin querying
    try:
        while "WOAH" == "WOAH":
            if IsServer == True:
                QueryURL = f"https://discord.com/api/v9/guilds/{ID}/messages/search?author_id={UserID}&offset={str(Data['Offset'])}"
            else:
                QueryURL = f"https://discord.com/api/v9/channels/{ID}/messages/search?author_id={UserID}&offset={str(Data['Offset'])}"
            Query = MainSession.get(QueryURL)
            match Query.status_code:
                case 200:
                    # Save messages
                    for Message in Query.json()["messages"]:
                        Messages.append(Message[0])

                    # If we're done
                    if len(Query.json()["messages"]) < 25:
                        raise BreakNestedLoop
                    else:
                        Data["Offset"] += 25
                case 202:  # Channel needs to index
                    time.sleep(2)
                case 403:  # No access to channel
                    raise BreakNestedLoop
                case 429:  # Ratelimit
                    if "retry_after" in Query.json().keys():
                        time.sleep(int(Query.json()["retry_after"]))
    except BreakNestedLoop:
        pass
    return Messages


AmountDeleted = 0


match UserSelection:
    case 1:  # Servers

        for Server in Channels["Server"]:
            ServerMessages = QueryChannelMessages(Server, True)

            for Message in ServerMessages:
                try:
                    while True:
                        DeleteRequest = MainSession.delete(
                            f"https://discord.com/api/v9/channels/{Message['channel_id']}/messages/{Message['id']}"
                        )

                        match DeleteRequest.status_code:
                            case 204:  # Success
                                AmountDeleted += 1
                                raise BreakNestedLoop
                            case 403:  # No access anymore
                                Debug(
                                    f"No access to channel {Message['channel_id']} in server {Server}"
                                )
                                raise BreakNestedLoop
                            case 429:  # Ratelimit
                                if "retry_after" in DeleteRequest.json().keys():
                                    time.sleep(int(DeleteRequest.json()["retry_after"]))
                except BreakNestedLoop:
                    pass

            Debug(f"Finished clearing messages in server {Server}")

ClearConsole()
Debug(f"Deleted {AmountDeleted} messages!", "DEBUG", True)
