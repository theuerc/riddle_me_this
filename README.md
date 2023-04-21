# Riddle Me This

Takes a youtube url, gets the best transcript (a manually entered english transcript, or a locally generated english transcript using OpenAI's Whisper model--it can translate if needed), chunks and vectorizes the transcript, and loads the most similar 2000 word chunk (using cosine similarity) into ChatGPT as context for a user prompt.

_Basically takes a youtube video and answers any question you ask it._

There are helper visualization to aid with prompting, like a network of co-occuring named entities (using a window size of 7, and filtering entities using the median page rank of the network). This is a particularly helpful visualization because the context that ChatGPT is provided with is the most similar 2000 word chunk from the original text, so asking about two co-occuring entities will likely fall within a single chunk of context.

Beyond the network visualization, the title, description, and other metadata are provided. The fetched transcript with and without hyperlink timestamps is provided as well, with the option to regex search for specific rows in the timestamped transcript to verify the accuracy of a specific line of text.

Everything is cached in a local sqlite database whose ERD diagram is shown below:
![Screen Shot 2023-04-20 at 11.56.30 PM.png](assets%2Fimg%2FScreen%20Shot%202023-04-20%20at%2011.56.30%20PM.png)

**Quickstart for Teaching Team:**

This project requires [Docker](https://www.docker.com/). Everything else should be installed automatically.

1. Clone the repo
```bash
git clone https://github.com/theuerc/riddle_me_this
```

2. Run the following commands in the root directory of the repo:
```bash
# make the database file
touch dev.db
# copy the environment file
cp .env.example .env
# open the .env file
nano .env
```

The .env file should include Google OAuth credentials and an OpenAI API key. 

If you need to make OAuth 2.0 web app credentials for Google, [click here](https://console.cloud.google.com/apis/), set the URI to `http://localhost:8080`, and the Authorized Redirect to `http://localhost:8080/login/authorized`. 

If you need an OpenAI API key, [click here](https://platform.openai.com/).

The bracketed sections need to be replaced in the .env file with your credentials:
```bash
# Environment variable overrides for local development
FLASK_APP=autoapp.py
FLASK_DEBUG=1
FLASK_ENV=development
DATABASE_URL=sqlite:////tmp/dev.db
GUNICORN_WORKERS=1
LOG_LEVEL=debug
SECRET_KEY=not-so-secret
# In production, set to a higher number, like 31556926
SEND_FILE_MAX_AGE_DEFAULT=0

# API keys for ChatGPT
OPENAI_API_KEY=[Your API Key]

# Google OAuth Credentials
CLIENT_ID=[Your Client ID]
CLIENT_SECRET=[Your Client Secret]
```
3. Once the dev.db file is created, and all of the required information is entered in the .env file, run the following commands in the root directory of the repo:
```bash
docker-compose build flask-dev
docker-compose run --rm manage db init
docker-compose run --rm manage db migrate
docker-compose run --rm manage db upgrade
docker-compose up flask-dev
```
Then go to http://localhost:8080/

At this point a sqlite database should be created. You can check this by running the following command in the root directory, or you can just move to the next step:
```bash
sqlite3 dev.db
sqlite> .tables
alembic_version  transcripts      videos         
roles            users   
sqlite> .exit
```
    

4. Click the button to login with Google, and follow the steps to login. You should then be redirected to the home_logged_in page where you can enter a url.

![Screen Shot 2023-04-20 at 11.52.11 PM.png](assets%2Fimg%2FScreen%20Shot%202023-04-20%20at%2011.52.11%20PM.png)

5. Enter a youtube url, and click the button to get the transcript. You should then be redirected to the video_details page where you can prompt with ChatGPT or Regex search the timestamped transcript.

![Screen Shot 2023-04-20 at 11.52.54 PM.png](assets%2Fimg%2FScreen%20Shot%202023-04-20%20at%2011.52.54%20PM.png)

Sample ChatGPT response:

![Screen Shot 2023-04-20 at 11.53.12 PM.png](assets%2Fimg%2FScreen%20Shot%202023-04-20%20at%2011.53.12%20PM.png)

Sample ChatGPT response to poor line of questioning:

![Screen Shot 2023-04-20 at 11.53.29 PM.png](assets%2Fimg%2FScreen%20Shot%202023-04-20%20at%2011.53.29%20PM.png)

Sample Entity Co-Occurrence network visualization:

![Screen Shot 2023-04-20 at 11.53.54 PM.png](assets%2Fimg%2FScreen%20Shot%202023-04-20%20at%2011.53.54%20PM.png)

Sample Regex search:

![Screen Shot 2023-04-20 at 11.54.08 PM.png](assets%2Fimg%2FScreen%20Shot%202023-04-20%20at%2011.54.08%20PM.png)


This flask app was made with the [flask cookiecutter template](https://github.com/cookiecutter-flask/cookiecutter-flask).
