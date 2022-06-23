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
        return input(FormattedMessage + ":\t")
    else:
        print(FormattedMessage)


def HangProcess():
    while True:
        time.sleep(1000)


def ClearConsole():  # Here in case I ever want to clean up this program's runtime appearance
    Command = "clear"
    if os.name in ("nt", "dos"):  # Windows uses cls
        Command = "cls"

    # Execute command
    os.system(Command)


def PromptFileUpload(
    AllowedFiles, Title="Please select a file.", InitialDirectory=os.getcwd()
):
    Root = Tkinter.Tk()
    Root.withdraw()  # We don't actually need a UI from TKinter
    return filedialog.askopenfilename(
        initialdir=InitialDirectory, title=Title, filetypes=AllowedFiles
    )


def ReadFromZip(ZipName, FileName):
    with ZipFile(ZipName) as ZipObject:
        with ZipObject.open(FileName) as MyFile:
            return MyFile.read()


# Get the Auth Token
AuthorizationToken = Debug("Enter your Discord authorization token", "OPTIONS", True)


# Get the User ID
UserID = Debug("Enter your Discord user ID", "OPTIONS", True)


# Session for a persistent token
MainSession = requests.session()
MainSession.headers = {"authorization": AuthorizationToken}


# Attempt to convert it to an integer-represented value
UserSelection = None
IntParseSuccess = False

while IntParseSuccess == False:
    UserSelection = Debug(
        "From where should Undiscord delete messages?\n\t\t[1]:\tServers\n\t\t[2]:\tDMs\n",
        "OPTIONS",
        True,
    )
    # Try parsing
    try:
        UserSelection = int(UserSelection)
        IntParseSuccess = True
    except ValueError:
        Debug("Please select a valid option!", "ERROR", False)


DeletePinned = Debug("Delete pinned messages? (y/n)", "OPTIONS", True) == "y"


# Unzip the data package

ZipReadFailure = True
MessageIndexJSON = "I do a little trolling."
CurrentServerListJSON = "I do a little trolling."

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

    except Exception as ReadZIPException:
        Debug("ReadZIPException! Something went wrong.", "ERROR", False)
        ZipReadFailure = True  # Shouldn't be necessary, but good practice

MessageIndex = json.loads(MessageIndexJSON)
CurrentServerList = json.loads(CurrentServerListJSON)

# Get the channels to index
Channels = {"DM": [], "Server": []}

ChannelsToPurge = []

# DMs

for Index in MessageIndex:
    if MessageIndex[Index] == None:
        continue  # Not this channel

    if MessageIndex[Index].startswith("Direct Message with"):
        Channels["DM"].append(Index)


# Servers
for Index in CurrentServerList.keys():
    Channels["Server"].append(Index)


# Easy way to break nested loops
class BreakNestedLoop(Exception):
    pass


def QueryChannelMessages(ID):
    Data = {"Offset": 0, "Messages": [], "QueryURL": "", "ChannelType": "guilds"}

    # Begin querying
    try:
        while "WOAH" == "WOAH":  # So that VSCode doesn't detect unreachable code
            Data[
                "QueryURL"
            ] = f"https://discord.com/api/v9/{Data['ChannelType']}/{ID}/messages/search?author_id={UserID}&offset={str(Data['Offset'])}"

            Query = MainSession.get(Data["QueryURL"])

            match Query.status_code:
                case 200:
                    # Save messages
                    Data["Messages"].extend(Query.json()["messages"])

                    # If we're done
                    if len(Data["Messages"]) == Query.json()["total_results"]:
                        raise BreakNestedLoop
                    else:
                        Data["Offset"] += 25
                case 202:  # Channel needs to index
                    time.sleep(2)
                case 404:  # Change type
                    Data[
                        "ChannelType"
                    ] = "channels"  # Group DMs are initially marked as SERVERS
                case 403:  # No access to channel
                    raise BreakNestedLoop
                case 429:  # Ratelimit
                    time.sleep(int(Query.json()["retry_after"]))
    except BreakNestedLoop:
        pass
    return Data["Messages"]


Logs = {"AmountDeleted": 0}


def DeleteMessage(Message):
    Message = Message[0]
    try:
        while True:
            if Message["pinned"] and not DeletePinned:
                raise BreakNestedLoop

            DeleteRequest = MainSession.delete(
                f"https://discord.com/api/v9/channels/{Message['channel_id']}/messages/{Message['id']}"
            )

            match DeleteRequest.status_code:
                case 204:  # Success
                    Logs["AmountDeleted"] += 1
                    raise BreakNestedLoop
                case 403:  # No access anymore
                    Debug(
                        f"No access to channel {Message['channel_id']} in {CurrentServerList[Server]}."
                    )
                    raise BreakNestedLoop
                case 429:  # Ratelimit
                    if "retry_after" in DeleteRequest.json().keys():
                        time.sleep(int(DeleteRequest.json()["retry_after"]))
    except BreakNestedLoop:
        return


match UserSelection:
    case 1:  # Servers

        for Server in Channels["Server"]:

            Debug(f"Querying messages in {CurrentServerList[Server]}...")
            ServerMessages = QueryChannelMessages(Server)

            Debug(f"Beginning to clear messages in {CurrentServerList[Server]}.")

            for Message in ServerMessages:
                DeleteMessage(Message)

            Debug(f"Finished clearing messages in {CurrentServerList[Server]}.")

    case 2:  # DMs

        for DM in Channels["DM"]:

            Debug(f"Querying messages in {MessageIndex[DM]}...")
            ChannelMessages = QueryChannelMessages(DM)

            Debug(f"Beginning to clear messages in {MessageIndex[DM]}.")

            for Message in ChannelMessages:
                Debug(f"Deleting message in {MessageIndex[DM]}.")  # TEMP
                DeleteMessage(Message)

            Debug(f"Finished clearing messages in {MessageIndex[DM]}.")

Debug(f"Deleted {Logs['AmountDeleted']} messages!", "DEBUG", True)
