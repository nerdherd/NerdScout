# NerdScout
The scouting app of Nerd Herd 687.

## Setup

### MongoDB setup

#### MongoDB Community Edition

Download [MongoDB Community Edition](https://www.mongodb.com/try/download/community)

Make sure you have MongoDB Compass installed, as well as the path to the mongod.exe (install for compass and all needed EXEs are within the download)

Create a folder to store the database (you can just create a folder `database` in the repository folder)

To start the database on Windows:
```powershell
\path\to\exe\mongod.exe --dbpath \path\to\database
```

or on Mac:

```bash
/path/to/executable/mongod --dbpath /path/to/database
```

Open compass and create a connection (the default URI should be correct)

Once you verify it works, create the file "mongoDB" in the secrets folder and paste in the URI

#### Atlas and Other Hosting

Place your MongoDB connection string in `mongoDB` and Compass, either beginning in `mongodb://` or `mongodb+srv://`. For more information, visit the [MongoDB Documentation](https://www.mongodb.com/docs/manual/reference/connection-string/).

Note: You only have to set up the secret key and compass connetion the first time.

### Secret key setup

Create a file `secretKey` in the secrets folder and put whatever text you want in there. This acts as the key for all of the encryption.

Note: You only have to set up the secret key the first time.

### The Blue Alliance setup

If you don't already have one, create a [The Blue Alliance](https://www.thebluealliance.com/) account

Under account, scroll to Read API Keys and create a new key.

Create a new file `theBlueAlliance` in the secrets folder and paste in the key.

Note: You only have to set up the API key the first time.

### Python setup

Make sure you have Python 3 installed.

Create a terminal in the directory NerdScout is located in. Then, make a virtual environment and activate it.

For Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

For Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

Now install the required packages.

```bash
pip install -r requirements.txt
```

You can deactivate the virtual environment with the deactivate keyword.

```bash
deactivate
```

Note: You only have to create the virtual environment and install the requirements the first time.

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
