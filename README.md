# domainsearch

**domainsearch** is a simple and fast command-line tool that helps you:

- Search if a domain exists (registered) across all known TLDs.
- Check if a domain responds on HTTPS (port 443).
- Save and reuse domain lists.

It fetches the official TLD list from IANA and supports multithreaded scanning for speed.

---

## Installation

First, clone the repository or download the source:

```bash
git clone https://github.com/yourusername/domainsearch.git
cd domainsearch
pip install .
```

Or if you have the `.whl` or `.tar.gz` file:

```bash
pip install domainsearch-0.1-py3-none-any.whl
```

---

## Usage

### Search domains based on a base name:

```bash
domainsearch advania
```

### Search and check HTTPS (port 443):

```bash
domainsearch advania --check-site
```

### Search and save results:

```bash
domainsearch advania --output results.txt
```

### Check HTTPS for domains from a file:

```bash
domainsearch --input results.txt --check-site
```

### Update the list of TLDs from IANA:

```bash
domainsearch --update
```

---

## Options

| Option           | Description                                              |
|------------------|----------------------------------------------------------|
| `--check-site`    | Check if domains respond on port 443 (HTTPS)             |
| `--output <file>` | Save found domains to a file                             |
| `--input <file>`  | Load domains from a file                                 |
| `--timeout <sec>` | Set timeout for HTTPS checks (default: 3 seconds)        |
| `--update`        | Update the TLD list from IANA                            |
| `--help`          | Show help message                                        |

---

## Example

```bash
domainsearch advania --check-site --output results.txt --timeout 5
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Notice

This project includes third-party libraries. See [NOTICE](NOTICE) for details.

