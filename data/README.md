# Preload and Test Data

You can load data from any of the json files in this directory into
Django using this command:

```
python manage.py loaddata <filename>.json
```

You should definitely load GroupPermissions.json, so you don't have to
set them all by hand. And you must load PreloadData.json, so you have
the base configuration data the system needs to run. (Currently,
that's just a single record describing the default fixity algorithm.)

If you're running integration tests with APTrust's back-end service
code, you should load TestServerData.json.

The make_test_data.py script transforms data from TestServerData.json
to be used as test data for impersonated nodes when running a local
testing cluster. It will generate test data for chron, hathi, tdr and
sdr by transforming values in the TestServerData.json file (which is
test data for the aptrust node).

After generating test data for impersonated nodes, run the script
dpnode/run_cluster.py to run the nodes on ports 8000-8004.