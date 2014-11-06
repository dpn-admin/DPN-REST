from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from dpn.data.models import Node, Protocol, Port, Storage

class Command(BaseCommand):
    help = 'Populates the DB with Node'

    def handle(self, *args, **options):
        if not settings.DEV:
            raise CommandError("ABORTING: This command should only be run in development!")
        # Clear Everything out
        Storage.objects.all().delete()
        Port.objects.all().delete()
        Node.objects.all().delete()

        # create rsync as protocol
        rsync = Protocol(name='rsync')
        rsync.save()

        storage_data = {
            "aptrust": {"region": 'VA', "type": "Amazon S3"},
            "tdr": {"region": 'TX', "type": "Solaris In Memory"},
            "sdr": {"region": 'CA', "type": "Stanford Superdisk"},
            "hathi": {"region": 'MI', "type": "Thumbdrive"},
            "chron": {"region": 'CA', "type": "CDROM under David's Desk"},
        }

        node_data = {
            "aptrust": {
                "name": "APTrust",
                "namespace": "aptrust",
                "api_endpoint": "https://dpn-dev.aptrust.org/dpnrest/",
                "ssh_username": "aptdpn",
                "replicate_to": True,
            },
            "tdr": {
                "name": "TDR",
                "namespace": "tdr",
                "api_endpoint": "https://dpn.utexas.edu/dpnrest/",
                "ssh_username": "tdrdpn",
                "pull_from": True,
                "replicate_to": True,
            },
            "sdr": {
                "name": "SDR",
                "namespace": "sdr",
                "api_endpoint": "https://dpn.stanford.edu/dpnrest/",
                "ssh_username": "sdrdpn",
                "pull_from": True,
                "replicate_to": True,
            },
            "hathi": {
                "name": "HathiTrust",
                "namespace": "hathi",
                "api_endpoint": "https://dpn.hathitrust.org/dpnrest/",
                "ssh_username": "hathidpn",
                "pull_from": True,
                "replicate_to": True,
            },
            "chron": {
                "name": "Chronopolis",
                "namespace": "chron",
                "api_endpoint": "https://dpn.chronopolis.org/dpnrest/",
                "ssh_username": "chrondpn",
                "pull_from": True,
                "replicate_to": True,
            },
        }

        for k, v in node_data.items():
            node = Node(**v)
            node.save()

            node.port_set.create(**{"ip": "127.0.0.1", "port": "22"})
            node.port_set.create(**{"ip": "127.0.0.1", "port": "443"})
            node.protocols.add(rsync)
            node.storage_set.create(**storage_data[k])
