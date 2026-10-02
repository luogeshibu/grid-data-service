# Local deployment configuration

Customer/deployment-specific connection settings are configured here.

For Jeddah:

```text
config/local/jeddah.yaml
```

This local file overrides the reusable profile:

```text
config/profiles/jeddah.yaml
```

`config/local/*.yaml` is ignored by Git by default.

Set the password with the `GRID_ORACLE_PASSWORD` process environment variable;
do not save the password in this directory.

When deploying a new site, create another local file with the same profile id,
for example `config/local/jazan.yaml`.
