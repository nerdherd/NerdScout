<h1 style="width:100%;text-align:center;" alt="A pair of binoculars with a propeller hat."><img src="./static/images/logo/logo.svg" height="100" /><br> NerdScout</h1>
<p style="width:100%;text-align:center;">The scouting app of Nerd Herd 687.</p>

## About

NerdScout is a scouting app for the *FIRST* Robotics Competition, aiding in data collection during matches. Scouts watch matches and use NerdScout to record what a robot did during a match, from scoring to defense to fouls. 

Pit scouting is also included, allowing scouts to ask prewritten questions to teams and input their answers into the app.

NerdScout then aggregates this data into tables for analytical use during Alliance Selection, along with providing stats for each team in many areas.

NerdScout also incorporates NerdPredict, a game where team members predict match results in order to gain the most points.

## Setup

### MongoDB setup

#### MongoDB Community Edition

MongoDB Community Edition is the self hosted version of MongoDB, helpful for development.

1. Download [MongoDB Community Edition](https://www.mongodb.com/try/download/community)

2. (optional) Install [MongoDB Compass](https://www.mongodb.com/try/download/compass), the GUI explorer for MongoDB. The installer is usually included with MongoDB Community Edition.

3. Create a folder to store the database. This can be anywhere, but `/database` is ignored by git in this repo.

4. Start the database

To start the database on Windows:
```powershell
\path\to\exe\mongod.exe --dbpath "\path\to\database"
```

or on Mac:

```bash
/path/to/executable/mongod --dbpath "/path/to/database"
```

5. (optional) Open Compass and create a connection (the default URI should be correct)

6. Once you verify it works, create the file `mongoDB` in the `secrets` directory and paste in the URI

#### Atlas and Other Hosting

Place your MongoDB connection string in `secrets/mongoDB` and Compass, either beginning in `mongodb://` or `mongodb+srv://`. For more information, visit the [MongoDB Documentation](https://www.mongodb.com/docs/manual/reference/connection-string/).

### Secret key setup

Create a file `secretKey` in the `secrets` directory with whatever text you want. This acts as the key for all of the encryption. Do not change this, unless you are resetting the database.

### The Blue Alliance setup

If you don't already have one, create a [The Blue Alliance](https://www.thebluealliance.com/) account

Under account, scroll to Read API Keys and create a new key.

Create a new file `theBlueAlliance` in the `secrets` directory and paste in the key.

### Python setup

Make sure you have Python 3 installed.

Create a terminal in the directory NerdScout is located in. Then, make a virtual environment and activate it.

For Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
```
For Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Now install the required packages.

```bash
pip install -r requirements.txt
```

You can deactivate the virtual environment with the deactivate keyword.

```bash
deactivate
```

The next time you want to run NerdScout, simply run the activation script.

## Running

Before running, ensure:
- All required secrets are added. Check /secrets/README.md for the full list.
- The database is running
- The virtual environment is active

Run the script using:

```bash
flask run
```

or use debug mode.

```bash
flask run --debug
```

This should open a development server and display an IP Address. Navigate to this IP address to view NerdScout.

The server included with Flask is **not** meant for production use. There are many options for running WSGI (Web Server Gateway Interface) servers suitable for production. Check out the [Flask documentation](https://flask.palletsprojects.com/en/stable/deploying/) for more information.