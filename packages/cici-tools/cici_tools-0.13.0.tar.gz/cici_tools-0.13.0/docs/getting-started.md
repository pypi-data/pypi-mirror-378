# Getting started

All **cici** configuration is managed by the `.cici` config directory. The
contents of this directory are part of your project and should be committed to
version control.

## `.cici/config.yaml`

## `.cici/README.md.j2`

## `.cici/.gitlab-ci.yml`

At present, cici still relies on some native GitLab CI/CD syntax to render final
pipelines. This couples cici to GitLab at present, and so we are working to
remove this requirement.
