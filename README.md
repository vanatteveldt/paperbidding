# Simple paper bidding website

We can't use easychair so I created a simple website for ICA Computational Methods paper bidding.
This is heavily customized to how ICA has their data stored, so this is not a general solution.
However, feel free to copy/clone/steal the repository and adapt it to your needs :)

# Installation

Clone the repository, setup a virtual environment and install the requirements:

```
git clone git@github.com:vanatteveldt/paperbidding
cd paperbidding/
python3 -m venv env
env/bin/pip install -U pip wheel
env/bin/pip install -r requirements.txt
```

# Importing the data

## Create the database

Initialize the database:

```
env/bin/python manage.py migrate
```

## Get the required data files
Add the three required files to the `data` folder: (the names don't matter, but it can't harm to stick to this convention. 
Note: 20XX refers to the ICA year (so 2021 is for ICA 2021, i.e. unit planning in 2020), however this was not done consistently in the past.

- `data/20xx_cm_volunteers.csv`: all people who volunteered to review (can be downloaded from the ICA submission web site as unit planner)
- `data/20xx_cm_abstracts.csv`: all abstracts submitted to CM this year (can be requested from ICA, download from web site does not include all authors)
- `data/20zz_all_abstracts.csv`: file with older abstracts to all divisions to do the matching (last year can be requested from ICA, olders years are in shared google drive)

You will also need the word embeddings file, which can be downloaded using:

```
wget -qO- "https://github.com/eyaler/word2vec-slim/blob/master/GoogleNews-vectors-negative300-SLIM.bin.gz?raw=true" | gunzip > data/GoogleNews-vectors-negative300-SLIM.bin
```

## Import the data 

Call the `import_data` script with the paths to the data files:

```
env/bin/python import_data.py ABSTRACTS_FILE VOLUNTEERS_FILE
```

For example, for 2021 it looks like this:

```
$ env/bin/python import_data.py data/2021_cm_abstracts.csv data/2021_cm_volunteers.csv 
** Added 134 authors to the database
** Imported 86 new papers (238 in total) and created 130 new authors that did not volunteer
```

Note: This automatically skips any author or paper already in the system, so you can call it again if it e.g. skipped one reviewer or gave an error message

Also note: Column names seem to vary from year to year, so it's possible you need to edit this file to change the column names

# Match reviewers to papers

Use the `match.py` to match the imported reviewers to the outstanding abstracts. 

```
$ env/bin/python match.py data/2020_all_abstracts.csv 
** Loading reference texts
*** Added 6321 reference texts from data/2020_all_abstracts.csv
*** Added 238 reference texts from this year's papers
*** Added 0 reference texts from volunteer keywords
** Loading word vectors from data/GoogleNews-vectors-negative300-SLIM.bin
*** Loaded 299567 word vectors with dimensionality 300
** Computing matches
*** Assigned similarity scores for 154 reviewers (skipped 0 reviewers)
```

Note: This automatically skips any reviewer already assigned scores, so you can call it again if it e.g. skipped one reviewer or gave an error message

# Check webpage and send emails

To run the website locally, use:

```
$ env/bin/python manage.py runserver
```

To log in, you need to generate credentials. You can do that with the `send_emails.py` script, which you can use to generate the email to yourself:

```
$ env/bin/python send_invitations.py --email wouter@vanatteveldt.com
Dear Wouter,
[...]To do the paper bidding, please visit the link below:
http://bid.ica-cm.org/?email=wouter@vanatteveldt.com&code=xxx
```

To test locally, go to http://localhost:8000/?email= etc. 

## Moving to production

To move to production, copy the database file `data/db.sqlite3` to the production server and run it there. Don't forget to commit, push, and pull any changes you made to the code or templates.

Note: we now macgyver that by running runserver in a screen on the amcat server on `/home/wva/paperbidding`, would probably be better to do it properly. "Next year", right? 

## Send a test email

As a final test, generate a gmail 'app' password and use it to send an email to yourself:

```
$ env/bin/python send_invitations.py --email wouter@vanatteveldt.com --password yourgmailpassword
```

## Mail the members

If you are happy with the site and invitation email, send it off to all members:

```
$ env/bin/python send_invitations.py --password yourgmailpassword
```

Note that there's a good chance it will stop after 100 or so emails due to rate limitations. In that case, store those emails in a file "sent.txt", wait 15 minutes, and call the script again with that ignore list:

```
$ env/bin/python send_invitations.py --password yourgmailpassword --ignore sent.txt
```

# Assign reviewers

(to come)
