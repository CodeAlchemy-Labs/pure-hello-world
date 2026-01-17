#!/usr/bin/env python3
"""
Verify the binary structure
"""
import struct

def verify_binary(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"Verifying {filename} ({len(data)} bytes)")
    
    # Check ELF header
    if data[0:4] != b'\x7fELF':
        print("ERROR: Not an ELF file")
        return
    
    # Get entry point
    entry_point = struct.unpack('<Q', data[24:32])[0]
    print(f"Entry point: 0x{entry_point:x}")
    
    # Find the lea instruction
    # It should be at entry_point + 14 bytes (7 for mov rax,1 + 7 for mov rdi,1)
    lea_offset = entry_point - 0x400000 + 14
    if lea_offset + 7 <= len(data):
        lea_bytes = data[lea_offset:lea_offset+7]
        print(f"LEA instruction at file offset 0x{lea_offset:x}: {lea_bytes.hex()}")
        
        # Extract the offset from lea rsi, [rip+offset]
        if lea_bytes[0:3] == b'\x48\x8d\x35':
            offset = struct.unpack('<i', lea_bytes[3:7])[0]
            print(f"Offset in LEA instruction: 0x{offset:x} ({offset})")
            
            # Calculate what address this points to
            lea_vaddr = entry_point + 14
            next_instruction_vaddr = lea_vaddr + 7
            calculated_string_addr = next_instruction_vaddr + offset
            print(f"LEA virtual address: 0x{lea_vaddr:x}")
            print(f"Next instruction: 0x{next_instruction_vaddr:x}")
            print(f"Calculated string address: 0x{calculated_string_addr:x}")
            
            # Check if string is at that address
            string_offset = calculated_string_addr - 0x400000
            if string_offset + 12 <= len(data):
                string_bytes = data[string_offset:string_offset+12]
                print(f"String at calculated address: {string_bytes}")
            else:
                print(f"ERROR: String offset 0x{string_offset:x} out of range")
        else:
            print(f"ERROR: Not a LEA instruction: {lea_bytes.hex()}")
    
    # Look for the actual string
    string_pos = data.find(b'Hello World')
    if string_pos != -1:
        print(f"Found 'Hello World' at file offset 0x{string_pos:x}")
        print(f"Virtual address: 0x{0x400000 + string_pos:x}")
        print(f"String: {data[string_pos:string_pos+12]}")
    else:
        print("ERROR: 'Hello World' string not found in binary")

if __name__ == '__main__':
    verify_binary('build/hello.bin')