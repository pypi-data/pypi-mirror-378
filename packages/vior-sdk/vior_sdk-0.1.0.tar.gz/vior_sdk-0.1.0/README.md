# Vior Secrets SDK (v0.1.0)

The **Vior Secrets SDK** provides a secure, cross-platform way to manage, store, and retrieve your secrets.
It works consistently on **Linux**, **Windows**, and **macOS**.

---

## Installation

### Linux & Windows

The installation process is the same for Linux and Windows. Install directly using pip:

```bash
pip install vior-cli
```

---

### macOS

On macOS, we recommend installing via **pipx** for isolation and easy upgrades.
If you don’t already have Homebrew and pipx installed, run:

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install pipx with Homebrew
brew install pipx

# Ensure pipx is added to your PATH
pipx ensurepath

# Install vior-cli with pipx
pipx install vior-cli
```

---

## Configuration

After installation, configure your credentials:

```bash
vior configure
```

You can obtain your credentials from the **Vior Secrets Console**:
[https://secrets.viorcloud.com](https://secrets.viorcloud.com)

For detailed setup instructions, refer to the documentation:
[https://secrets.viorcloud.com/docs](https://secrets.viorcloud.com/docs)

---

## Usage Examples

Store a new secret:

```bash
vior secrets put my-db-password "supersecret123"
```

Retrieve a secret:

```bash
vior secrets get my-db-password
```

List all secrets:

```bash
vior secrets list
```

Delete a secret:

```bash
vior secrets delete my-db-password
```

---

## Troubleshooting

### 1. CLI not found

```
Error: vior-cli not found on your system.

Hint: Install it using: pip install vior-cli

Note (macOS): Ensure pipx is installed and in PATH. If not, run:
  brew install pipx
  pipx ensurepath
  pipx install vior-cli

For more information, please refer to the documentation: https://secrets.viorcloud.com/docs
```

---

### 2. Authentication error

```
Error: No configuration found on your system.

Hint: Configure your credentials using: vior configure

Note: Please get your credentials from https://secrets.viorcloud.com
      or refer to the documentation at https://secrets.viorcloud.com/docs

For more information, please refer to the documentation.
```

---

## Notes

* Linux and Windows installation steps are **identical** (via pip).
* macOS users should use **pipx** to avoid dependency conflicts.
* Always ensure your credentials are configured before using the SDK.

---

## Documentation

For more information, please refer to the official documentation:
[https://secrets.viorcloud.com/docs](https://secrets.viorcloud.com/docs)

---

## Changelog

### v0.1.0

* Initial release of **Vior Secrets SDK**
* Added cross-platform CLI (`vior-cli`)
* Basic secret management commands: `put`, `get`, `list`, `delete`
* Added configuration via `vior configure`
* Added troubleshooting notes for common errors

---
