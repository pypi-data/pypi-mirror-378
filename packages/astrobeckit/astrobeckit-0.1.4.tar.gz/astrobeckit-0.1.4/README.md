# astrobeckit

A small package full of useful little scripts for astro.

## Installation

```bash
pip install astrobeckit
```

## Usage

[activate python environment]

And then use any of the following commands on the command line.

## papergirl
This script will scrape the arxiv new posts page for all the new papers of the day,
cross check these against lists of authors and key words that you are interested in
and only return those specific papers. It will then email this curated list straight
to your inbox.
Note that this script requires the following environment variables to be set

```bash
PAPERGIRL_PASSWORD # the app specific password
PAPERGIRL_FROM     # the email address it should be sent from
PAPERGIRL_TO       # the email address it should be sent to
```

The author and topic lists should also exist even if blank. To run:

```bash
papergirl (--topics [location of topics file] --authors [location of authors file])`
```

## synchro
This script creates a file called "splash.filenames" that lists in the correct
filenames you need for a synchronised movie with splash. It is designed to be 
used when you have several simulation folders and for whatever reason the files
have gotten out of synch. It requires the log files and a file that lists the
folders you are interested in, separated as a new line. To run:

```bash
synchro --folders_file [file that lists the folders of interest]
       (--prefix [file name prefix, e.g. disc]
        --end [when to stop movie])
```

## auto_resubmit
This script is specific to the AVON cluster at Warwick. Looks for all the subfolders
in the current directory and resubmits the simulation in there if it hasn't finished.
Assumes that the run submission script is called "run_sbatch.sh".

This script also assumes the existance of multi_run.sh, a short script that
generates linked submission jobs. It is also uploaded to this repository but
must be downloaded separately and is assumed to be in `~/runs/`. To run:

```bash
auto_resubmit (--search_string [masks for a string in the folder names]
               --dry_run [if True, just does a test run]
               --n_sub [how many linked jobs do you want submitted])
```


