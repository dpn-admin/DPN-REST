# make_test_data.py
#
# This script generates test data for other nodes that we want to impersonate
# in our local integration tests. The main test data file, TestServerData.json,
# comes from running Django's dumpdata command on our test server. We may
# update TestServerData.json occasionally, and when we do, this script enables
# us to transform that into test data files for other nodes.
#
# Usage:
#
# > python make_test_data.py <node>
#
# The node param is one of DPN's other node namespaces:
#
# * chron
# * hathi
# * tdr
# * sdr
#
# The script transform data in TestServerData.json into data suitable for
# running a local instance of chron/hathi/tdr/sdr. The output goes to
# TestServerData_<node>.json (e.g. TestServerData_tdr.json)
#
# The run_cluster.py script then loads the data for each node from the
# correct json file.

import os
import re
import sys
import uuid

# The namespace of the node for which we're generating data.
allowed_targets = ('chron', 'hathi', 'tdr', 'sdr',)
target_node = None

# This is the basic test data file, dumped from the test server.
this_dir = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(this_dir, "TestServerData.json")

# Match and capture UUIDs & other data
uuid_regex = re.compile(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', re.IGNORECASE)
ingest_node_regex = re.compile(r'"ingest_node": (\d+)')
admin_node_regex = re.compile(r'"admin_node": (\d+)')
local_id_regex = re.compile(r'"local_id": "(.+)"')
from_node_regex = re.compile(r'"from_node": (\d+)')
to_node_regex = re.compile(r'"to_node": (\d+)')

# Map original uuids to replacement uuids
uuid_replacements = {}

# Map node namespaces to ids
node_id = {
    'aptrust': '1',
    'hathi': '2',
    'chron': '3',
    'tdr': '4',
    'sdr': '5',
}

# Used for generating new bag names
bag_counter = 1

def run():
    global target_node
    target_node = get_target_node()
    if target_node not in allowed_targets:
        print("Usage: python make_test_data.py <node>")
        print("Node must be one of {0}".format(", ".join(allowed_targets)))
        sys.exit(1)
    transform_file()

def transform_file():
    global target_node
    outfile_name = "TestServerData_{0}.json".format(target_node)
    with open(outfile_name, 'w') as output_file:
        with open(data_file) as input_file:
            for line in input_file:
                line = replace_uuid(line.rstrip())
                line = replace_node_name(line)
                line = replace_ingest_node(line)
                line = replace_admin_node(line)
                line = replace_from_node(line)
                line = replace_to_node(line)
                line = replace_local_id(line)
                line = set_superuser(line + os.linesep)
                output_file.write(line)
    print("Transformed data is in {0}".format(outfile_name))

def get_target_node():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return None

def replace_uuid(line):
    match = uuid_regex.search(line)
    if match:
        orig_uuid = match.group(0)
        if orig_uuid not in uuid_replacements:
            uuid_replacements[orig_uuid] = str(uuid.uuid4())
        #print("Replacing {0} with {1}".format(orig_uuid, uuid_replacements[orig_uuid]))
        return line.replace(orig_uuid, uuid_replacements[orig_uuid])
    return line

def replace_node_name(line):
    if "username" in line or "namespace" in line:
        return line
    return line.replace('aptrust', target_node)

def set_superuser(line):
    global target_node
    if '"username"' in line:
        if "{0}_user".format(target_node) in line:
            return '{0} "is_superuser": true,'.format(line)
        else:
            return '{0} "is_superuser": false,'.format(line)
    return line


def replace_ingest_node(line):
    match = ingest_node_regex.search(line)
    if match:
        orig_node_id = match.group(1)
        #print("Replacing ingest_node {0} with {1}".format(orig_node_id, node_id[target_node]))
        return line.replace(orig_node_id, node_id[target_node])
    return line


def replace_admin_node(line):
    match = admin_node_regex.search(line)
    if match:
        orig_node_id = match.group(1)
        #print("Replacing admin_node {0} with {1}".format(orig_node_id, node_id[target_node]))
        return line.replace(orig_node_id, node_id[target_node])
    return line

def replace_from_node(line):
    match = from_node_regex.search(line)
    if match:
        orig_node_id = match.group(1)
        if orig_node_id == node_id['aptrust']:
            #print("Replacing from_node {0} with {1}".format(orig_node_id, node_id[target_node]))
            return line.replace(orig_node_id, node_id[target_node])
    return line

def replace_to_node(line):
    match = to_node_regex.search(line)
    if match:
        orig_node_id = match.group(1)
        if orig_node_id == node_id['aptrust']:
            #print("Replacing to_node {0} with {1}".format(orig_node_id, node_id[target_node]))
            return line.replace(orig_node_id, node_id[target_node])
    return line

def replace_local_id(line):
    global bag_counter
    match = local_id_regex.search(line)
    if match:
        orig_local_id = match.group(1)
        new_local_id = "{0}_bag_{1}".format(target_node, bag_counter)
        bag_counter += 1
        #print("Replacing local_id {0} with {1}".format(orig_local_id, new_local_id))
        return line.replace(orig_local_id, new_local_id)
    return line


if __name__ == "__main__":
    run()
