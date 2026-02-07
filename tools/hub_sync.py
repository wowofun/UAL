import argparse
import os
import sys

# Mock Registry for Demo Purposes
# In a real scenario, this would query a central API
REGISTRY = {
    "industry_pack_v1": {
        "description": "Industrial automation concepts (conveyor, arm, weld)",
        "content": """
concepts:
  # Industrial Range (0x2000+)
  0x2001: ["conveyor", "belt"]
  0x2002: ["arm", "manipulator", "robot_arm"]
  0x2003: ["weld", "fuse", "join"]
  0x2004: ["drill", "bore"]
  0x2005: ["inspect_qc", "check_quality"]
"""
    },
    "smart_city_v1": {
        "description": "Smart city infrastructure (traffic_light, sensor, camera)",
        "content": """
concepts:
  # City Range (0x3000+)
  0x3001: ["traffic_light", "signal"]
  0x3002: ["sensor", "detector"]
  0x3003: ["camera", "cctv"]
  0x3004: ["intersection", "junction"]
  0x3005: ["pedestrian", "walker"]
"""
    }
}

def sync_package(package_name):
    print(f"🔄 Syncing package: {package_name}...")
    
    if package_name not in REGISTRY:
        print(f"❌ Package '{package_name}' not found in registry.")
        print("Available packages:", ", ".join(REGISTRY.keys()))
        return
        
    pkg_info = REGISTRY[package_name]
    
    # Simulate download
    content = pkg_info["content"]
    
    # Save to src/ual/packages/
    # Assuming this script is in tools/ and packages should be in src/ual/packages/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Root
    target_dir = os.path.join(base_dir, "src/ual/packages")
    
    if not os.path.exists(target_dir):
        try:
            os.makedirs(target_dir)
        except OSError as e:
            print(f"❌ Failed to create directory {target_dir}: {e}")
            return
        
    target_file = os.path.join(target_dir, f"{package_name}.yaml")
    
    try:
        with open(target_file, "w") as f:
            f.write(content.strip())
        print(f"✅ Package installed to: {target_file}")
        print("Restart your UAL application to load the new concepts.")
    except IOError as e:
        print(f"❌ Failed to write file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UAL Semantic Hub Sync Tool")
    parser.add_argument("package", nargs="?", help="Package name to install")
    parser.add_argument("--list", action="store_true", help="List available packages")
    
    args = parser.parse_args()
    
    if args.list:
        print("📦 Available Packages:")
        for k, v in REGISTRY.items():
            desc = v.get('description', '')
            print(f" - {k}: {desc}")
    elif args.package:
        sync_package(args.package)
    else:
        parser.print_help()
