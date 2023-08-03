# GoalKeeper - Collaborative Goal-Setting Bot

GoalKeeper is a collaborative goal-setting bot designed to assist you in setting and achieving your goals. Whether you're working on personal projects, team objectives, or professional development, GoalKeeper is here to support you every step of the way.



# Setup a starter code from Github

Follow these steps to get started with GoalKeeper:

1. Clone the repository: git clone [https://github.com/tahir80/goal_sync.git](https://github.com/tahir80/goal_sync.git)
2. cd *goal_sync*
3. Install the required dependencies: `pip install -r requirements.txt`
4. Before setting up the Slack event subscription, you should deploy your code on Heroku to obtain a static URL for your app. This static URL will be used later when configuring the Slack event subscription. Follow the steps below to create a Heroku app and deploy your code:
   1. **Create a Heroku Account:** If you don't have a Heroku account, sign up for one at Heroku.
   2. **Install Heroku CLI:** Download and install the Heroku Command Line Interface (CLI) from Heroku CLI.
   3. **Login to Heroku:** Open a terminal or command prompt and log in to Heroku using the command: heroku login
   4. **Initialize Git:** If your code is not already in a Git repository, navigate to your project directory and initialize Git: `git init`
`git add .`
`git commit -m "Initial commit"`
   5. **Create a Heroku App:** Create a new Heroku app using the Heroku CLI: heroku create your-app-name
   6. **Deploy to Heroku:** Deploy your code to Heroku: `git push heroku master` This will automatically build and deploy your app on Heroku. Obtain Static URL: Once the deployment is successful, you will get a static URL for your app. It will be in the format https://your-app-name.herokuapp.com/
   7. **Set up environment variables:**

You need to set up the following environment variables on Heroku (https://devcenter.heroku.com/articles/config-vars):

- `SLACK_TOKEN`: Your Slack bot token.
- `SIGNING_SECRET`: Your Slack app signing secret.
- `CHANNEL_ID`: The ID of the channel where you want GoalKeeper to operate.
- `REDIS_HOST`: Redis server host.
- `REDIS_PORT`: Redis server port.
- `REDIS_PASS`: Redis server password
- `OPENAI_API_KEY`: Open AI key
- `PINECONE_API_KEY`: Pinecone API key
- `PINECONE_ENVIRONMENT_REGION`

# Creating a Slack App


Follow these steps to create a Slack bot and add it to a channel so that it can interact with users and respond to messages:

## Step 1: Create a Slack App

1. Go to the [Slack API website](https://api.slack.com/apps) and sign in to your Slack workspace or create a new one.

2. Click on "Create an App" to start creating a new Slack app.

3. Give your app a name and select the workspace where you want to install it.

## Step 2: Set Up Bot User

1. In the Slack app settings, navigate to the "Bot Users" section.

2. Click on "Add a Bot User" and follow the prompts to create a new bot user for your app.

## Step 3: Install App to Workspace

1. Go to the "Install App" section in the Slack app settings.

2. Click on "Install App to Workspace" to add your app to the Slack workspace.

3. Review the permissions requested by your app and click "Allow" to grant them.

## Step 4: Obtain OAuth Access Token

1. In the Slack app settings, navigate to the "OAuth & Permissions" section.

2. Under the "OAuth Tokens for Your Workspace" section, you will find your OAuth access token. Copy it and keep it secure as it will be used to authenticate your bot with the Slack API.

## Step 5: Add Bot to a Channel

1. In Slack, go to the channel where you want to add the bot.

2. Invite the bot to the channel by mentioning its name with an "@" symbol. For example, "@your-bot-name".

## Step 6: Enable scopes
From the "OAuth and Permissions", enable the following scopes

[app_mentions:read](https://api.slack.com/scopes/app_mentions:read)
[channels:history](https://api.slack.com/scopes/channels:history)
[channels:read](https://api.slack.com/scopes/channels:read)
[chat:write](https://api.slack.com/scopes/chat:write)
[groups:history](https://api.slack.com/scopes/groups:history)
[groups:read](https://api.slack.com/scopes/groups:read)
[im:history](https://api.slack.com/scopes/im:history)
[im:read](https://api.slack.com/scopes/im:read)
[im:write](https://api.slack.com/scopes/im:write)
[mpim:history](https://api.slack.com/scopes/mpim:history)
[mpim:read](https://api.slack.com/scopes/mpim:read)
[mpim:write](https://api.slack.com/scopes/mpim:write)
[reactions:read](https://api.slack.com/scopes/reactions:read)
[team:read](https://api.slack.com/scopes/team:read)
[users:read](https://api.slack.com/scopes/users:read)

And from the "event subscription", add the following scopes

[app_mention](https://api.slack.com/events/app_mention)
[member_joined_channel](https://api.slack.com/events/member_joined_channel)
[member_left_channel](https://api.slack.com/events/member_left_channel)
[message.channels](https://api.slack.com/events/message.channels)
[message.groups](https://api.slack.com/events/message.groups)
[message.im](https://api.slack.com/events/message.im)
[message.mpim](https://api.slack.com/events/message.mpim)
[reaction_added](https://api.slack.com/events/reaction_added)


# Description of main features
## SmartGoalSettingChatbot Class

The `SmartGoalSettingChatbot` class is a chatbot designed to guide users in setting specific, measurable, achievable, relevant, and time-bound (SMART) goals. The chatbot uses the Langchain library, which leverages OpenAI language models for natural language processing.

### Class Features

- `__init__`: Initializes the chatbot and sets up the necessary configurations, including the OpenAI API key and conversation memory.
- `kick_start()`: Initiates the conversation by providing an introductory message to users.
- `get_next_predict(input)`: Continues the conversation based on the user's input and provides responses accordingly.
- `get_conversation_history()`: Retrieves the conversation history stored in the memory of the chatbot.

### Usage

1. Create an instance of the `SmartGoalSettingChatbot` class.

2. Call `kick_start()` to initiate the conversation with a welcome message.

3. Use `get_next_predict(input)` to interact with the chatbot and get responses based on user input.

4. Retrieve the conversation history using `get_conversation_history()` if needed.


### Ingestion Class for Pinecone Indexing

The `Ingestion` class handles the process of ingesting chat history data into a Pinecone index for efficient retrieval and searching. It leverages the Langchain library and the Pinecone API to accomplish this task.

#### Class Features

- `ingest_docs(index_name, chat_history)`: Asynchronous function that ingests chat history data into a Pinecone index.
  - Checks if the index already exists, if not, creates a new index.
  - Initializes embeddings using OpenAI language models.
  - Splits chat history into smaller chunks using RecursiveCharacterTextSplitter.
  - Adds the chat history to the index if it's empty or updates the embeddings if the index is not empty.

#### Usage

1. Make sure you have the necessary environment variables set, including `PINECONE_API_KEY` and `PINECONE_ENVIRONMENT_REGION`, which are used for Pinecone initialization.

2. Call the `ingest_docs(index_name, chat_history)` method to add chat history to the Pinecone index.

   Note: This function is asynchronous and should be awaited when called.

 **Note: Currently, I am planning to use Celery to improve the asynchronous call to Pinecone for storing vectors**



