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
