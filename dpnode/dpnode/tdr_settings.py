#
# Special settings file for impersonating TDR node
# when running local tests.
#
import os

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dpnrest_tdr.db',
    }
}

# Directory to be monitored for new added bags
DPN_BAG_DIR = os.path.join(PROJECT_PATH, '../../files/bags_tdr')

# node identifier, should match the namespace entry in the Node entry.
DPN_NAMESPACE = 'tdr'
