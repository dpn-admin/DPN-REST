'''
    "SCIENCE. It works, bitches."

        - xkcd Narrator
'''

from dpn.data.models import RegistryEntry, Node
from dpn.data.utils import dpn_strptime
from dpn.api.serializers import RegistryEntrySerializer

def registry_list_parser(results, node, track=False):
    """
    Takes a list of registry entry results and creates or updates matching
    registry entries or logs any invalid entries.

    :param results: List of Registry Entry dictionaries.
    :param node: Node object the entries are from.
    :param track: Boolean to indicate if last modified date of registries should
                  be updated for the node.
    :return: None
    """
    last_modified = None
    for entry in results:
        try:
            record = RegistryEntry.objects.get(
                dpn_object_id=entry['dpn_object_id'],
                first_node=node)
        except RegistryEntry.DoesNotExist:
            record = None
        re = RegistryEntrySerializer(data=entry, instance=record)
        if re.is_valid():
            last_modified = re.validated_data['last_modified_date']
            re.save()
    if last_modified and track:
        node.last_pull_date = dpn_strptime(last_modified)
        node.save()