import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from extract.fetch_data import fetch_all_assets
from transform.clean_transform import run_transform
from load.load_to_db import run_load

def run_pipeline():
    print(f"\n{'='*50}")
    print(f"Pipeline started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    try:
        print("Step 1: Extract")
        fetch_all_assets()
        print("Step 2: Transform")
        run_transform()
        print("Step 3: Load")
        run_load()
        print(f"Pipeline completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    run_pipeline()
