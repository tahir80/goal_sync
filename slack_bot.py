
import slack
from flask import Flask, abort, request, jsonify, session
from flask_session import Session
from slackeventsapi import SlackEventAdapter
from slack.errors import SlackApiError
from os import environ
import string
import random
import json
import redis
import asyncio

from GoalSettingBot import SmartGoalSettingChatbot
# from RedisSessionStore import RedisDataStore
from Ingestion import ingest_docs




SLACK_TOKEN = environ.get('SLACK_TOKEN')
SIGNING_SECRET = environ.get('SIGNING_SECRET')
CHANNEL_ID = environ.get('CHANNEL_ID')

REDIS_HOST = environ.get('REDIS_HOST')
REDIS_PORT = environ.get('REDIS_PORT')
REDIS_PASS = environ.get('REDIS_PASS')


REDIS_POOL = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASS,
    decode_responses=True  # Set to True to automatically decode responses to strings
)



# Initialize the session extension
# app.secret_key = 'your_secret_key'  # Change this to a secure secret key

app = Flask(__name__)

app.secret_key = "youwillneverknowmysecretkeyunlessyitoldyou"

slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, '/slack/events', app)

client = slack.WebClient(token=SLACK_TOKEN)

chatbot = SmartGoalSettingChatbot()

# redis_store = RedisDataStore(REDIS_HOST, REDIS_PORT, REDIS_PASS)

try:
    response = client.auth_test()
    print("API call successful!")
    print("Team: ", response['team'])
    print("User: ", response['user'])
except:
    print("error in API call")

user_sessions = {} # replace it with redis

@app.route('/', methods=['POST'])
def endpoint():
    if 'challenge' in request.json:
        challenge_value = request.json['challenge']
        return jsonify({'challenge': challenge_value})

    # Handle the actual event logic here

    return jsonify({'status': 'success'})
# hello

@app.route('/slack/events', methods=['POST'])
def checkEvents():
    print("from: checkEvents")
    print(request.json)
    return jsonify({'response': request.json})

@app.route('/test', methods=['GET'])
def test():
    return 'Welcome to the screen!'


#https://renzolucioni.com/serverless-slash-commands-with-python/


@app.route('/interactivity', methods=['POST'])
def interactivity():
    print("I was called here")
    payload = request.form.get("payload")

    # Get the channel ID from the 'container' object
    print(payload)

    # Load the payload JSON string into a Python dictionary
    payload_data = json.loads(payload)

    channel_id = payload_data['container']['channel_id']

    # Access the 'actions' field from the payload
    actions = payload_data.get('actions', [])
    
    # Loop through the actions to find the desired text
    for action in actions:
        if action.get('text', {}).get('text') == "Set a goal":
            print("success. I want to create a goal")
            r = redis.Redis(connection_pool=REDIS_POOL)
            # redis_store.set_data("_set_goal_", "set_goal", 300)
            print("User wants to create a goal first!")
            r.set('_goal_set_', 'goal_set')
            r.expire("_goal_set_", 3600)

            client.chat_postMessage(channel=channel_id, text=chatbot.kick_start())
            
            # You can perform additional actions here based on the user's choice
            break

    return "", 200

# def is_request_valid(request):
#     print(request.form['token'])
#     is_token_valid = request.form['token'] == environ.get('SLACK_TOKEN')
#     is_team_id_valid = request.form['team_id'] == environ['SLACK_TEAM_ID']

#     return is_token_valid and is_team_id_valid


@app.route('/triggerchat', methods=['POST'])
def triggerchat():

    # payload = request.form.get("payload")
    # print(payload)
    # payload_data = json.loads(payload)

    # channel_id = payload_data['container']['channel_id']

    payload = request.form.to_dict()
    print(payload)

    channel_id = payload.get('channel_id')

    r = redis.Redis(connection_pool=REDIS_POOL)
    r.set('_goal_set_', 'goal_set')
    r.expire("_goal_set_", 3600)

    # chatbot.reset_memory()

    client.chat_postMessage(channel=channel_id, text=chatbot.kick_start())

    return jsonify(
        text='setgoal',
    )


@app.route('/endgoal', methods=['POST'])
def endgoal():
    payload = request.form.to_dict()
    channel_id = payload.get('channel_id')
    r = redis.Redis(connection_pool=REDIS_POOL)
    # r.delete('_goal_set_')
    if r.exists("_goal_set_") == 1:
        r.delete('_goal_set_')
    
    print(chatbot.get_conversation_history())
    # get the current event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ingest_docs("chat-history-index", chatbot.get_conversation_history()))

    return jsonify(
        text='endgoal',
    )


@slack_event_adapter.on("app_mention")
def on_app_mention(data):
    channel_id = data["event"]["channel"]
    print(data)
    print(channel_id)
    user_id = data["event"]["user"]
    message = f"Hello, <!channel>! We are starting a group conversation. Please join in!"
    response = client.auth_test()
    if response['user_id']!= user_id:
        message = "Hello, <!channel>! How can I help you?"
        
        # Post the group conversation message in the public channel
        client.chat_postMessage(channel=channel_id, text=message)


# def get_bot_id():
#     response = client.auth_test()
#     return response['user_id']

# BOT_ID = get_bot_id()

@slack_event_adapter.on('message')
def message(payload):
    print(payload)
    # session.get('goal_set', 'not set')
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    # if text == "hi":
    #     client.chat_postMessage(channel=channel_id, text='Hi, How can I help you?')
    

    r = redis.Redis(connection_pool=REDIS_POOL)
    
    print("user id is "+ user_id)
    response = client.auth_test()
    print("user 2 id is"+response['user_id'])
    # return response['user_id']

    value = r.get("_goal_set_")
    # if value is not None:
    #     value = value.decode('utf-8')
    
    # print("session value" + value)
    if value == "goal_set" and response['user_id'] != user_id:
        print("I was called from the combined logical conditions")
        message = chatbot.get_next_predict(text)
        client.chat_postMessage(channel=channel_id, text=message)
        if text.lower() == "exit" or text.lower() == "end":
            print("Conversation ended. Goodbye!")


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
