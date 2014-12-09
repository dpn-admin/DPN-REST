import json

from django.conf import settings

from dpn.client import REGISTRY_URL, TRANSFER_URL
from dpn.client.apiclient import APIException, APIClient
from dpn.client.parsers import registry_list_parser
from dpn.data.utils import dpn_strftime, dpn_strptime
from dpn.data.models import ACCEPT, PENDING, BRIGHTENING, RIGHTS, DATA, REJECT
from dpn.data.models import RegistryEntry

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
        'page_size': 300,
        'ordering': "last_modified_date",
        'first_node': node.namespace,
    }
    if last_modified:
        qs["after"] = dpn_strftime(last_modified)

    for type in [BRIGHTENING, RIGHTS, DATA]:
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
                raise APIException("Getting registry entries returned status %d from %s" % (response.status, node.namespace))
                more = False

    if last_modified:
        node.last_pull_date = last_modified
        node.save()

def accept_transfers(node, max):
    """
    Queries the node for pending transfers and accepts those that have a valid
    registry entry in our local database and are below the configured size
    limit for transfers.

    :param node: Node to accept from.
    :param max: Max number of accepted transfers to have at once.
    """
    if not node.api_root:
        raise APIException("No api root defined for %s" % node.namespace)

    try:
        token = settings.NODES[node.namespace]['token']
    except KeyError:
        raise APIException("No API Key for %s" % node.namespace)

    accepted_count = 0
    client = APIClient(node.api_root, token)

    # Get the number of currently accepted transfers with fixity null and exit
    # if at or above max
    qs = {
        'status': ACCEPT,
        'fixity': "null",
        'ordering': 'updated_on',
        'page_size': max,
    }

    response = client.get(TRANSFER_URL, params=qs)
    if response.status == 200:
        raw = response.read()
        data = json.loads(raw.decode('utf-8'))
        results = data.get("results", [])
        accepted_count = len(results)
    else:
        raise APIException("Getting accepted transfers returned status %d from %s" % (response.status, node.namespace))

    if accepted_count >= max:
        return

    # Get pending transfers ordered by oldest paged by remainder of max.
    qs = {
        'status': PENDING,
        'ordering': 'updated_on',
        'page_size': max - accepted_count,
    }
    response = client.get(TRANSFER_URL, params=qs)
    if response.status == 200:
        raw = response.read()
        data = json.loads(raw.decode('utf-8'))
        results = data.get("results", [])
        for xfer in results:
            try:
                _accept_transfer(client, xfer)
            except KeyError:
                pass # TODO log this instead.
    else:
        raise APIException("Getting pending transfers returned status %d from %s" % (response.status, node.namespace))

    # Iterate through transfers, skip any without registry entries, reject any
    # above the size limit, accept the rest.

def _accept_transfer(client, xfer):
    """
    marks a specific transfer ID as accepted.

    :param client: APIClient to use.
    :param xfer: Dict of transfer to accept.
    :return:
    """
    try:
        entry = RegistryEntry.objects.get(dpn_object_id=xfer["dpn_object_id"])
    except RegistryEntry.DoesNotExist:
        return

    xfer["status"] = ACCEPT
    if xfer["size"] >= settings.DPN_MAX_SIZE:
        xfer["status"] = REJECT

    response = client.put("%s%s/" % (TRANSFER_URL, xfer["event_id"]), data=xfer)
    if response.status not in [200, 204]:
        raise APIException("Updating transfer %s returned status %d" % (xfer["event_id"], response.status))