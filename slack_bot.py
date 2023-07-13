
import slack
from flask import Flask, request, jsonify
from slackeventsapi import SlackEventAdapter
import os
import string
import random
import json

SLACK_TOKEN = "xoxb-5328365176998-5334989540850-Ti4HW1S5gdAA6vHEUINOOHOK"
SIGNING_SECRET = "22238f2e2ddafaa7b8154bd7510cee23"
CHANNEL_ID = "C059ECX4JA3"

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, '/slack/events', app)

client = slack.WebClient(token=SLACK_TOKEN)

user_sessions = {}

@app.route('/', methods=['POST'])
def endpoint():
    if 'challenge' in request.json:
        challenge_value = request.json['challenge']
        return jsonify({'challenge': challenge_value})

    # Handle the actual event logic here

    return jsonify({'status': 'success'})
# hello


@app.route('/interactivity', methods=['POST'])
def interactivity():
    print("I was called here")
    payload = request.form.get("payload")
    print(payload)
    return "", 200

@slack_event_adapter.on('message')
def message(payload):
    # print(payload)
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if text == "hi":
        client.chat_postMessage(channel=channel_id, text='Hello World!')


@slack_event_adapter.on("member_joined_channel")
def handle_team_join(payload):
    print(" new member joined")
    event = payload.get('event', {})
    user_list = client.users_list()

    #count the number of members
    # Parse the JSON response
    response_data = json.loads(user_list)

    # Get the list of members from the response
    members = response_data.get("members", [])

    # Count the number of members
    member_count = len(members)

    # Print the count of members
    print(f"The number of users: {member_count}")

    user_id = event.get('user')

    # to get channel ID for DM
    res = client.conversations_open(users=user_id)
   
    channel_id = res['channel']['id']

    if user_id not in user_sessions:
        # New user joined the channel
        session_id = generate_session_id(10)
        user_sessions[user_id] = session_id
        # bot_response = detect_intent_texts("reactpageagent-jypw", session_id,
                                        #    "ice breaker", "en-US")

        # detect_intent_texts("reactpageagent-jypw", session_id, \
        #                                "ice breaker", "en-US")

        # print(bot_response.query_result.fulfillment_text)
        # for response in bot_response:
        #     client.chat_postMessage(channel=channel_id, text=response[0])
        

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
                                "text": "I want to create a goal first",
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
                                "text": "Show goals by others",
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


def detect_intent_texts(project_id, session_id, text, language_code):
    """Returns the result of detect intent with texts as inputs.
    Using the same `session_id` between requests allows continuation
    of the conversation."""
    # from google.cloud import dialogflow
    # import dialogflow_v2 as dialogflow
    from google.cloud import dialogflow

    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    print("Session path: {}\n".format(session))

    text_input = dialogflow.TextInput(text=text, language_code=language_code)

    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    print("Fulfillment text: {}\n".format(response.query_result))
    # return response.query_result.fulfillment_text

    fulfillment_messages = response.query_result.fulfillment_messages
    text_responses = []

    for message in fulfillment_messages:
        if message.text:
            text_responses.append(message.text.text)

    return text_responses


@slack_event_adapter.on("member_left_channel")
def handle_member_left_channel(payload):
    event = payload.get('event', {})
    user_id = event.get('user')
    del user_sessions[user_id]
    print("deleted!")


if __name__ == "__main__":
    # slack_event_adapter.start(port=5000)
    app.run()
