# Configuration

There are three configuration layers:

```text
config/application.yaml
    Application/API runtime settings.

config/profiles/<site>.yaml
    Reusable business profile: hierarchy, entity types, SQL, cache policy.

config/local/<site>.yaml
    Deployment-local Oracle endpoint / username overrides; the password is read
    from GRID_ORACLE_PASSWORD.
```

For the current Jeddah package, Oracle connection settings are in:

```text
config/local/jeddah.yaml
```

To change the Oracle endpoint or username, edit that file and restart the service.
Set `GRID_ORACLE_PASSWORD` in the process environment; do not write it to YAML.
