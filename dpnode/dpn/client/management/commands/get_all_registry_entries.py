"""
    Do not argue with an idiot. He will drag you down to his level and beat you
    with experience.
            - Unknown
"""
import json
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from dpn.client.apiclient import APIClient
from dpn.data.models import Node
from dpn.client.parsers import registry_list_parser

class Command(BaseCommand):
    help = 'Pulls registry entries from all nodes or named node only if ' \
           'specified.'

    option_list = BaseCommand.option_list + (
        make_option("--node",
            dest="namespace",
            default=None,
            help="Namespace of specific node to pull registry entries from."
        ),
    )

    def handle(self, *args, **options):
        nodes = Node.objects.exclude(api_root__isnull=True).exclude(
                api_root__exact='').exclude(namespace=settings.DPN_NAMESPACE)
        if options['namespace']:
            nodes.filter(namespace=options['namespace'])

        if not nodes:
            raise CommandError("No nodes found to query.")

        for node in nodes:
            self._get_entries(node, "B")
            self._get_entries(node, "R")
            self._get_entries(node, "D")
            self.stdout.write("Done pulling entries from %s" % node.namespace)

    def _get_entries(self, node, type):
        try:
            token = settings.NODES[node.namespace]['token']
        except KeyError:
            self.stdout.write("No API Key for %s" % node.namespace)
            return None

        client = APIClient(node.api_root, token)
        url = '/api-v1/registry/'
        while url:
            qs = {
                'object_type': type,
                'page_size': 300,
                'first_node': node.namespace,
            }
            response = client.get(url, params=qs)
            if response.status == 200:
                raw = response.read()
                data = json.loads(raw.decode('utf-8'))
                url = data.get("next", None)
                registry_list_parser(data.get("results", None), node)
            else:
                self.stdout.write("API replied with %d status for %s" % (
                    response.status, node.namespace) )
