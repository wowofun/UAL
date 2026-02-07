import argparse
import os
import yaml
import sys
import datetime

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from ual.atlas import UniversalAtlas

class PackageManager:
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.packages_dir = os.path.join(self.root_dir, "src/ual/packages")
        os.makedirs(self.packages_dir, exist_ok=True)
        self.atlas = UniversalAtlas()

    def create_package(self, name, start_id):
        """Create a new package template."""
        filename = f"{name}.yaml"
        filepath = os.path.join(self.packages_dir, filename)
        
        if os.path.exists(filepath):
            print(f"❌ Package '{filename}' already exists.")
            return

        # Convert hex string to int if needed
        if isinstance(start_id, str) and start_id.startswith("0x"):
            start_id_int = int(start_id, 16)
        else:
            start_id_int = int(start_id)

        template = {
            "meta": {
                "name": name,
                "author": "Your Name",
                "created": str(datetime.date.today()),
                "version": "0.1.0"
            },
            "concepts": {
                # Example entry
                f"0x{start_id_int:X}": ["example_concept", "alias1"]
            }
        }
        
        with open(filepath, 'w') as f:
            yaml.dump(template, f, sort_keys=False, default_flow_style=False)
            
        print(f"✅ Created package template: {filepath}")
        print(f"👉 Edit this file to add your concepts starting from ID 0x{start_id_int:X}")

    def validate_package(self, filename):
        """Check for ID conflicts."""
        filepath = os.path.join(self.packages_dir, filename)
        if not os.path.exists(filepath):
            print(f"❌ File {filename} not found.")
            return

        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)

        if "concepts" not in data:
            print("⚠️ No 'concepts' section found.")
            return

        conflicts = []
        for sid_str, names in data["concepts"].items():
            sid = int(str(sid_str), 16) if str(sid_str).startswith("0x") else int(sid_str)
            
            # Check against core atlas (excluding the file we are checking ideally, 
            # but UniversalAtlas loads everything on init. 
            # So we check if the ID is already mapped to a DIFFERENT primary name)
            
            existing_name = self.atlas._id_to_concept.get(sid)
            if existing_name and existing_name != names[0]:
                conflicts.append(f"ID {hex(sid)} conflict: '{names[0]}' vs existing '{existing_name}'")

        if conflicts:
            print(f"❌ Validation Failed: {len(conflicts)} conflicts found.")
            for c in conflicts:
                print(f"  - {c}")
        else:
            print("✅ Validation Passed: No ID conflicts detected.")
            print("📦 This package is ready to be committed or shared!")

    def list_packages(self):
        print("📂 Local Packages:")
        for f in os.listdir(self.packages_dir):
            if f.endswith(".yaml"):
                print(f"  - {f}")

def main():
    parser = argparse.ArgumentParser(description="UAL Package Manager")
    subparsers = parser.add_subparsers(dest="command")

    # Create
    create_parser = subparsers.add_parser("create", help="Create a new package")
    create_parser.add_argument("name", help="Package name (e.g. medical_v1)")
    create_parser.add_argument("--start-id", default="0x5000", help="Starting Hex ID (default: 0x5000)")

    # Validate
    val_parser = subparsers.add_parser("validate", help="Validate a package for conflicts")
    val_parser.add_argument("file", help="Filename (e.g. medical_v1.yaml)")

    # List
    subparsers.add_parser("list", help="List installed packages")

    args = parser.parse_args()
    pm = PackageManager()

    if args.command == "create":
        pm.create_package(args.name, args.start_id)
    elif args.command == "validate":
        pm.validate_package(args.file)
    elif args.command == "list":
        pm.list_packages()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
