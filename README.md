# Overview

EarthDiver is a prototype for a REST based protocol for a node in the DPN
network of replicating nodes.  Currently it shows datastructures and some
proposed REST calls that could be used to negotiate interactions in the DPN
network.

# Installation

For demonstration purposes this is being checked out and run under django
runserver and not currently intended for a production release.

To Setup just:

* Checkout the code from this repo to some local file.
* I recommend using a virtualenvironment under python 3.4 (see pyvenv for
  more info)
* Setup whatever DB you want to use.  I use sqlite for demos.
* With the virtual environment active `pip install -r requirements.txt`
* Copy EarthDiver/dpnode/localsettings_dist.py to
  EarthDover/dpnode/localsettings.py and configure as needed.
* From EarthDiver/dpnode/ run `python manage.py syncdb` then
  `python manage.py migrate`

Setting up test data:

* Activate your virtual environment.
* You can populate some data for nodes through the loaddata manage.py command
  using the node.json file.  Add any port or storage data you want.
* Add a new user to use an auth token for and assign them to a node.
  Permissions are based on user permissions and they can only see their own node
  content for transfers.
* Add fake transfers and registries entries by using the manage.py command
  'make_testdata'

To Run just:

* Activate your virtual environment. (noticing a theme here?)
* from EarthDiver/dpnode run `python manage.py runserver`

To Test:

*  Use something like PostMan in Firefox or a similar Chrome plugin to easily
   mimic REST client calls.  You'll need to set the Authorized token header for
   it to work.