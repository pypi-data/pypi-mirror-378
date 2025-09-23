import json
import sys
from pathlib import Path
from typing import Dict

def load_malicious_packages() -> Dict:
    """Load malicious packages database from JSON file"""
    script_dir = Path(__file__).parent.parent.parent
    malicious_packages_path = script_dir / "malicious_packages.json"
    
    try:
        if not malicious_packages_path.exists():
            print(f"Critical: malicious_packages.json not found at {malicious_packages_path}")
            print("Please ensure malicious_packages.json is in the same directory as this script.")
            sys.exit(1)
        
        with open(malicious_packages_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'malicious_packages' not in data:
            raise ValueError("Invalid JSON structure: 'malicious_packages' array not found")
        
        print(f"Loaded {len(data['malicious_packages'])} malicious package definitions")
        print(f"Last updated: {data.get('metadata', {}).get('last_updated', 'Unknown')}")
        
        return data
        
    except Exception as e:
        print(f"Failed to load or parse malicious_packages.json: {e}")
        print("Please ensure the file exists and is valid JSON.")
        sys.exit(1)
