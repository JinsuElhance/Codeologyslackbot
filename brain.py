# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 17:45:02 2018

@author: jelha
"""
import importlib
import time
import pdb
import re
from slackclient import SlackClient
importlib.import_module("commands")

# instantiate Slack client
slack_client = SlackClient("xoxb-482917055219-483238542069-E575j3KoJzdx4fr2DoCDdYW6")
# starterbot's user ID in Slack: value is assigned after the bot starts up
bot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
commandList = {
               "help" : "lists out all commands",
               "excuse (MEETING NAME) (MEETING EXCUSE)": "Submits an excuse an upcoming mandatory meeting",
               "more" : "more commands incoming!"
               }
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
MENTIONS_REGEX = "(?<![\w.-])@([A-Za-z]\w*(?:\.\w+)*)(?=>)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == bot_id:
                return message, event["channel"], event
    return None, None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def parse_direct_mentions(message_text):
    matches = re.findall(MENTIONS_REGEX, message_text)
    return matches if matches else None

def handle_command(command, channel, event):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Here is a list of things that I can do!\n" + helpCommand()

    # Finds and executes the given command, filling in response
    response = None

    # This is where you start to implement more commands!
    if command.startswith("excuse"):
        response = requestExcuse(event)

    if command.startswith("help") :
        response = default_response

    if command.startswith("addAdmin") :
        addAdmin(event)
    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

#def addAdmin(message_event):
#    #Check if current user is an admin
#    if slack_client.api_call("users.info", user = message_event["user"])["user"]["is_admin"] :
#        #Get list of all mentions that aren't @Bolb
#        mentions = parse_direct_mentions(message_event["text"])[1:]
#        for toOp in mentions:
#            print(str(toOp))
#            pdb.set_trace()
#            toOpUser = slack_client.api_call("users.info", user = toOp)
#            if toOpUser["user"]["is_admin"]:
#                return toOpUser["user"]["real_name"] + " is already an admin."
#            else:
#                slack_client.api_call("")

def requestExcuse(message_event):
    """
    A command that takes in a message event and returns a response on whether or not
    the requested user was successfully excused from the meeting.

    Expects: message_event with message_event["text"] having form:

    @Bot excuse @toExcuse <meetingName> <excuseText>

    If sender is admin automatically authorizes excuse and tells toExcuse
    If not, sends admins a request to authorize excuse

    """
    mentions = parse_direct_mentions(message_event["text"])[1:]
    print(mentions)
    words = message_event["text"].split()
    #meetings = getMeetings() This needs to be defined and conencted to Google Calendar!
    meetings = ["GM1", "GM2", "TownHall"]

    if not mentions and not slack_client.api_call("users.info", user = mentions[0]):
        return "You passed in an invalid user or no user at all! Dummy."

    if words[3] not in meetings:
        return "Can't find that meeting"

    if len(words) < 5:
        return "You don't seem to be passing in enough arguments"

    toExcuseID = mentions[0]
    toExcuseName = slack_client.api_call("users.info", user = toExcuseID)["user"]["real_name"]
    excuseText = " ".join(words[4:])
    meeting = words[3]

    if isAdmin(message_event["user"]) :
        response = toExcuseName + " has been excused from " + meeting + " for " + excuseText + "."
        #Open up DM with toExcuse and tells them which meeting they've been excused for.
        im = slack_client.api_call("im.open", user = toExcuseID, return_im = True)
        print(im)
        slack_client.api_call("chat.postMessage", channel = im["channel"]["id"], text = response)
    else:
        im = slack_client.api_call("im.open", user = message_event["user"], return_im = True)
        response = "You have been requested to be excused from " + meeting + " for " + excuseText + "."
        request = toExcuseName + " has requested to be excused from " + meeting + " for " + excuseText + "."
        slack_client.api_call("chat.postMessage", channel = im["channel"]["id"], text = request)

    return response

def isAdmin(user_id):
    return slack_client.api_call("users.info", user = user_id)["user"]["is_admin"]


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Bolb connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        bot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel, event = parse_bot_commands(slack_client.rtm_read())

            if command:
                handle_command(command, channel, event)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")