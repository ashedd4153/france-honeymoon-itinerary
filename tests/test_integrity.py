import json
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

BASE_DIR = Path(__file__).parent.parent
ITINERARY_PATH = BASE_DIR / "itinerary.json"

def test_json_structure():
    """Validates that itinerary.json exists and has required keys."""
    if not ITINERARY_PATH.exists():
        logging.error(f"❌ itinerary.json not found at {ITINERARY_PATH}")
        return False
    
    try:
        with open(ITINERARY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"❌ itinerary.json is not valid JSON: {e}")
        return False

    required_keys = ["destinations", "planning_docs", "trip_title"]
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        logging.error(f"❌ Missing required keys in itinerary.json: {missing_keys}")
        return False
    
    # Check if destinations list is empty (causes st.tabs crash)
    if not data.get("destinations"):
        logging.error("❌ 'destinations' list is empty. This will crash st.tabs.")
        return False

    logging.info("✅ itinerary.json structure is valid.")
    return data

def test_file_references(data):
    """Checks that all external files referenced in JSON actually exist."""
    all_passed = True
    
    # Check Destination Files and Inner Keys
    for dest in data.get("destinations", []):
        name = dest.get("name", "Unknown")
        
        # Check required inner keys
        required_inner = ["dates", "days", "emoji", "file"]
        missing_inner = [k for k in required_inner if k not in dest]
        if missing_inner:
            logging.error(f"❌ Destination '{name}' missing keys: {missing_inner}")
            all_passed = False
            
        file_ref = dest.get("file")
        if file_ref:
            file_path = BASE_DIR / file_ref
            if not file_path.exists():
                logging.error(f"❌ Missing file for {name}: {file_path}")
                all_passed = False
            else:
                logging.info(f"   Found {file_ref}")

    # Check Planning Docs
    for name, file_ref in data.get("planning_docs", {}).items():
        file_path = BASE_DIR / file_ref
        if not file_path.exists():
            logging.error(f"❌ Missing planning doc '{name}': {file_path}")
            all_passed = False
        else:
            logging.info(f"   Found {file_ref}")
            
    return all_passed

def main():
    logging.info("🚀 Starting Dashboard Integrity Test...")
    
    data = test_json_structure()
    if not data:
        sys.exit(1)
        
    if not test_file_references(data):
        logging.error("💥 basic integrity checks failed. Do not start dashboard.")
        sys.exit(1)
        
    logging.info("🎉 All checks passed. Dashboard should be safe to launch.")

if __name__ == "__main__":
    main()
