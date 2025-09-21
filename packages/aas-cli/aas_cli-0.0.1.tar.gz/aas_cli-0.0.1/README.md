<div align="center">
    <img src="https://raw.githubusercontent.com/SmartFactory-KL/aas-cli/main/docs/images/banner-aas-cli-purple-500.png" alt="aas-mcp">
</div>

<div align="center">
  <a href="https://github.com/SmartFactory-KL/aas-cli/actions/workflows/test.yaml"><img src="https://github.com/SmartFactory-KL/aas-cli/actions/workflows/test.yaml/badge.svg" alt="Test"></a>
  <a href="https://codecov.io/gh/SmartFactory-KL/aas-cli"><img src="https://codecov.io/gh/SmartFactory-KL/aas-cli/branch/main/graph/badge.svg" alt="codecov"></a>
  <a href="https://pypi.org/project/aas-cli"><img src="https://img.shields.io/pypi/v/aas-clil?color=%2334D058" alt="PyPI - Version"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
</div>

<p align="center">
    <b>Documentation</b>: <a href="https://shellsmith.pages.dev/cli" target="_blank">https://shellsmith.pages.dev/cli</a>
</p>


**aas-cli** is a Python CLI for managing [Asset Administration Shells (AAS)](https://industrialdigitaltwin.org/en/content-hub/aasspecifications), Submodels, and Submodel Elements via the [Eclipse BaSyx](https://www.eclipse.org/basyx/) REST API.

## Installation

```bash
pip install aas-cli
```

**Requires**: Python 3.10+

## Usage

```bash
aas --help
```

| Command  | Description                                              |
|----------|----------------------------------------------------------|
| `info`   | Display the current Shell tree and identify issues.      |
| `upload` | Upload a single AAS file or all AAS files from a folder. |
| `nuke`   | ☢️ Delete all Shells and Submodels (irrevocable).        |
| `encode` | Encode a value (e.g. Shell ID) to Base64.                |
| `decode` | Decode a Base64-encoded value.                           |
| `get`    | Get Shells, Submodels, and Submodel Elements.            |
| `delete` | Delete Shells, Submodels, or Submodel Elements.          |
| `update` | Update Shells, Submodels, or Submodel Elements.          |
| `create` | Create new Shells, Submodels, or Submodel Elements.      |

> ℹ️ Run `aas <command> --help` to view subcommands and options.

➡️ Full CLI reference: [shellsmith.pages.dev/cli](https://shellsmith.pages.dev/cli)

## Configuration

The default AAS environment host is:

```
http://localhost:8081
```

You can override it in several ways:

- Set the environment variable:  
  ```bash
  SHELLSMITH_BASYX_ENV_HOST=https://your-host:1234
  ```

- Create a `.env` file in your project with:  
  ```dotenv
  SHELLSMITH_BASYX_ENV_HOST=https://your-host:1234
  ```

- Use the `--host` option with any CLI command:  
  ```bash
  aas get shells --host https://your-host:1234
  ```

## 🤝 Contributing

We welcome contributions!

See the [Contributing Guide](https://shellsmith.pages.dev/contributing/) for setup, testing, and coding standards.
