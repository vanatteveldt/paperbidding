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

Note: Column names seem to vary from year to year, so it's possible you need to edit this file to change the column names

