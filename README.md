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
- `data/20xx_cm_abstracts.csv`: abstracts submitted to CM this year *with all authors* (can be requested from ICA)
- `data/2021_cm_abstracts_website.csv` : all abstracts submitted to CM this year *with type and keywords* (can be downloaded as unit planner)
- `data/20zz_all_abstracts.csv`: file with older abstracts to all divisions to do the matching (last year can be requested from ICA, olders years are in shared google drive)

Note that it's a bit annoying that half the info is in the abstracts emailed from ICA and the other half in the abstracts we can download ourselves, so hopefully this can be sorted at some point. 

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

# Check progress and send reminders

To check progress, I generally copy the `data/db.sqlite3` file back from the production server to my personal computer and work locally.
That way, if I screw up at least the site is still up and the data is still there. 
Note that sqlite files can be corrupted if copied while someone is writing, but that should be relatively rare so in that case just copy again.
I'm sure there is also an elegant solution. For next year. 

Now, run the `mail_reminders.py` script with `--check`:

```
$ env/bin/python send_reminder.py --check
** Bids received from 105 reviewers
** 50 reviewers still need to bid
[... list of emails and links for people that didn't submit bids yet ...]
```

If you want to remind the laggards, make sure to update the reminder email template ([email_reminder.txt](email_reminder.txt)) and run the same script with the email password:

```
$ env/bin/python send_reminder.py --password yourgmailpassword
** Bids received from 105 reviewers
** 50 reviewers still need to bid
** Sending reminder emails...
[... list of emails that are being sent ...]
```

If you get an error message halfway through, you can copy the list of successful mails to a file and use it with `--ignore` as above

# Assign reviewers

When the bidding is done, you can use the `assign.py` script to automatically assign papers to authors:

```
$ env/bin/python assign.py > assignments.csv
```

You can check this file and e.g. list how many papers per person to see if it seems mostly fair. 

After this, you need to assign the reviews in the ICA system. They promised it's possible automatically, otherwise it's a lot of clicking...

The assignment uses a greedy algorithm that (IIUC) goes through all papers, starting with the one with the least bids on it. Then it sorts the bidders for that paper starting with the people that have the least assignments so far, where full papers count more than abstracts (in case of ties it favours the best match according to the matching step). Then, it simply assigns the first three reviewers and goes to the next paper.

It will give an error message if any paper had less than three bids. For now it ignores 'no' and 'conflict', but since we have always been able to assign papers to 'yes' bidders, that doesn't seem to be a problem.  

