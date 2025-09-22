# CI/CD component packaging

## `cici bundle` command

```sh
cici bundle
```

!!! note

    The `cici bundle` command will be replaced by the `cici package` command in a future release.

## Pre-commit hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://gitlab.com/saferatday0/cici
    rev: ""
    hooks:
      - id: cici-bundle
```

Run `pre-commit autoupdate` to pin to a stable version.
