# edtrack

⚡ **edtrack** is a tiny CLI tool for keeping track of emails and the sites/apps tied to them.  
Store everything in a single JSON file—easy to share, easy to back up, zero fluff.

---

## ✨ Features

- Add / edit / delete emails  
- Add / edit / delete sites linked to emails  
- List, search, and count emails or sites  
- Export all data to a JSON backup  
- Works fully offline, no encryption (simple and transparent)

Data lives at:

```
~/.edtrack/tracker.json
```

---

## 🛠️ Installation

Python 3.7+ required.

```bash
pip install edtrack
```

---

## 🚀 Usage

Run the CLI:

```bash
edtrack [flags] [arguments]
```

### Core Flags (short & speedy)

| Flag      | Args                       | Action                                  |
|-----------|-----------------------------|-----------------------------------------|
| `-ade`    | `<email>`                   | Add email                               |
| `-ads`    | `<site> <email>`            | Add site/app under an email             |
| `-ede`    | `<old_email> <new_email>`   | Edit email                              |
| `-eds`    | `<site> <email> <new_name>` | Edit site/app name                      |
| `-del`    | `<email>`                   | Delete email & all its sites            |
| `-dls`    | `<site> <email>`            | Delete site from a specific email       |
| `-le`     | none                        | List all emails                         |
| `-ls`     | `[email]` (optional)        | List all sites or only sites for email  |
| `-se`     | `<email>`                   | Search for an email                     |
| `-ss`     | `<site>`                    | Search which email(s) own a site        |
| `-ce`     | none                        | Count total emails                      |
| `-cs`     | none                        | Count total sites                       |
| `-export` | `<file.json>`               | Export data to a JSON file              |

---

### Examples

```bash
# Add an email
edtrack -ade bro@example.com

# Add a site under that email
edtrack -ads GitHub bro@example.com

# Edit an email
edtrack -ede bro@example.com bro2@example.com

# Edit a site name
edtrack -eds GitHub bro2@example.com Forgejo

# List all emails
edtrack -le

# List all sites or only for one email
edtrack -ls
edtrack -ls bro2@example.com

# Search
edtrack -se bro2@example.com
edtrack -ss Forgejo

# Counts
edtrack -ce
edtrack -cs

# Export full database
edtrack -export backup.json
```

---

## 🧩 Import From Python

Need the data inside another script?  
```python
from edtrack import import_tracker

data = import_tracker()
print(data["emails"])
print(data["sites"])
```

---

## 📜 License

MIT – do whatever you want, just don’t sue the author.

---

*Built with ❤️ by people who like short flags and clean JSON.*
