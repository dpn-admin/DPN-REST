"""
    I love deadlines. I like the whooshing sound they make as they fly by.
            - Douglas Adams
"""

# Set a reasonable Project Path setting so I dont' have to use hard coded paths.
import os
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

DEBUG = False # Always make False by default.
TEMPLATE_DEBUG = DEBUG
# IMPORTANT SET ONLY TO TRUE IN DEVELOPMENT ENVIRONMENT
DEV = False

ADMINS = (
# ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '', # Or path to database file if using sqlite3.
        'USER': '', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}

# Make this unique, and don't share it with anybody.
# Useful tool for this at http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = ''

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/assets/'

# URL paths for login. Must be strings, cannot be named paths.
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = '/'

# GRAPELLI SETTINGS
GRAPPELLI_ADMIN_TITLE = 'APTrust Admin'

# -----------------------
#
#  DPN NODE SETTINGS
#
# -----------------------

# Date Format
DPN_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ" # ISO 8601 format for strftime functions.

# Max Size of allowable bags
DPN_MAX_SIZE = 1099511627776 # 1 TB

# Directory to be monitored for new added bags
DPN_BAG_DIR = os.path.join(PROJECT_PATH, '../../files/bags')

# node identifier used for namespacing.
DPN_NAMESPACE = 'aptrust'

# Number of nodes to replicate to.
DPN_COPY_TOTAL = 2