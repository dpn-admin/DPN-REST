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

import json
import os
import sys
import uuid

# The namespace of the node for which we're generating data.
allowed_targets = ('chron', 'hathi', 'tdr', 'sdr',)
target_node = None

# This is the basic test data file, dumped from the test server.
this_dir = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(this_dir, "TestServerData.json")
highest_user_id = 0

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

def run():
    target_node = get_target_node()
    if target_node not in allowed_targets:
        print("Usage: python make_test_data.py <node>")
        print("Node must be one of {0}".format(", ".join(allowed_targets)))
        sys.exit(1)
    transform_data(target_node)

def transform_data(target_node):
    outfile_name = "TestServerData_{0}.json".format(target_node)
    with open(data_file) as input_file:
        data = json.loads(input_file.read())
        update_users(data, target_node)
        update_bags(data, target_node)
        update_fixities(data, target_node)
        update_transfer_requests(data, target_node)
        update_restore_requests(data, target_node)
        create_local_admin(data, target_node)
        with open(outfile_name, 'w') as output_file:
            output_file.write(json.dumps(data, indent=4))
            output_file.write("\n")
    print("Transformed data is in {0}".format(outfile_name))

def get_target_node():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return None

def update_users(data, target_node):
    global highest_user_id
    for obj in data:
        if obj['model'] == 'auth.user':
            if obj['pk'] > highest_user_id:
                highest_user_id = obj['pk']
            if obj['fields']['is_superuser'] == False:
                obj['fields']['is_staff'] = False
                obj['fields']['groups'] = [1]

def update_bags(data, target_node):
    bag_counter = 1
    target_node_id = node_id[target_node]
    for obj in data:
        if obj['model'] == 'data.bag':
            orig_uuid = obj['pk']
            if orig_uuid not in uuid_replacements:
                uuid_replacements[orig_uuid] = str(uuid.uuid4())
            obj['pk'] = uuid_replacements[orig_uuid]
            obj['fields']['first_version_uuid'] = uuid_replacements[orig_uuid]
            obj['fields']['ingest_node'] = target_node_id
            obj['fields']['admin_node'] = target_node_id
            obj['fields']['replicating_nodes'] = []
            obj['fields']['local_id'] = "{0}_bag_{1}".format(target_node, bag_counter)
            bag_counter += 1

def update_fixities(data, target_node):
    for obj in data:
        if obj['model'] == 'data.fixity':
            obj['fields']['bag'] = uuid_replacements[obj['fields']['bag']]

def update_transfer_requests(data, target_node):
    target_node_id = node_id[target_node]
    for obj in data:
        if obj['model'] == 'data.replicationtransfer':
            new_id = obj['fields']['replication_id'].replace('aptrust', target_node)
            obj['fields']['replication_id'] = new_id
            obj['fields']['from_node'] = target_node_id
            if obj['fields']['to_node'] == target_node_id:
                obj['fields']['to_node'] = node_id['aptrust']
            new_link = obj['fields']['link'].replace('aptrust', target_node)
            obj['fields']['link'] = new_link
            obj['fields']['bag'] = uuid_replacements[obj['fields']['bag']]

def update_restore_requests(data, target_node):
    target_node_id = node_id[target_node]
    for obj in data:
        if obj['model'] == 'data.restoretransfer':
            new_id = obj['fields']['restore_id'].replace('aptrust', target_node)
            obj['fields']['restore_id'] = new_id
            obj['fields']['to_node'] = target_node_id
            if obj['fields']['from_node'] == target_node_id:
                obj['fields']['from_node'] = node_id['aptrust']
            new_link = obj['fields']['link'].replace('aptrust', target_node)
            obj['fields']['link'] = new_link
            obj['fields']['bag'] = uuid_replacements[obj['fields']['bag']]

def create_local_admin(data, target_node):
    global highest_user_id
    new_admin_user_id = highest_user_id + 1
    new_admin = {
        "pk": new_admin_user_id,
        "fields": {
            "is_active": True,
            "last_login": "2015-06-05T14:46:20.744Z",
            "date_joined": "2015-05-04T17:27:12Z",
            "user_permissions": [],
            "first_name": target_node,
            "password": "pbkdf2_sha256$15000$Klz2TFoxY8xE$/I58ocVVFVI2xLCEfaCS0BJXEuKbCMSu7nmBAPENGXo=",
            "username": "{0}_admin".format(target_node),
            "email": "{0}_admin@aptrust.org".format(target_node),
            "last_name": "admin",
            "is_staff": True,
            "groups": [
                2
            ],
            "is_superuser": True
        },
        "model": "auth.user"
    }
    new_admin_token = {
        "pk": "0000000000000000000000000000000000000000",
        "fields": {
            "created": "2015-05-04T17:32:48.340Z",
            "user": new_admin_user_id
        },
        "model": "authtoken.token"
    }
    new_admin_profile = {
        "pk": new_admin_user_id,
        "fields": {
            "node": node_id[target_node],
            "user": new_admin_user_id
        },
        "model": "data.userprofile"
    }
    # index = 0
    # for obj in data:
    #     index += 1
    #     if obj['model'] == 'auth.user':
    #         data.insert(index, new_admin)
    #         break
    data.append(new_admin)
    data.append(new_admin_token)
    data.append(new_admin_profile)


if __name__ == "__main__":
    run()
