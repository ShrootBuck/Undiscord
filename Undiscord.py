# Undiscord, by ShrootBuck


# Imports

import json
import math
import requests
import time
from zipfile import ZipFile
from tkinter import filedialog
import tkinter as Tkinter
import os


# Functions

SendWebhook = False
WebhookURL = ""


def Debug(Message, Prefix="DEBUG", IsInput=False):
    FormattedMessage = "[" + Prefix + "]:\t" + Message

    # Behavior determined on whether it's an input or not
    if IsInput:
        return input(FormattedMessage + ":\t")
    else:
        print(FormattedMessage)

    if SendWebhook == True:  # Yields, I know
        try:
            RequestSatisfied = False

            while RequestSatisfied == False:
                Request = requests.post(
                    WebhookURL,
                    data={
                        "content": FormattedMessage,
                        "username": "Undiscord",
                        "avatar_url": "https://raw.githubusercontent.com/ShrootBuck/Undiscord/main/DiscordLogo.png",
                    },
                )
                if Request.status_code != 204:
                    RequestJSON = Request.json()
                    if "retry_after" in RequestJSON.keys():
                        time.sleep(math.ceil(int(RequestJSON["retry_after"]) / 1000))
                    else:
                        RequestSatisfied = True
                else:
                    RequestSatisfied = True
        except:
            pass


def HangProcess():
    while True:
        time.sleep(69)


def ClearConsole():
    Command = "clear"
    if os.name in ("nt", "dos"):  # Windows uses cls
        Command = "cls"

    # Execute command
    os.system(Command)


def PromptFileUpload(
    AllowedFiles, Title="Please select a file", InitialDirectory=os.get_exec_path()
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


# Session for a persistent token
MainSession = requests.session()
MainSession.headers = {"authorization": AuthorizationToken}


# Get the User ID
Debug("Collecting user info...")
UserInfo = MainSession.get("https://discord.com/api/v9/users/@me")
UserID = Username = Discriminator = "I do a little trolling."

if UserInfo.status_code == 200:
    ResponseJSON = UserInfo.json()
    UserID = ResponseJSON["id"]
    Username = ResponseJSON["username"]
    Discriminator = ResponseJSON["discriminator"]

    Debug(f"Successfully logged in to {Username}#{Discriminator}")

else:
    Debug("Failed to get user info, please close the program and try again.", "ERROR")


DeletePinned = Debug("Delete pinned messages? (y/n)", "OPTIONS", True) == "y"


# Unzip the data package

ZipReadFailure = True
ChannelIndexJSON = "I do a little trolling."
CurrentServerListJSON = "I do a little trolling."
ArchivePath = "I do a little trolling."

# Ensure auto-retry
while ZipReadFailure:
    try:
        Debug("Please import your Discord data package.", "OPTIONS")
        ArchivePath = PromptFileUpload(
            [("ZIP Files", "*.zip")], "Please import your Discord data package."
        )
        ChannelIndexJSON = ReadFromZip(ArchivePath, "messages/index.json")
        CurrentServerListJSON = ReadFromZip(ArchivePath, "servers/index.json")

        ZipReadFailure = False

    except Exception as ReadZIPException:
        Debug("ReadZIPException! Something went wrong.", "ERROR")
        ZipReadFailure = True  # Shouldn't be necessary, but good practice

ChannelIndex = json.loads(ChannelIndexJSON)
CurrentServerList = json.loads(CurrentServerListJSON)

# Get the channels to index
Channels = {"DM": [], "Server": [], "GroupChat": []}

# Webhook settings
WebhookURL = Debug(
    "Enter a Discord webhook URL to forward the console to, or leave blank for none",
    "OPTIONS",
    True,
)
SendWebhook = WebhookURL.strip() != ""

ClearConsole()

# DMs

for Index in ChannelIndex:
    if ChannelIndex[Index] == None:
        continue  # Not this channel

    if ChannelIndex[Index].startswith("Direct Message with"):
        Channels["DM"].append(Index)
    else:
        ChannelData = json.loads(
            ReadFromZip(ArchivePath, f"messages/c{str(Index)}/channel.json")
        )
        if ChannelData["type"] == 3:
            Channels["DM"].append(Index)


# Servers
for Index in CurrentServerList.keys():
    Channels["Server"].append(Index)


# Easy way to break nested loops
class BreakNestedLoop(Exception):
    pass


def QueryChannelMessages(ID):
    Data = {"Offset": 0, "Messages": [], "QueryURL": "", "ChannelType": "channels"}

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
                    if len(Query.json()["messages"]) < 25:
                        raise BreakNestedLoop
                    else:
                        Data["Offset"] += 25
                case 202:  # Channel needs to index
                    RetryAfter = Query.json()["retry_after"]
                    time.sleep(RetryAfter)
                case 404:  # Change type

                    if Data["ChannelType"] == "guilds":
                        raise BreakNestedLoop
                    else:
                        Data["ChannelType"] = "guilds"
                case 403:  # No access anymore
                    raise BreakNestedLoop

                case 404:
                    raise BreakNestedLoop

                case 429:  # Ratelimit
                    if "retry_after" in Query.json().keys():
                        RetryAfter = math.ceil(Query.json()["retry_after"])
                        Debug(f"Pausing for {RetryAfter} seconds...", "RATE-LIMIT")
                        time.sleep(int(RetryAfter))
                    else:
                        raise BreakNestedLoop
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

                    Debug("Deleted message")

                    raise BreakNestedLoop
                case 403:  # No access anymore
                    raise BreakNestedLoop

                case 404:
                    raise BreakNestedLoop

                case 429:  # Ratelimit
                    if "retry_after" in DeleteRequest.json().keys():
                        RetryAfter = math.ceil(DeleteRequest.json()["retry_after"])
                        Debug(f"Pausing for {RetryAfter} seconds...", "RATE-LIMIT")
                        time.sleep(int(RetryAfter))
                    else:
                        raise BreakNestedLoop
    except BreakNestedLoop:
        return


# Servers
for Server in Channels["Server"]:

    Debug(f"Sending query for messages in {CurrentServerList[Server]}")
    ServerMessages = QueryChannelMessages(Server)

    Debug(f"Beginning to clear messages in {CurrentServerList[Server]}")

    for Message in ServerMessages:
        DeleteMessage(Message)

    Debug(f"Finished clearing messages in {CurrentServerList[Server]}")


# DMs
for DM in Channels["DM"]:

    Debug(f"Sending query for messages in {ChannelIndex[DM]}")
    ChannelMessages = QueryChannelMessages(DM)

    Debug(f"Beginning to clear messages in {ChannelIndex[DM]}")

    for Message in ChannelMessages:
        DeleteMessage(Message)

    Debug(f"Finished clearing messages in {ChannelIndex[DM]}")


Debug(f"Deleted {Logs['AmountDeleted']} messages!")

HangProcess()
