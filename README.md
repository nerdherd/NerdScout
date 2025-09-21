# Nerd Scout
The scouting app of Nerd Herd 687.

## Running

Make sure you have Python 3 installed. <br>
Create a terminal in the directory Nerd Scout is located in. Then, make a virtual environment and activate it.

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

Before running, place all required secrets into /secrets. Check /secrets/README.md for more info.

Now, run the script using:

```bash
flask run
```

or use debug mode.

```bash
flask run --debug
```

This should open a development server and display an IP Address. Navigate to this IP address to view Nerd Scout