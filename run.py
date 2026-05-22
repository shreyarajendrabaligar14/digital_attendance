import asyncio
import os
import argparse
from app.core.attendance import process_attendance
import json

async def main():
    parser = argparse.ArgumentParser(description="Run Digital Attendance without a web link.")
    parser.add_argument("image_path", help="Path to the classroom image file.")
    args = parser.parse_args()

    if not os.path.exists(args.image_path):
        print(f"Error: Image file not found at {args.image_path}")
        return

    print(f"Processing attendance for image: {args.image_path}...")
    try:
        result = await process_attendance(args.image_path)
        print("\n--- Attendance Result ---")
        print(json.dumps(result, indent=2))
        print("-------------------------")
    except Exception as e:
        print(f"Error during processing: {e}")

if __name__ == "__main__":
    asyncio.run(main())
