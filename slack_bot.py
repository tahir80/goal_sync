
import slack
from flask import Flask, request, jsonify, session
from flask_session import Session
from slackeventsapi import SlackEventAdapter
from os import environ
import string
import random
import json
import redis

from GoalSettingBot import SmartGoalSettingChatbot


SLACK_TOKEN = environ.get('SLACK_TOKEN')
SIGNING_SECRET = environ.get('SIGNING_SECRET')
CHANNEL_ID = environ.get('CHANNEL_ID')
REDIS_URL = environ.get('REDIS_URL')



# Initialize the session extension
# app.secret_key = 'your_secret_key'  # Change this to a secure secret key

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url(REDIS_URL)

app.secret_key = "youwillneverknowmysecretkeyunlessyitoldyou"

session.init_app(app)

slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, '/slack/events', app)

client = slack.WebClient(token=SLACK_TOKEN)



try:
    response = client.auth_test()
    print("API call successful!")
    print("Team: ", response['team'])
    print("User: ", response['user'])
except:
    print("error in API call")

user_sessions = {}

@app.route('/', methods=['POST'])
def endpoint():
    if 'challenge' in request.json:
        challenge_value = request.json['challenge']
        return jsonify({'challenge': challenge_value})

    # Handle the actual event logic here

    return jsonify({'status': 'success'})
# hello

@app.route('/test', methods=['GET'])
def test():
    return 'Welcome to the screen!'

@app.route('/interactivity', methods=['POST'])
def interactivity():
    print("I was called here")
    payload = request.form.get("payload")
    print(payload)
    
    # Load the payload JSON string into a Python dictionary
    payload_data = json.loads(payload)

    # Access the 'actions' field from the payload
    actions = payload_data.get('actions', [])
    
    # Loop through the actions to find the desired text
    for action in actions:
        if action.get('text', {}).get('text') == "I want to create a goal first":
            print("User wants to create a goal first!")
            session["goal_set"] = "goal_set"
            print(session["goal_set"])
            # chatbot = SmartGoalSettingChatbot()
            # chatbot.start_conversation()
            # You can perform additional actions here based on the user's choice
            break

    return "", 200

@slack_event_adapter.on('message')
def message(payload):
    print(payload)
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if text == "hi":
        client.chat_postMessage(channel=channel_id, text='Hello World!')
    if session["goal_set"]:
        print("success!")



@slack_event_adapter.on("member_joined_channel")
def handle_team_join(payload):
    print(" new member joined")
    event = payload.get('event', {})

    user_id = event.get('user')

    # to get channel ID for DM
    res = client.conversations_open(users=user_id)
   
    channel_id = res['channel']['id']


    if user_id not in user_sessions:
        # New user joined the channel
        session_id = generate_session_id(10)
        user_sessions[user_id] = session_id
        
        user_info = client.users_info(user=user_id)
        user_name = user_info["user"]["name"]


        message_to_send = {"channel": channel_id,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Hi " +user_name+" :wave:"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Great to see you here!  I'm GoalKeeper, your collaborative goal-setting bot. \n "\
                        "I'm here to help you set and achieve your goals. \n "\
                        "Before we begin, let me provide you with some information about what I can do to assist you."
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "• I will regularly check in with you to track your progress and offer support. Feel free to update me on any changes or difficulties you encounter along the way. \n "\
                        "• You have the flexibility to create new goals, modify existing ones, and track your progress. \n "\
                        "• I'll send you notifications and reminders to keep you on track with your goals."
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Sounds exciting? Let's begin"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Set a goal",
                                "emoji": True
                            },
                            "value": "click_me_123",
                            "action_id": "actionId-0"
                        }
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Inspired me with some ideas",
                                "emoji": True
                            },
                            "value": "click_me_123",
                            "action_id": "actionId-0"
                        }
                    ]
                },

                 {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Show goals set by others",
                                "emoji": True
                            },
                            "value": "click_me_123",
                            "action_id": "actionId-0"
                        }
                    ]
                }
            ]
        }

    client.chat_postMessage(**message_to_send)



@slack_event_adapter.on("reaction_added")
def reaction_added(event_data):
    emoji = event_data["event"]["reaction"]
    print(emoji)


def generate_session_id(length):
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    session_id = ''.join(random.choice(characters) for _ in range(length))
    return session_id


@slack_event_adapter.on("member_left_channel")
def handle_member_left_channel(payload):
    event = payload.get('event', {})
    user_id = event.get('user')
    del user_sessions[user_id]
    print("deleted!")


if __name__ == "__main__":
    # slack_event_adapter.start(port=5000)
    app.run()
