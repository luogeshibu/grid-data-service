# Profiles

Each project gets one YAML profile.

Examples:

```text
profiles/
├─ jeddah.yaml
├─ jazan.yaml
├─ madinah.yaml
└─ another-project.yaml
```

The Python backend stays unchanged.

A profile controls:

- Oracle datasource(s)
- model vs realtime datasource separation
- tree hierarchy
- supported entity types
- all project SQL
- caching
- realtime enable/disable
- generic named-query exposure

Do not put database passwords directly in YAML.
Use `${ENV_VAR}` and place secrets in `.env` or the deployment environment.
