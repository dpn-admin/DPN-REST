

# Overview

EarthDiver is a prototype for a REST based protocol for a node in the DPN
network of replicating nodes.  Currently it shows data structures and some
proposed REST calls that could be used to negotiate interactions in the DPN
network.

## Build Status

* Master: [![Build Status](https://travis-ci.org/APTrust/EarthDiver.svg?branch=master)](https://travis-ci.org/APTrust/EarthDiver)
* Develop: [![Build Status](https://travis-ci.org/APTrust/EarthDiver.svg?branch=develop)](https://travis-ci.org/APTrust/EarthDiver)

# Installation

For demonstration purposes this is being checked out and run under django
runserver and not currently intended for a production release.

## Setup Python Environment

* Python 3.4 is a requirement, this comes installed by default on many modern
  linux distributions, usually under python3 rather than the system default.
* It's always recommended to use a virtualenv for your python dependencies or an
  image like vagrant.  Python 3 recommends using
  [venv](https://docs.python.org/3/library/venv.html) for the virtual env. The
  venv command is typically named pyvenv-3.4 on most of these systems as well.

### NOTE ON UBUNTU:

There is a known bug with venv in Ubuntu 14.04 (and perhaps other versions as
well.) as it is missing the 'ensurepip' module required for venv to work
correctly.

To fix you'll need to download the current
[python 3.4 source](https://www.python.org/downloads/) and untar it to a local
directory.  Then copy <temp python dir>/Lib/ensurepip your python 3 Lib
directory, which is usually /usr/lib/python3.4

## Setup Project Code

* Clone the project from GitHub as needed to a local directory.
* Setup whatever DB you want to use.  I use sqlite against a *.db file in the
  project data directory for development or when using runserver. *.db files are
  in the .gitignore file.
* With the virtual environment active `pip install -r requirements.txt`
* Copy EarthDiver/dpnode/localsettings_dist.py to
  EarthDover/dpnode/localsettings.py and configure as needed.
* From EarthDiver/dpnode/ run `python manage.py migrate` **twice** the first
  time (It needs to run the base migrations than the local ones).
* Load the base data by running 'python manage.py loaddata ../data/PreloadData.json'
  That will load data that must exist in the database, such as the sha256
  fixity algorithm that all nodes must initially support.

### System Dependencies

* In development it will frequently require you to have some development
  libraries installed as well.

  `>sudo apt-get install libpython3-dev, libyaml-dev`

## Setup SuperUser & Groups

* Group permissions are supplied the EarthDiver/data/GroupPermissions.json
  fixture that support the access model of the REST calls.
* Load it by executing 'python manage.py loaddata ../data/GroupPermissions.json'
* Create your initial superuser by 'python manage.py createsuperuser'

## Creating API Users

* Normal users and created and assigned in the django admin interface.
* Create a user and save them.
* Edit the user and click on the 'Profile' section and assign the user to
  an appropriate node. (This controls what transfers they can see and more)
* Edit the user and assign them to the appropriate user group:
    * 'api_users' are users from other nodes, it allows them to query the API
       and view returns as needed.
    * 'api_admins' are for a localnode user, it includes the above permissions
      plus the ability to add transfers or registry entries.

## Setting up test data:

* Activate your virtual environment.
* To populate with stub test data execute the following manage.py commands:
    * `python manage.py make_nodes` Makes some stub node data, etc.
    * `python manage.py make_testdata` Makes some test registry entries and
       transfers.
* Add a new user to use an auth token for and assign them to a node.
  Permissions are based on user permissions and they can only see their own node
  content for transfers.

# Runserver for Development Testing:

* Activate your virtual environment. (noticing a theme here?)
* from EarthDiver/dpnode run `python manage.py runserver`

# Testing:

*  Use something like PostMan in Firefox or a similar Chrome plugin to easily
   mimic REST client calls.  You'll need to set the Authorized token header for
   it to work.