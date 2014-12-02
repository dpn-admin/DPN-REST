import json

from django.conf import settings

from dpn.client import REGISTRY_URL
from dpn.client.apiclient import APIException, APIClient
from dpn.client.parsers import registry_list_parser
from dpn.data.utils import dpn_strftime


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

    client = APIClient(node.api_root, token)
    qs = {
        'page_size': 300,
        'ordering': "last_modified_date",
        'first_node': node.namespace,
    }
    if node.last_pull_date:
        qs["after"] = dpn_strftime(node.last_pull_date)

    more = True
    while more:
        response = client.get(REGISTRY_URL, params=qs)
        if response.status == 200:
            raw = response.read()
            data = json.loads(raw.decode('utf-8'))
            more = data.get("next", False)
            results = data.get("results", None)
            if results:
                last_modified = results[-1].get("last_modified_date", None)
                registry_list_parser(data.get("results", None))
        else:
            raise APIException("Response %d returned from %s" % (
                                            response.status, node.namespace))
