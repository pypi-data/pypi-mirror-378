import argparse
import json
import os
import re

# Store tracker in home directory
FILE = os.path.expanduser("~/.edtrack/tracker.json")
os.makedirs(os.path.dirname(FILE), exist_ok=True)

def import_tracker(file_path=FILE):
    """Import tracker data from JSON file for other scripts"""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    else:
        return {"emails": [], "sites": []}

def save(data, file_path=FILE):
    """Save tracker data to JSON"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def valid_email(e):
    return re.match(r"[^@]+@[^@]+\.[^@]+", e)

def main():
    data = import_tracker()
    parser = argparse.ArgumentParser(description="Pro Email & Site Tracker")

    # --- Short CLI flags ---
    parser.add_argument("-ade", nargs=1, help="Add a new email")
    parser.add_argument("-ads", nargs=2, metavar=('SITENAME','EMAIL'), help="Add a new site/app under an email")
    parser.add_argument("-ede", nargs=2, metavar=('OLD','NEW'), help="Edit an existing email")
    parser.add_argument("-eds", nargs=3, metavar=('SITENAME','EMAIL','NEWNAME'), help="Edit a site/app name")
    parser.add_argument("-dle", nargs=1, help="Delete an email")
    parser.add_argument("-dls", nargs=2, metavar=('SITENAME','EMAIL'), help="Delete a site/app")
    parser.add_argument("-le", action="store_true", help="List all emails")
    parser.add_argument("-ls", nargs="?", const="", help="List all sites or filter by email")
    parser.add_argument("-se", nargs=1, help="Check if an email exists")
    parser.add_argument("-ss", nargs=1, help="Check which email(s) own a site")
    parser.add_argument("-ce", action="store_true", help="Count total emails")
    parser.add_argument("-cs", action="store_true", help="Count total sites")
    parser.add_argument("-export", nargs=1, metavar="FILE", help="Export tracker data to a JSON file")

    args = parser.parse_args()

    # --- Export ---
    if args.export:
        export_file = args.export[0]
        with open(export_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Exported tracker data to {export_file}")
        return

    # --- Add/Edit/Delete ---
    if args.ade:
        email = args.ade[0]
        if valid_email(email):
            if email not in data["emails"]:
                data["emails"].append(email)
                save(data)
                print(f"Added email: {email}")
            else:
                print("Email already exists!")
        else:
            print("Invalid email format!")

    elif args.ads:
        site, email = args.ads
        if email in data["emails"]:
            data["sites"].append({"site": site, "email": email})
            save(data)
            print(f"Added site {site} under {email}")
        else:
            print("Email not found! Add it first with -ade.")

    elif args.ede:
        old, new = args.ede
        if old in data["emails"]:
            if valid_email(new):
                data["emails"][data["emails"].index(old)] = new
                for s in data["sites"]:
                    if s["email"] == old:
                        s["email"] = new
                save(data)
                print(f"Updated email {old} -> {new}")
            else:
                print("Invalid new email format!")
        else:
            print("Old email not found!")

    elif args.eds:
        site, email, new_name = args.eds
        found = False
        for s in data["sites"]:
            if s["site"] == site and s["email"] == email:
                s["site"] = new_name
                found = True
                save(data)
                print(f"Updated site {site} -> {new_name} for {email}")
                break
        if not found:
            print("Site/email combination not found!")

    elif args.dle:
        email = args.dle[0]
        if email in data["emails"]:
            data["emails"].remove(email)
            data["sites"] = [s for s in data["sites"] if s["email"] != email]
            save(data)
            print(f"Deleted email {email} and all its sites")
        else:
            print("Email not found!")

    elif args.dls:
        site, email = args.dls
        original_len = len(data["sites"])
        data["sites"] = [s for s in data["sites"] if not (s["site"] == site and s["email"] == email)]
        if len(data["sites"]) < original_len:
            save(data)
            print(f"Deleted site {site} for {email}")
        else:
            print("Site/email combination not found!")

    # --- List/Search/Count ---
    elif args.le:
        if data["emails"]:
            print("Tracked emails:")
            for e in data["emails"]:
                print(f"- {e}")
        else:
            print("No emails tracked yet!")

    elif args.ls is not None:
        if args.ls:
            filtered = [s for s in data["sites"] if s["email"] == args.ls]
            if filtered:
                print(f"Sites under {args.ls}:")
                for s in filtered:
                    print(f"- {s['site']}")
            else:
                print("No sites found for this email.")
        else:
            if data["sites"]:
                print("All tracked sites:")
                for s in data["sites"]:
                    print(f"{s['site']} ({s['email']})")
            else:
                print("No sites tracked yet!")

    elif args.se:
        email = args.se[0]
        print("Found!" if email in data["emails"] else "Not found!")

    elif args.ss:
        site = args.ss[0]
        owners = [s["email"] for s in data["sites"] if s["site"] == site]
        if owners:
            print(f"Site {site} belongs to: {', '.join(owners)}")
        else:
            print("Site not found!")

    elif args.ce:
        print(f"Total emails: {len(data['emails'])}")

    elif args.cs:
        print(f"Total sites: {len(data['sites'])}")

    else:
        parser.print_help()
