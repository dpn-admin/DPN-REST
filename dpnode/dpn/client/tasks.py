import json

from django.conf import settings

from dpn.client import REGISTRY_URL
from dpn.client.apiclient import APIException, APIClient
from dpn.client.parsers import registry_list_parser
from dpn.data.utils import dpn_strftime, dpn_strptime

def pull_registry_entries(node):
    """
    Pulls registry entries from the specified node that have been modified
    since the last pull and updates our local database.

    :param node: Node object to pull entries from.
    :return:
    """

    if not node.api_root:
        raise APIException("No api root defined for %s" % node.namespace)

    try:
        token = settings.NODES[node.namespace]['token']
    except KeyError:
        raise APIException("No API Key for %s" % node.namespace)

    last_modified = node.last_pull_date if node.last_pull_date else None
    client = APIClient(node.api_root, token)
    qs = {
        'page_size': 2,
        'ordering': "last_modified_date",
        'first_node': node.namespace,
    }
    if last_modified:
        qs["after"] = dpn_strftime(last_modified)

    for type in ['B', 'R', 'D']:
        qs["object_type"] = type
        more = True
        while more:
            response = client.get(REGISTRY_URL, params=qs)
            if response.status == 200:
                raw = response.read()
                data = json.loads(raw.decode('utf-8'))
                results = data.get("results", None)
                if results:
                    last_modified = dpn_strptime(results[-1].get("last_modified_date", None))
                    registry_list_parser(data.get("results", None), node, track=False)
                    qs["after"] = dpn_strftime(last_modified)
                else:
                    more = False
            else:
                raise APIException("Response %d returned from %s" % (
                                            response.status, node.namespace))
                more = False

    if last_modified:
        node.last_pull_date = last_modified
        node.save()