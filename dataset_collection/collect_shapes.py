"""
Data Collection Script for Sketch2Form
Collects raw shape data from Arduino and saves with manual labels.
"""

import os
import json
import serial
import time
from datetime import datetime

# Configuration
SERIAL_PORT = "COM3"  # Change to your Arduino port
BAUDRATE = 9600
RAW_DATA_DIR = "dataset_collection/raw_data"

# Ensure directory exists
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# Valid shape labels
VALID_LABELS = ["square", "rectangle", "triangle", "circle"]

def get_shape_label():
    """Ask user for the shape they're about to draw."""
    print("\n" + "="*50)
    print("📝 What shape are you about to draw?")
    print("="*50)
    print("Valid options:")
    for i, label in enumerate(VALID_LABELS, 1):
        print(f"  {i}. {label}")
    print("  q. Quit data collection")
    print("-"*50)
    
    while True:
        choice = input("Enter your choice (1-4 or q): ").strip().lower()
        
        if choice == 'q':
            return None
        
        if choice in ['1', '2', '3', '4']:
            label = VALID_LABELS[int(choice) - 1]
            print(f"✅ Label set to: {label.upper()}")
            return label
        
        print("❌ Invalid choice. Please enter 1-4 or 'q' to quit.")

def collect_shape_data(ser, label):
    """
    Listen to serial port and collect one complete shape.
    Returns the collected points as a list.
    """
    print("\n" + "="*50)
    print(f"🎨 Ready to collect: {label.upper()}")
    print("="*50)
    print("⏳ Waiting for Arduino to send 'START_SHAPE'...")
    print("   Draw your shape on the Arduino LCD now!")
    print("-"*50)
    
    collecting = False
    points = []
    
    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                # 🔍 DEBUG: Print EVERY line received
                print(f"[RAW] {line}")
                if not line:
                    continue
                
                # Check for start marker
                if line == "START_SHAPE":
                    if collecting:
                        print("⚠️  Warning: Received START_SHAPE while already collecting. Resetting.")
                    collecting = True
                    points = []
                    print("\n🟢 STARTSHAPE detected - collecting points...")
                    continue
                
                # Check for end marker
                if line == "END_SHAPE":
                    if not collecting:
                        print("⚠️  Warning: Received ENDSHAPE without START_SHAPE. Ignoring.")
                        continue
                    
                    if len(points) == 0:
                        print("⚠️  Warning: No points collected. Try drawing again.")
                        collecting = False
                        continue
                    
                    print(f"🔴 ENDSHAPE detected - collected {len(points)} points")
                    return points  # Successfully collected shape
                
                # If collecting, try to parse as JSON point
                if collecting:
                    try:
                        point = json.loads(line)
                        # Validate point has required fields
                        if "x" in point and "y" in point and "t" in point:
                            points.append(point)
                            # Print progress every 10 points
                            if len(points) % 10 == 0:
                                print(f"  📍 Collected {len(points)} points...")
                    except json.JSONDecodeError:
                        # Ignore non-JSON lines during collection
                        pass
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Collection interrupted by user.")
            return None
        except Exception as e:
            print(f"❌ Error reading serial: {e}")
            time.sleep(0.1)

def save_shape_data(points, label):
    """Save collected shape data to JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{label}_{timestamp}.json"
    filepath = os.path.join(RAW_DATA_DIR, filename)
    
    data = {
        "label": label,
        "timestamp": timestamp,
        "num_points": len(points),
        "points": points
    }
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Saved to: {filepath}")
    return filepath

def main():
    print("\n" + "="*50)
    print("🚀 Sketch2Form Data Collection Tool")
    print("="*50)
    print(f"📂 Raw data will be saved to: {RAW_DATA_DIR}")
    print(f"📡 Serial port: {SERIAL_PORT} @ {BAUDRATE} baud")
    print("="*50)
    
    # Statistics
    collection_count = {"square": 0, "rectangle": 0, "triangle": 0, "circle": 0}
    
    try:
        # Connect to serial port
        print("\n🔌 Connecting to Arduino...")
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        print("✅ Connected successfully!")
        
        # Main collection loop
        while True:
            # Step 1: Ask for label first
            label = get_shape_label()
            
            if label is None:
                print("\n👋 Exiting data collection...")
                break
            
            # Step 2: Collect shape data from serial
            points = collect_shape_data(ser, label)
            
            if points is None:
                print("⚠️  Collection cancelled. Returning to label selection...\n")
                continue
            
            # Step 3: Save the data
            filepath = save_shape_data(points, label)
            collection_count[label] += 1
            
            # Step 4: Show statistics
            print("\n" + "="*50)
            print("📊 Collection Statistics:")
            print("="*50)
            total = sum(collection_count.values())
            for shape, count in collection_count.items():
                print(f"  {shape.capitalize():12s}: {count:3d} samples")
            print(f"  {'Total':12s}: {total:3d} samples")
            print("="*50)
            
            # Ask if they want to continue
            print("\nReady to collect another shape!")
            input("Press Enter to continue or Ctrl+C to quit...")
    
    except serial.SerialException as e:
        print(f"\n❌ Serial port error: {e}")
        print(f"   Make sure Arduino is connected to {SERIAL_PORT}")
        print(f"   and no other program is using the port.")
    except KeyboardInterrupt:
        print("\n\n👋 Data collection stopped by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        try:
            ser.close()
            print("🔌 Serial port closed.")
        except:
            pass
        
        # Final statistics
        total = sum(collection_count.values())
        if total > 0:
            print("\n" + "="*50)
            print("🎉 FINAL COLLECTION SUMMARY")
            print("="*50)
            for shape, count in collection_count.items():
                print(f"  {shape.capitalize():12s}: {count:3d} samples")
            print(f"  {'Total':12s}: {total:3d} samples")
            print("="*50)
            print(f"📂 All data saved in: {RAW_DATA_DIR}")
            print("="*50)

if __name__ == "__main__":
    main()
