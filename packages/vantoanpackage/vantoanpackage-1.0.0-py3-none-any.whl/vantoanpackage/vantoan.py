#!/usr/bin/env python3
import sys
import time

def main():
    if len(sys.argv) < 2:
        print("Lee Vawn Toan - usage: vantoan <command>")
        return

    cmd = sys.argv[1]
    if cmd == "-hi":
        print("VanToan Hello User")
    elif cmd == "-v":
        print("VanToan version 1.0")
        print("Device: Ios")
    elif cmd == "-ffmax":
        print("Loading....")
        time.sleep(2)
        print("Done!")
    elif cmd == "-ffth":
        print("Loading....")
        time.sleep(2)
        print("Done!")
    elif cmd == "help":
        print("vantoan commands:")
        print("vantoan -hi")
        print("vantoan -v")
        print("vantoan -ffmax")
        print("vantoan -ffth")
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()