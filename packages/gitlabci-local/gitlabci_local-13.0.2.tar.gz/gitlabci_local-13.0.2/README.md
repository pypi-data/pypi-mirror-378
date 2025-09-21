# gcil

<!-- markdownlint-disable no-inline-html -->

[![Release](https://img.shields.io/pypi/v/gitlabci-local?color=blue)](https://pypi.org/project/gitlabci-local)
[![Python](https://img.shields.io/pypi/pyversions/gitlabci-local?color=blue)](https://pypi.org/project/gitlabci-local)
[![Downloads](https://img.shields.io/pypi/dm/gitlabci-local?color=blue)](https://pypi.org/project/gitlabci-local)
[![License](https://img.shields.io/gitlab/license/RadianDevCore/tools/gcil?color=blue)](https://gitlab.com/RadianDevCore/tools/gcil/-/blob/main/LICENSE)
<br />
[![Build](https://gitlab.com/RadianDevCore/tools/gcil/badges/main/pipeline.svg)](https://gitlab.com/RadianDevCore/tools/gcil/-/commits/main/)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gcil&metric=bugs)](https://sonarcloud.io/dashboard?id=RadianDevCore_gcil)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gcil&metric=code_smells)](https://sonarcloud.io/dashboard?id=RadianDevCore_gcil)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gcil&metric=coverage)](https://sonarcloud.io/dashboard?id=RadianDevCore_gcil)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gcil&metric=ncloc)](https://sonarcloud.io/dashboard?id=RadianDevCore_gcil)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gcil&metric=alert_status)](https://sonarcloud.io/dashboard?id=RadianDevCore_gcil)
<br />
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](https://commitizen-tools.github.io/commitizen/)
[![gcil](https://img.shields.io/badge/gcil-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/gcil)
[![guidelines](https://img.shields.io/badge/radiandevcore-guidelines-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/wiki/guidelines)
[![pre-commit-crocodile](https://img.shields.io/badge/pre--commit--crocodile-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/pre-commit-crocodile)

Launch .gitlab-ci.yml jobs locally, wrapped inside the specific images,  
with inplace project volume mounts and adaptive user selections

**Documentation:** <https://radiandevcore.gitlab.io/tools/gcil>  
**Package:** <https://pypi.org/project/gitlabci-local/>

---

## Purpose

The main purpose of this project is to unify and enhance reliability  
of builds, tests or releases running on GitLab CI in a similar local context,  
by providing the simplicity of an interactive and automated terminal tool  
and avoiding code duplication (Makefile, Shell scripts, docker run, ...).

Rather than creating yet another standard, the .gitlab-ci.yml specification  
is the common and unique interface between GitLab CI and `gcil`.

---

## Preview

![preview.svg](https://gitlab.com/RadianDevCore/tools/gcil/raw/13.0.2/docs/preview.svg)

---

<span class="page-break"></span>

## Examples

<!-- prettier-ignore-start -->

```bash
gcil                   # Launch the jobs choices interactive menu
gcil -p                # Launch the jobs pipeline automatically
gcil -l                # Launch the job selection interactive menu
gcil 'Dev'             # Launch jobs where the name contains a given string
gcil --debug 'Job 1'   # Hold a finishing specific job for debugging
gcil --bash 'Job 1'    # Prepare a bash environment for a specific job
gitlabci-local         # Shortcut alias to gcil
```

<!-- prettier-ignore-end -->

---

## Usage

<!-- prettier-ignore-start -->
<!-- readme-help-start -->

```yaml
usage: gcil [-h] [--version] [--no-color] [--update-check] [--settings] [--set GROUP KEY VAL] [-p] [-q]
            [-c CONFIGURATION] [-B] [-A] [-C COMMANDS] [-n NETWORK] [-e ENV] [-E ENGINE] [-H] [--notify]
            [--privileged [BOOL]] [--random-paths] [-r] [-S] [--ssh [SSH_USER]] [-v VOLUME] [-w WORKDIR]
            [--bash | --debug] [--display] [--shell SHELL] [--all] [--configure] [--input KEY=VAL] [-f] [-i] [-m]
            [--no-console] [--no-git-safeties] [--no-script-fail] [-R] [--no-verbose] [--scripts] [-t TAGS]
            [-d | -s | -l | --pull | --rmi] [--]
            [names ...]

gcil: Launch .gitlab-ci.yml jobs locally (aliases: gitlabci-local)

internal arguments:
  -h, --help           # Show this help message
  --version            # Show the current version
  --no-color           # Disable colors outputs with 'NO_COLOR=1'
                       # (or default settings: [themes] > no_color)
  --update-check       # Check for newer package updates
  --settings           # Show the current settings path and contents
  --set GROUP KEY VAL  # Set settings specific 'VAL' value to [GROUP] > KEY
                       # or unset by using 'UNSET' as 'VAL'

pipeline arguments:
  -p, --pipeline       # Automatically run pipeline stages rather than jobs
  -q, --quiet          # Hide jobs execution context
  -c CONFIGURATION     # Path to the .gitlab-ci.yml configuration file or folder
  -B, --no-before      # Disable before_script executions
  -A, --no-after       # Disable after_script executions
  -C COMMANDS          # Run specific commands instead of "scripts" commands
  -n NETWORK           # Configure the network mode used (or define CI_LOCAL_NETWORK)
                       # Choices: bridge, host, none. Default: bridge
  -e ENV               # Define VARIABLE=value, pass VARIABLE or ENV file
  -E ENGINE            # Force a specific engine (or define CI_LOCAL_ENGINE)
                       # Default list: auto,docker,podman
  -H, --host           # Run jobs on the host rather than containers (or define CI_LOCAL_HOST)
  --notify             # Enable host notifications of pipeline and jobs results
  --privileged [BOOL]  # Give extended privileges to the containers
                       # (Defaults to 'true', or define CI_LOCAL_PRIVILEGED)
  --random-paths       # Mount random folder paths in the container
  -r, --real-paths     # Mount real folder paths in the container (Linux / macOS only)
  -S, --sockets        # Mount engine sockets for nested containers
                       # (Enabled by default with services: docker:*dind)
  --ssh [SSH_USER]     # Bind SSH credentials to a container's user
  -v VOLUME            # Mount VOLUME or HOST:TARGET in containers
  -w WORKDIR           # Override the container's working path

debugging arguments:
  --bash               # Prepare runners for manual bash purposes
  --debug              # Keep runners active for debugging purposes
  --display            # Enable host DISPLAY forwarding features
  --shell SHELL        # Configure the default bash/debug shell entrypoint

jobs arguments:
  --all                # Enable all jobs by default in selections
  --configure          # Show interactive configurations for CI/CD inputs
  --input KEY=VAL      Define KEY=value for CI/CD inputs
  -f, --force          # Force the action (use with --pull)
  -i, --ignore-case    # Ignore case when searching for names
  -m, --manual         # Allow manual jobs to be used
  --no-console         # Disable console launch in bash/debug modes
                       # (or default settings: [runner] > no_console)
  --no-git-safeties    # Disable automated Git safeties configuration
                       # (or default settings: [runner] > no_git_safeties)
  --no-script-fail     # Fail on missing 'script' nodes of jobs
                       # (or default settings: [runner] > no_script_fail)
  -R, --no-regex       # Disable regex search of names
  --no-verbose         # Hide jobs verbose outputs
  --scripts            # Dump parsed jobs entrypoint scripts
  -t TAGS              # Handle listed tags as manual jobs
                       # Default list: deploy,local,publish

features arguments:
  -d, --dump           # Dump parsed .gitlab-ci.yml configuration
  -s, --select         # Force jobs selection from enumerated names
  -l, --list           # Select one job to run (implies --manual)
  --pull               # Pull container images from jobs
  --rmi                # Delete container images from jobs

positional arguments:
  --                   # Positional arguments separator (recommended)
  names                # Names of specific jobs (or stages with --pipeline)
                       # Regex names is supported unless --no-regex is used
```

<!-- readme-help-stop -->
<!-- prettier-ignore-end -->

---

<span class="page-break"></span>

## Additional features in 'variables'

`gcil` implements further support of most command-line parameters  
using `variables:` values, either globally or specifically for each job:

<!-- prettier-ignore-start -->

```yaml
variables:
  CI_LOCAL_AFTER: bool                # Enable or disable `after_script` executions (see `-A`)
  CI_LOCAL_BASH: bool                 # Prepare runners for manual bash purposes (see `--bash`)
  CI_LOCAL_BEFORE: bool               # Enable or disable `before_script` executions (see `-B`)
  CI_LOCAL_DEBUG: bool                # Keep runners active for debugging purposes (see `--debug`)
  CI_LOCAL_DISPLAY: bool              # Enable host `DISPLAY` forwarding features (see `--display`)
  CI_LOCAL_ENGINE: str                # Force a specific engine (see `-E`)
  CI_LOCAL_EXTENDS_INCOMPLETE: bool   # Accept incomplete `extends:` jobs for local use
  CI_LOCAL_HOST: bool                 # Run jobs on the host rather than containers (see `--host`)
  CI_LOCAL_MANUAL: bool               # Allow manual jobs to be used (see `--manual`)
  CI_LOCAL_NETWORK: str               # Configure the network mode used (see `--network`)
  CI_LOCAL_NO_CONSOLE: bool           # Disable console launch in bash/debug modes (see `--no-console`)
  CI_LOCAL_NO_VERBOSE: bool           # Hide jobs verbose outputs (see `--no-verbose`)
  CI_LOCAL_NOTIFY: bool               # Enable host notifications of pipeline and jobs results (see `--notify`)
  CI_LOCAL_PRIVILEGED: bool           # Configure the privileged mode used (see `--privileged`)
  CI_LOCAL_QUIET: bool                # Hide jobs execution context (see `-q`)
  CI_LOCAL_RANDOM_PATHS: bool         # Mount random folder paths in the container (see `--random-paths`)
  CI_LOCAL_REAL_PATHS: bool           # Mount real folder paths in the container (see `-r`)
  CI_LOCAL_SHELL: str                 # Configure the default bash/debug shell entrypoint (see `--shell`)
  CI_LOCAL_SOCKETS: bool              # Mount engine sockets for nested containers (see `-S`)
  CI_LOCAL_SSH: bool|str              # Bind SSH credentials to a container's user (see `--ssh`)
  CI_LOCAL_WORKDIR: str               # Override the container's working path (see `-w`)
```

<!-- prettier-ignore-end -->

## Additional features in '.local'

`gcil` implements further support of most command-line parameters  
inside a `.local:` node to ease default parameters definitions.

Supported local values for a `.local` node are:

<!-- prettier-ignore-start -->

```yaml
.local:
  all: bool              # Enable all jobs by default in selections (see `--all`)
  env: list[str]         # Define `VARIABLE=value`, pass `VARIABLE` or `ENV` file (see `-e`)
  image: dict|str        # Override container image's `name` and/or `entrypoint
  include: dict          # Map `include: project:` names to local paths
  names: list[str]       # Names of specific jobs (or stages with `--pipeline`) (see `names`)
  no_regex: bool         # Disable regex search of names (see `--no-regex`)
  pipeline: bool         # Automatically run pipeline stages rather than jobs (see `-p`)
  tags: list[str]        # Handle listed tags as manual jobs (see `--tags`)
  variables: dict[str]   # Define `KEY: VALUE` variables for local jobs
  version: str           # Define a minimum version for `gcil` recommended for this file
  volumes: dict[str]     # Mount `VOLUME` or `HOST:TARGET` in containers (see `-v`)
```

<!-- prettier-ignore-end -->

Examples for each of these can be found in the `local` unit tests: [tests/local](https://gitlab.com/RadianDevCore/tools/gcil/blob/main/tests/local/.gitlab-ci.yml)
and [tests/includes](https://gitlab.com/RadianDevCore/tools/gcil/blob/main/tests/includes/.gitlab-ci.project.yml)

---

<span class="page-break"></span>

## Job execution in native context

`gcil` runs every jobs in the specified container image.

For specific local purposes where the native host context is wished,  
where the host tools, folders or credentials are required,  
`image: local` can be used to run the scripts natively.

For specific purposes, the `image: local:quiet` variant  
can be used to enable the `quiet` option for specific jobs.

The `image: local:silent` variant extends the `quiet` option  
by also disabling the verbose script `set -x` line entry.

An example usage can be found in the local `Changelog` job: [.gitlab-ci.yml](https://gitlab.com/RadianDevCore/tools/gcil/blob/main/.gitlab-ci.yml)

---

<span class="page-break"></span>

## Environment variables

<details>
  <summary>Expand environment variables documentation</summary>
  <div style="padding-left: 30px">
    <br />

`gcil` uses the variables defined in .gitlab-ci.yml  
and parses the simple environment variables file named `.env`.

If specific environment variables are to be used in the job's container:

- `-e VARIABLE`: pass an environment variable
- `-e VARIABLE=value`: set a variable to a specific value
- `-e ENVIRONMENT_FILE`: parse a file as default variables

For example, `-e TERM=ansi` may enable colored terminal outputs.

The variable `CI_LOCAL` is automatically defined to `true` by `gcil`  
to allow specific conditions for local purposes in jobs' scripts.

The variable `CI_LOCAL_HOST` is automatically defined to `true` by `gcil`  
if running the job natively on the host (for example wiht `--host`)

The following variables are also defined by `gcil`:

- `CI_COMMIT_REF_NAME`: The branch or tag name for which project is built (GitLab CI)
- `CI_COMMIT_REF_SLUG`: CI_COMMIT_REF_NAME in lowercase, shortened to 63 bytes,  
  and with everything except 0-9 and a-z replaced with -. No leading / trailing - (GitLab CI)
- `CI_COMMIT_SHA`: The commit revision for which project is built (GitLab CI)
- `CI_COMMIT_SHORT_SHA`: The first eight characters of CI_COMMIT_SHA (GitLab CI)
- `CI_PROJECT_NAME`: The name of the directory for the project (GitLab CI)
- `CI_PROJECT_NAMESPACE`: The project namespace (username or group name) of the job (GitLab CI)
- `CI_LOCAL_USER_HOST_GID`: The host user's group ID value
- `CI_LOCAL_USER_HOST_UID`: The host user's user ID value
- `CI_LOCAL_USER_HOST_USERNAME`: The host user's username value

  </div>

</details>

---

<span class="page-break"></span>

## Supported container engines

`gcil` currently supports these container engines:

- **Docker :** <https://docs.docker.com/get-docker/> (root daemon, as user or sudoer)
- **Podman :** <https://podman.io/getting-started/> (rootless or root CLI)

---

## Supported systems

<details>
  <summary>Supported Linux systems</summary>
  <div style="padding-left: 30px">

|        Engines        | Linux Mint, Ubuntu | CentOS | Others |
| :-------------------: | :----------------: | :----: | :----: |
|    Native (shell)     |       **✓**        | **✓**  | **?**  |
| Docker (as&nbsp;user) |       **✓**        | **✓**  | **?**  |
| Docker (as&nbsp;root) |       **✓**        | **✓**  | **?**  |
| Podman (as&nbsp;user) |       **~**        | **~**  | **?**  |
| Podman (as&nbsp;root) |       **✓**        | **✓**  | **?**  |

  </div>
</details>

<details>
  <summary>Supported macOS systems</summary>
  <div style="padding-left: 30px">

|        Engines        | macOS (10.14, 10.15, 11.0, ...) |
| :-------------------: | :-----------------------------: |
|    Native (shell)     |              **✓**              |
| Docker (as&nbsp;user) |              **?**              |

  </div>
</details>

<span class="page-break"></span>

<details>
  <summary>Supported Windows systems</summary>
  <div style="padding-left: 30px">

|         Engines         | Windows 10 (1909, 2004, 20H2) | Others |
| :---------------------: | :---------------------------: | :----: |
| Native (Command Prompt) |             **~**             | **?**  |
|    Native (Git Bash)    |             **✓**             | **?**  |
| Docker (Hyper&#8209;V)  |             **✓**             | **?**  |
|   Docker (WSL&nbsp;2)   |             **✓**             | **?**  |

  </div>
</details>

<details>
  <summary>Supported Android systems</summary>
  <div style="padding-left: 30px">

|     Engines     | Android (7.0, 7.1, 8.0, 8.1, 9.0, 10, 11, ...) |
| :-------------: | :--------------------------------------------: |
| Native (Termux) |                     **✓**                      |

  </div>
</details>

---

<span class="page-break"></span>

## Compatible projects

Most GitLab CI projects should work with `gcil` without any local-specific changes.  
However, if specific configurations like credentials, caches or user rights are needed, the `CI_LOCAL` variable can be used.

Projects compatible with `gcil` can use this badge to ease things for developers, both as an indicator and a documentation shortcut button :

> [![gcil](https://img.shields.io/badge/gcil-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/gcil)

```markdown title="Badge in Markdown"
[![gcil](https://img.shields.io/badge/gcil-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/gcil)
```

```html title="Badge in HTML"
<a href="https://radiandevcore.gitlab.io/tools/gcil"><img src="https://img.shields.io/badge/gcil-enabled-brightgreen?logo=gitlab" alt="gcil" style="max-width:100%;"></a>
```

---

<span class="page-break"></span>

## Userspace available settings

`gcil` creates a `settings.ini` configuration file in a userspace folder.

For example, it allows to change the default engines priority (`[engines] > engine`),  
or to disable the automated updates daily check (`[updates] > enabled`)

The `settings.ini` file location and contents can be shown with the following command:

```bash
gcil --settings
```

---

## Environment available configurations

`gcil` uses `colored` for colors outputs and `questionary` for interactive menus.

If colors of both outputs types do not match the terminal's theme,  
an environment variable `NO_COLOR=1` can be defined to disable colors.

---

<span class="page-break"></span>

## Dependencies

- [colored](https://pypi.org/project/colored/): Terminal colors and styles
- [docker](https://pypi.org/project/docker/): Docker Engine API
- [python-dotenv](https://pypi.org/project/python-dotenv/): Support for .env files parsing
- [PyYAML](https://pypi.org/project/PyYAML/): YAML parser and emitter for Python
- [questionary](https://pypi.org/project/questionary/): Interactive terminal user interfaces
- [setuptools](https://pypi.org/project/setuptools/): Build and manage Python packages
- [update-checker](https://pypi.org/project/update-checker/): Check for package updates on PyPI

---

## References

- [.gitlab-ci.yml](https://docs.gitlab.com/ee/ci/yaml/): GitLab CI/CD Pipeline Configuration Reference
- [commitizen](https://pypi.org/project/commitizen/): Simple commit conventions for internet citizens
- [git-cliff](https://github.com/orhun/git-cliff): CHANGELOG generator
- [gitlab-release](https://pypi.org/project/gitlab-release/): Utility for publishing on GitLab
- [OCI](https://opencontainers.org): Open Container Initiative
- [mkdocs](https://www.mkdocs.org/): Project documentation with Markdown
- [mkdocs-coverage](https://pawamoy.github.io/mkdocs-coverage/): Coverage plugin for mkdocs documentation
- [mkdocs-exporter](https://adrienbrignon.github.io/mkdocs-exporter/): Exporter plugin for mkdocs documentation
- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/): Material theme for mkdocs documentation
- [mypy](https://pypi.org/project/mypy/): Optional static typing for Python
- [pexpect-executor](https://radiandevcore.gitlab.io/tools/pexpect-executor): Automate interactive CLI tools actions
- [pre-commit](https://pre-commit.com/): A framework for managing and maintaining pre-commit hooks
- [pre-commit-crocodile](https://radiandevcore.gitlab.io/tools/pre-commit-crocodile): Git hooks intended for developers using pre-commit
- [PyPI](https://pypi.org/): The Python Package Index
- [termtosvg](https://pypi.org/project/termtosvg/): Record terminal sessions as SVG animations
- [Termux](https://termux.com): Linux terminal emulator on Android
- [twine](https://pypi.org/project/twine/): Utility for publishing on PyPI
- [winpty](https://github.com/rprichard/winpty): Windows PTY interface wrapper
