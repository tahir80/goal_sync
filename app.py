import os
import re
import random
import string
import requests
import dialogflow
from flask import Flask, request, jsonify, render_template, session

from google.protobuf.json_format import MessageToDict


from logging import INFO
from typing import Dict
from flask.logging import create_logger
from dialogflow_fulfillment import WebhookClient, QuickReplies, Context

from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
# from flask_redis import Redis
import redis

import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or \
    'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'
# app.secret_key = os.urandom(24)
# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# app.secret_key = 'BAD_SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:topsecret@localhost/goalkeeper'
uri = os.getenv("DATABASE_URL")  # or other relevant config var
# if uri.startswith("postgres://"):
#     uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri

# app.config['SESSION_TYPE'] = 'sqlalchemy'
# app.config['SESSION_TYPE'] = 'filesystem'

REDIS_URL = "redis://:p98b2bc14b0283540c464c82a9343508f90b432e0400386a5769afad5dd84140d@ec2-99-80-230-229.eu-west-1.compute.amazonaws.com:24159"

db = SQLAlchemy(app)

# app.config['SESSION_SQLALCHEMY'] = db

# app.config['SESSION_REDIS'] = redis.from_url(os.getenv("REDIS_URL"))
# store = redis.Redis.from_url(os.getenv("REDIS_URL"))


# Session(app)

#---------------SESSION STORAGE--------------------------------#

class SessionStore:
    """Store session data in Redis."""

    def __init__(self, token, url='redis://:p98b2bc14b0283540c464c82a9343508f90b432e0400386a5769afad5dd84140d@ec2-99-80-230-229.eu-west-1.compute.amazonaws.com:24159', ttl=3600):
        self.token = token
        self.redis = redis.Redis.from_url(url)
        self.ttl = ttl

    def set(self, key, value):
        self.refresh()
        return self.redis.hset(self.token, key, value)

    def get(self, key):
        self.refresh()
        return self.redis.hget(self.token, key)

    def incr(self, key):
        self.refresh()
        return self.redis.hincrby(self.token, key, 1)

    def refresh(self):
        self.redis.expire(self.token, self.ttl)

#----------------------THE END---------------------------------#

# have u used sess anytwhere ? nope

######################### MODEL CLASSES ##################################

class TASK(db.Model):
    __tablename__ = 'TASK'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    status = db.Column(db.String(500))
    time_stamp = db.Column(db.DateTime, default = datetime.datetime.utcnow())

    def __init__(self, title, status):
        self.title = title
        self.status = status


class SESSION(db.Model):
    __tablename__ = 'SESSION'
    id = db.Column(db.Integer, primary_key = True)

    #relationship
    t_id = db.Column(db.Integer, db.ForeignKey('TASK.id'))
    key = db.Column(db.String(500))
    time_stamp = db.Column(db.DateTime, default = datetime.datetime.utcnow())

    def __init__(self, t_id, key):
        self.t_id = t_id
        self.key = key

class USER(db.Model):
    __tablename__ = 'USER'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    passcode = db.Column(db.String(100), nullable = False)
    time_stamp = db.Column(db.DateTime, default = datetime.datetime.utcnow())

    def __init__(self, passcode, name):
        self.name = name
        self.passcode = passcode


class QUIZ(db.Model):

    __tablename__ = 'QUIZ'
    id = db.Column(db.Integer, primary_key = True)
    u_id = db.Column(db.Integer, db.ForeignKey('USER.id'))
    t_id = db.Column(db.Integer, db.ForeignKey('TASK.id'))
    s_id = db.Column(db.Integer, db.ForeignKey('SESSION.id'))

    intent = db.Column(db.String(500))
    queryText = db.Column(db.String(1000))

    time_stamp = db.Column(db.DateTime, default = datetime.datetime.utcnow())

    def __init__(self, intent, queryText, u_id, t_id, s_id):
        self.intent = intent
        self.queryText = queryText
        self.u_id = u_id
        self.t_id = t_id
        self.s_id = s_id

class GOAL(db.Model):

    __tablename__ = 'GOAL'
    id = db.Column(db.Integer, primary_key = True)
    u_id = db.Column(db.Integer, db.ForeignKey('USER.id'))
    t_id = db.Column(db.Integer, db.ForeignKey('TASK.id'))
    s_id = db.Column(db.Integer, db.ForeignKey('SESSION.id'))

    goal_name = db.Column(db.String(500))
    specific = db.Column(db.String(1000))
    measurable = db.Column(db.String(1000))
    actionable = db.Column(db.String(1000))
    realistic = db.Column(db.String(1000))
    timely = db.Column(db.String(1000))
    msg = db.Column(db.String(1000))

    time_stamp = db.Column(db.DateTime, default = datetime.datetime.utcnow())


    def __init__(self, u_id, t_id, s_id, goal_name, specific, measurable, actionable, realistic, timely):
        self.u_id = u_id
        self.t_id = t_id
        self.s_id = s_id
        self.goal_name = goal_name
        self.specific = specific
        self.measurable = measurable
        self.actionable = actionable
        self.realistic = realistic
        self.timely = timely

#############################END OF MODEL CLASSES############################



logger = create_logger(app)
logger.setLevel(INFO)

@app.route('/set/<key>/<value>')
def set_session(key, value):
    # session["testing"] = 123
    session[key] = value
    # return session
    return session[key]

@app.route('/get/<key>')
def get_session(key):
    # print(session['user_id'])
    return session['key']
# yo a eavel this outncu



def detect_intent_with_parameters(project_id, session_id, query_params, language_code, user_input):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text = user_input
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    # response = session_client.detect_intent(session=session, query_input=query_input, query_params=query_params)
    response = session_client.detect_intent(session=session, query_input=query_input)
    return response


@app.route('/')
def hello_world():
    session['testing'] = "i was set from the main route"
    return render_template('index.html')


@app.route('/welcomeIntent', methods=["Post"])
def welcomeIntent():
    print(request.form['sess_id'])


    GOOGLE_AUTHENTICATION_FILE_NAME = "credentials/key.json"
    current_directory = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(current_directory, GOOGLE_AUTHENTICATION_FILE_NAME)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path

    client = dialogflow.SessionsClient()
    session = client.session_path('reactpageagent-jypw', request.form['sess_id'])

    event_input = dialogflow.types.EventInput(name='WELCOME', language_code='en-US')
    query_input = dialogflow.types.QueryInput(event=event_input)
    response = client.detect_intent(session=session, query_input=query_input)
    result = MessageToDict(response)
    #print(result)


    #response = {"message": result['queryResult']['intent'], "payload": None}

    return jsonify(result['queryResult'])



@app.route('/chat', methods=["Post"])
def chat():


    # print(session.get('testing'))
    # session['test'] = "tahir"
    input_text = request.form['message']

    if len(input_text) > 255:
        input_text = input_text[:255]


    GOOGLE_AUTHENTICATION_FILE_NAME = "credentials/key.json"
    current_directory = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(current_directory, GOOGLE_AUTHENTICATION_FILE_NAME)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path

    GOOGLE_PROJECT_ID = "reactpageagent-jypw"
    session_id = request.form['sess_id']
    print(session.items())
    print(session.get('id'))
    print(session.get('username'))
    context_short_name = "does_not_matter"

    context_name = "projects/" + GOOGLE_PROJECT_ID + "/agent/sessions/" + session_id + "/contexts/" + context_short_name.lower()

    parameters = dialogflow.types.struct_pb2.Struct()

    context_1 = dialogflow.types.context_pb2.Context(
        name=context_name,
        lifespan_count=2,
        parameters=parameters
    )
    query_params_1 = {"contexts": [context_1]}

    language_code = 'en'

    response = detect_intent_with_parameters(
        project_id=GOOGLE_PROJECT_ID,
        session_id=session_id,
        query_params=query_params_1,
        language_code=language_code,
        user_input=input_text
    )
    result = MessageToDict(response)
    print(result['queryResult'])

    return jsonify(result['queryResult'])


def handler(agent: WebhookClient) -> None:
    """Handle the webhook request.."""
    #agent.followup_event = 'WELCOME'
    # agent.add('How are you feeling today?')
    # agent.add(QuickReplies(quick_replies=['Happy :)', 'Sad :(']))


def get_Name_ID(agent):

    store = SessionStore(agent.session, REDIS_URL)

    task = TASK.query.filter_by(status="active").first()

    #add new user
    if not USER.query.filter_by(passcode = agent.parameters["id"]).first():
        user = USER(agent.parameters["id"], agent.parameters["name"])
        db.session.add(user)
        db.session.flush()
        store.set('u_id', user.id)
        db.session.commit()
    else:
        user = USER.query.filter_by(passcode=agent.parameters["id"]).first()
        store.set('u_id', user.id)

    #create a unique session for the user
    user_session = SESSION(task.id, agent.session)
    db.session.add(user_session)
    db.session.flush()
    store.set('s_id', user_session.id)
    db.session.commit()

    store.set('usrName', agent.parameters["name"])
    print('----get_Name_ID------')
    print(store.get('usrName'))
    print(store.get('u_id'))
    print(store.get('s_id'))
    # context.set(name = 'sessiondata', lifespan_count=300, parameters={"user_id": agent.parameters["id"], "session_id": user_session.id})


# def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
#         return ''.join(random.choice(chars) for _ in range(size))
# def __init__(self, u_id, t_id, s_id, goal_name, specific, measurable, actionable, realistic, timely):
def goalName(agent):

    task = TASK.query.filter_by(status="active").first()

    store = SessionStore(agent.session, REDIS_URL)
    print('----goalName------')
    name = store.get('usrName')
    name = name.decode("utf-8")
    print(name)
    uid = store.get('u_id')
    uid = uid.decode("utf-8")
    print(uid)
    sid = store.get('s_id')
    sid = sid.decode("utf-8")
    print(sid)

    goal = GOAL(uid, task.id, sid, agent.parameters["goalName"], "", "", "", "", "")
    db.session.add(goal)
    db.session.flush()
    # session['goal_id'] = goal.id
    store.set('goal_id', goal.id)
    # users['id']['goal_id'] = goal.id
    db.session.commit()
# def __init__(self, intent, queryText, u_id, t_id, s_id):
def saveQuizData(agent):
    print('/////--------agent.action------/////')
    print(agent.action)
    print(agent.query)
    store = SessionStore(agent.session, REDIS_URL)
    uid = store.get('u_id')
    uid = uid.decode("utf-8")
    sid = store.get('s_id')
    sid = sid.decode("utf-8")
    task = TASK.query.filter_by(status="active").first()
    if agent.action == "quiz4.action":
        quiz = QUIZ(agent.action, agent.parameters['quiz4text'], uid, task.id, sid)
        db.session.add(quiz)
        db.session.commit()
    else:
        quiz = QUIZ(agent.action, agent.query, uid, task.id, sid)
        db.session.add(quiz)
        db.session.commit()


def savegoaldata(agent):
    store = SessionStore(agent.session, REDIS_URL)
    uid = store.get('u_id')
    uid = uid.decode("utf-8")
    sid = store.get('s_id')
    sid = sid.decode("utf-8")
    gid = store.get('goal_id')
    gid = gid.decode("utf-8")
    task = TASK.query.filter_by(status="active").first()

    goal = GOAL.query.filter_by(id=gid).first()
    if agent.action == "goal.setting.specific" or agent.action == "goal.setting.rephrase":
        goal.specific = agent.query
        db.session.add(goal)
        db.session.commit()

    if agent.action == "goal.setting.measurable" or agent.action == "goal.setting.measurable.rephrase":
        goal.measurable = agent.query
        db.session.add(goal)
        db.session.commit()

    if agent.action == "goal.setting.actionable" or agent.action == "goalsettingactionable-rephrase":
        goal.actionable = agent.query
        db.session.add(goal)
        db.session.commit()

    if agent.action == "goal.setting.realistic" or agent.action == "goal.setting.realistic.rephrase":
        goal.realistic = agent.query
        db.session.add(goal)
        db.session.commit()

    if agent.action == "goal.setting.timely" or agent.action == "goalsettingtimely-rephrase":
        goal.timely = agent.query
        db.session.add(goal)
        db.session.commit()

#   if(intent === "goal.setting.rephrase" ||
# intent === "goal.setting.measurable.rephrase" ||
# intent === "goal.setting.actionable - rephrase" ||
# intent === "goal.setting.realistic - rephrase" ||
# intent === "goal.setting.timely - rephrase")
@app.route('/rephrase', methods=["Post"])
def rephrase():
    data = request.get_json()
    store = SessionStore("projects/reactpageagent-jypw/agent/sessions/" + data['sid'], REDIS_URL)
    print(data['sid'])
    gid = store.get('goal_id')
    gid = gid.decode("utf-8")
    goal = GOAL.query.filter_by(id=gid).first()
    result = ''
    if data['intentData'] == 'goal.setting.rephrase':
        result = goal.specific
    if data['intentData'] == 'goal.setting.measurable.rephrase':
        result = goal.measurable
    if data['intentData'] == 'goal.setting.actionable - rephrase':
        result = goal.actionable
    if data['intentData'] == 'goal.setting.realistic - rephrase':
        result = goal.realistic
    if data['intentData'] == 'goal.setting.timely - rephrase':
        result = goal.timely

    if data['intentData'] == 'goal.setting.measurable':
        if goal.measurable != '':
            result = goal.measurable
        else:
            result = goal.specific

    if data['intentData'] == 'goal.setting.actionable':
        if goal.actionable != '':
            result = goal.actionable
        else:
            result = goal.measurable

    if data['intentData'] == 'goal.setting.realistic':
        if goal.realistic != '':
            result = goal.realistic
        else:
            result = goal.actionable

    if data['intentData'] == 'goal.setting.timely':
            if goal.timely != '':
                result = goal.timely
            else:
                result = goal.realistic
    if data['intentData'] == 'downloadable':
        result = goal.timely

    if data['intentData'] == 'change.request':
        result = goal.timely

    return jsonify(result)



def changeRequest(agent):
    store = SessionStore(agent.session, REDIS_URL)
    gid = store.get('goal_id')
    gid = gid.decode("utf-8")
    goal = GOAL.query.filter_by(id=gid).first()

    goal.timely = agent.query
    db.session.add(goal)
    db.session.commit()



def setAnotherGoal(agent):
    store = SessionStore(agent.session, REDIS_URL)

    task = TASK.query.filter_by(status="active").first()
    user_session = SESSION(task.id, agent.session)
    db.session.add(user_session)
    db.session.flush()
    store.set('s_id', user_session.id)
    db.session.commit()

    uid = store.get('u_id')
    uid = uid.decode("utf-8")

    goal = GOAL(uid, task.id, user_session.id, agent.parameters["name"], agent.parameters["specific"], agent.parameters["measurable"], agent.parameters["actionable"], agent.parameters["realistic"], agent.parameters["timely"])

    db.session.add(goal)
    db.session.flush()
    store.set('goal_id', goal.id)
    db.session.commit()

@app.route('/webhook', methods=['POST', 'GET'])
def webhook() -> Dict:
    Quiz_actions = ['quiz1.action', 'quiz1.quiz1-custom', 'quiz1.quiz1-custom-2', \
                'quiz2.action', 'quiz2.quiz2-custom', 'quiz2.quiz2-custom-2', \
                'quiz3.action', 'quiz3.quiz3-custom', 'quiz3.quiz3-custom-2', \
                'quiz4.action' ,\
                'quiz5.action', 'quiz5.quiz5-custom', 'quiz5.quiz5-custom-2', \
                'quiz6.action', 'quiz6.quiz6-custom', 'quiz6.quiz6-custom-2', \
                'quiz7.action', 'quiz7.quiz7-custom', 'quiz7.quiz7-custom-2', \
                'quiz8.action', 'quiz8.quiz8-custom', 'quiz8.quiz8-custom-2', \
                'quiz9.action', 'quiz9.quiz9-custom', 'quiz9.quiz9-custom-2',\
                'quiz10.action']

    # Get WebhookRequest object
    request_ = request.get_json(force=True)

    # Log request headers and body
    logger.info(f'Request headers: {dict(request.headers)}')
    logger.info(f'Request body: {request_}')

    # Handle request
    agent = WebhookClient(request_)
    # print("contexts: ", agent.contexts)

    action = request_.get('queryResult').get('action')

    if action  == "get.secret.key":
        agent.handle_request(get_Name_ID)

    if action  == "goal.setting.name":
        agent.handle_request(goalName)

    if action in Quiz_actions:
        agent.handle_request(saveQuizData)

    if action == "goal.setting.specific" or action == "goal.setting.rephrase" or \
       action == "goal.setting.measurable" or action == "goal.setting.measurable.rephrase" or \
       action == "goal.setting.actionable" or action == "goalsettingactionable-rephrase" or \
       action == "goal.setting.realistic" or action == "goal.setting.realistic.rephrase" or \
       action == "goal.setting.timely" or action == "goalsettingtimely-rephrase":
        agent.handle_request(savegoaldata)

    if action == "change.request":
        agent.handle_request(changeRequest)

    if action == "set.another.goal":
        agent.handle_request(setAnotherGoal)




    #Log WebhookResponse object
    # logger.info(f'Response body: {agent.response}')
    print('/////------agent.response---/////')
    print(agent.response)


    return agent.response


if __name__ == '__main__':
    # app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run()
