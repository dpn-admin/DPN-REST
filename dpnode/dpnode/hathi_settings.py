#
# Special settings file for impersonating hathi node
# when running local tests.
#
import os

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dpnrest_hathi.db',
    }
}

# Directory to be monitored for new added bags
DPN_BAG_DIR = os.path.join(PROJECT_PATH, '../../files/bags_hathi')

# node identifier, should match the namespace entry in the Node entry.
DPN_NAMESPACE = 'hathi'
