# GoalKeeper - Collaborative Goal-Setting Bot

![GoalKeeper Logo](https://example.com/goalkeeper_logo.png)

GoalKeeper is a collaborative goal-setting bot designed to assist you in setting and achieving your goals. Whether you're working on personal projects, team objectives, or professional development, GoalKeeper is here to support you every step of the way.

## Getting Started

Follow these steps to get started with GoalKeeper:

1. Clone the repository: git clone [https://github.com/tahir80/goal_sync.git](https://github.com/tahir80/goal_sync.git)
2. cd goal_sync
3. Install the required dependencies: pip install -r requirements.txt

4. Before proceeding with setting up the Slack event subscription, it is recommended to deploy your code on Heroku to obtain a static URL for your app. This static URL will be used later when configuring the Slack event subscription. Follow the steps below to create a Heroku app and deploy your code:

Create a Heroku Account: If you don't have a Heroku account, sign up for one at Heroku.

Install Heroku CLI: Download and install the Heroku Command Line Interface (CLI) from Heroku CLI.

Login to Heroku: Open a terminal or command prompt and log in to Heroku using the command:
heroku login
Initialize Git: If your code is not already in a Git repository, navigate to your project directory and initialize Git:
git init
git add .
git commit -m "Initial commit"
Create a Heroku App: Create a new Heroku app using the Heroku CLI:

heroku create your-app-name
heroku create your-app-name
Replace your-app-name with a unique name for your app.

Deploy to Heroku: Deploy your code to Heroku:
git push heroku master
This will automatically build and deploy your app on Heroku.

Obtain Static URL: Once the deployment is successful, you will get a static URL for your app. It will be in the format https://your-app-name.herokuapp.com/

3. Set up environment variables:

You need to set up the following environment variables on Heroku (https://devcenter.heroku.com/articles/config-vars):

- `SLACK_TOKEN`: Your Slack bot token.
- `SIGNING_SECRET`: Your Slack app signing secret.
- `CHANNEL_ID`: The ID of the channel where you want GoalKeeper to operate.
- `REDIS_HOST`: Redis server host.
- `REDIS_PORT`: Redis server port.
- `REDIS_PASS`: Redis server password (if applicable).

4. Run the application:





