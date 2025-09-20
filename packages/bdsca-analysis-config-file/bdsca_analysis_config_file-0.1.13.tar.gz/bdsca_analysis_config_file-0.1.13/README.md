
# bdsca-analysis-config-file

Utilities and CLI to validate and work with BDSCA analysis configuration files (YAML).

**Note:** Validation, vulnerability triage, and adding new components to the BOM by component purl are implemented. Overwriting component info is *not* implemented yet.

## CLI Usage

All commands are available via the `bdsca-config` CLI:

### Show Version

```
bdsca-config --version
```

### Validate a YAML Configuration File

```
bdsca-config validate <config.yaml> [--output yaml|json|summary] [--target]
```

- Validates the file and prints errors in a table if invalid.
- Use `--output` to pretty-print the file in YAML, JSON, or summary format.
- Use `--target` to print the effective change target (project info).

### Add Missing Components to BOM

```
bdsca-config add-components <config.yaml> --base-url <BLACKDUCK_URL> --api-token <TOKEN> [--insecure] [--verbosity info|debug]
```

- Adds missing components from `componentAdditions` to the BOM for each project in the config.
- Only the `purl` field is allowed in `componentAdditions.component`. Extra fields are rejected by schema validation.

Example config:

```
componentAdditions:
	- component:
			purl: pkg:pypi/sample@1.0.0
```

### Remediate Vulnerabilities

```
bdsca-config remediate <config.yaml> --base-url <BLACKDUCK_URL> --api-token <TOKEN> [--insecure] [--verbosity info|debug] [--dryrun]
```

- Validates the file and performs remediation using Black Duck.
- Use `--dryrun` to preview changes without making updates.

### Module Usage

You can also run commands via Python module execution:

```
python -m bdsca_analysis_config_file --version
python -m bdsca_analysis_config_file validate examples/example.yaml
```

## Configuration Shape & Examples

- `specVersion`: "1"
- `changeTarget`: array of targets; each target is an object with a required project:

```
changeTarget:
	- project:
			name: example-project
			version: "1.0"
	- project:
			name: another-project
			version: "main"
```

- `vulnerabilityTriages` are specified at the top level and apply to all target projects:

```
vulnerabilityTriages:
	- component:
			name: lib-a
			codetype: python
			vendor: vendor-a
			version: "1.2.3"
		triages:
			- cve: CVE-2024-0001
				resolution: PATCHED
				comment: fixed upstream
```

- `componentAdditions` for adding components by purl:

```
componentAdditions:
	- component:
			purl: pkg:pypi/sample@1.0.0
```

## Output Examples

- Single project summary:

```
bdsca-config validate examples/example.yaml --output summary --target
...
target: project name='example-project' version='1.0'
```

- Multiple projects summary:

```
bdsca-config validate examples/example2.yaml --output summary --target
...

	- project name='HippotechOrg/sampleapp' version='main'
	- project name='HippotechOrg/anotherapp' version='1.2.3'
```

## Features

- Modern src/ layout with pyproject.toml
- CLI with validation, remediation, and BOM addition
- Tests via pytest, lint via ruff and black, typing via mypy
- Pre-commit hooks and GitHub Actions CI

## Quickstart

Install in editable mode with dev tools and run tests:

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .[dev]
pytest
```

## Installation

To install the package locally after building:

```
python -m build
pip install dist/bdsca_analysis_config_file-<version>-py3-none-any.whl
```

Replace `<version>` with the actual version number (e.g. 0.1.8).

To install from PyPI or TestPyPI:

```
pip install bdsca-analysis-config-file
```

Or from TestPyPI:

```
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple bdsca-analysis-config-file
```

## Release Script

To build, version, and (optionally) upload the package, use the PowerShell release script:

```
powershell -NoProfile -ExecutionPolicy Bypass -File release.ps1 -Part patch -Repository testpypi
```

Example: local build and install test with custom pip arguments (no upload):

```
powershell -NoProfile -ExecutionPolicy Bypass -File release.ps1 -Part patch -Repository testpypi -NoUpload -PipArgs "--timeout 30 --retries 1 --trusted-host pypi.org --trusted-host files.pythonhosted.org"
```

This bumps the patch version, builds the package, uploads to TestPyPI, and verifies install. You can use other options:

- `-Part minor` or `-Part major` to bump minor/major version
- `-NewVersion 0.2.0` to set an explicit version
- `-Repository pypi` to upload to PyPI
- `-NoUpload` to skip upload (local build only)
- `-NoInstallTest` to skip install verification
- `-SkipToolsUpgrade` to skip pip/build/twine upgrade
- `-DryRun` to preview actions without executing

See the script header for full option documentation.

## Dry-run Mode

- Use the `--dryrun` flag with the `remediate` command to see what would change without making any updates to Black Duck.
- For each matched vulnerable component, the CLI prints the current remediation status and comment alongside the new values that would be applied.
- No PUT requests are sent in dry-run mode, and the command returns success if the preview steps complete.
- specVersion: "1"
- changeTarget: array of targets; each target is an object with a required project:

```
changeTarget:
	- project:
			name: example-project
			version: "1.0"
	- project:
			name: another-project
			version: "main"
```

+- vulnerabilityTriages are specified at the top level and apply to all target projects.

```
vulnerabilityTriages:
	- component:
			name: lib-a
			codetype: python
			vendor: vendor-a
			version: "1.2.3"
		triages:
			- cve: CVE-2024-0001
				resolution: PATCHED
				comment: fixed upstream
```

The CLI applies these triages for each project listed in changeTarget.

## Target display

- Single project summary:

```
bdsca-config validate examples/example.yaml --output summary --target
...
target: project name='example-project' version='1.0'
```

- Multiple projects summary lists each project on its own line:

```
bdsca-config validate examples/example2.yaml --output summary --target
...
target:
	- project name='HippotechOrg/sampleapp' version='main'
	- project name='HippotechOrg/anotherapp' version='1.2.3'
```

## License

MIT © Jouni Lehto

## Release script

To build, version, and (optionally) upload the package, use the PowerShell release script:

```
powershell -NoProfile -ExecutionPolicy Bypass -File release.ps1 -Part patch -Repository testpypi
```

Example: local build and install test with custom pip arguments (no upload):

```
powershell -NoProfile -ExecutionPolicy Bypass -File release.ps1 -Part patch -Repository testpypi -NoUpload -PipArgs "--timeout 30 --retries 1 --trusted-host pypi.org --trusted-host files.pythonhosted.org"
```

This bumps the patch version, builds the package, uploads to TestPyPI, and verifies install. You can use other options:

- `-Part minor` or `-Part major` to bump minor/major version
- `-NewVersion 0.2.0` to set an explicit version
- `-Repository pypi` to upload to PyPI
- `-NoUpload` to skip upload (local build only)
- `-NoInstallTest` to skip install verification
- `-SkipToolsUpgrade` to skip pip/build/twine upgrade
- `-DryRun` to preview actions without executing

See the script header for full option documentation.
## Dry-run mode

- Use the `--dryrun` flag with the `remediate` command to see what would change without making any updates to Black Duck.
- For each matched vulnerable component, the CLI prints the current remediation status and comment alongside the new values that would be applied.
- No PUT requests are sent in dry-run mode, and the command returns success if the preview steps complete.