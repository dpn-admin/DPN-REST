"""
    'Contrary to what people may say, there is no upper limit to stupidity.'
                    - Stephen Colbert

"""

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from dpn.data.models import Node
from dpn.client.tasks import accept_transfers

class Command(BaseCommand):
    help = 'Pulls registry entries from all nodes or named node only if ' \
           'specified.'

    option_list = BaseCommand.option_list + (
        make_option("--node",
            dest="namespace",
            default=None,
            help="Namespace of specific node to pull registry entries from."
        ),
        make_option("--max",
                    dest="max",
                    default=settings.DPN_MAX_ACCEPT,
                    help="Max number of transfer to mark as accepted at once."
                    )
    )

    def handle(self, *args, **options):
        nodes = Node.objects.exclude(api_root__isnull=True).exclude(
                api_root__exact='').exclude(namespace=settings.DPN_NAMESPACE)
        nodes = nodes.filter(replicate_from=True)
        if options['namespace']:
            nodes.filter(namespace=options['namespace'])

        if not nodes:
            raise CommandError("No nodes found to query.")

        for node in nodes:
            accept_transfers(node, options['max'])
            self.stdout.write("Done accepting transfers from %s" %
                              node.namespace)