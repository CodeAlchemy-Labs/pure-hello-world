#!/usr/bin/env python3
"""
Pure Binary Hello World Generator - Fixed Version
Creates a minimal ELF64 executable that writes "Hello World\n" to stdout.
"""
import struct
import os
import sys

def create_hello_binary(output_path='hello.bin'):
    elf = bytearray()
    
    # ELF Header
    elf.extend(b'\x7fELF')                 # Magic number
    elf.append(2)                          # 64-bit
    elf.append(1)                          # Little endian
    elf.append(1)                          # Version
    elf.append(0)                          # OS ABI
    elf.extend(b'\x00' * 8)                # Padding
    elf.extend(struct.pack('<H', 2))       # ET_EXEC
    elf.extend(struct.pack('<H', 0x3e))    # x86-64
    elf.extend(struct.pack('<I', 1))       # Version
    elf.extend(struct.pack('<Q', 0x400080)) # Entry point
    elf.extend(struct.pack('<Q', 64))      # Program header offset
    elf.extend(struct.pack('<Q', 0))       # No section headers
    elf.extend(struct.pack('<I', 0))       # Flags
    elf.extend(struct.pack('<H', 64))      # ELF header size
    elf.extend(struct.pack('<H', 56))      # Program header size
    elf.extend(struct.pack('<H', 1))       # 1 program header
    elf.extend(struct.pack('<H', 0))       # Section header size
    elf.extend(struct.pack('<H', 0))       # No section headers
    elf.extend(struct.pack('<H', 0))       # No string table
    
    # Program Header (single loadable segment)
    elf.extend(struct.pack('<I', 1))       # PT_LOAD
    elf.extend(struct.pack('<I', 7))       # RWX permissions
    elf.extend(struct.pack('<Q', 0))       # Offset in file
    elf.extend(struct.pack('<Q', 0x400000)) # Virtual address
    elf.extend(struct.pack('<Q', 0x400000)) # Physical address
    elf.extend(struct.pack('<Q', 0x200))   # File size (512 bytes)
    elf.extend(struct.pack('<Q', 0x200))   # Memory size (512 bytes)
    elf.extend(struct.pack('<Q', 0x1000))  # Alignment
    
    # Padding to entry point at 0x400080
    # Current position: 64 + 56 = 120 bytes
    # Need to reach 0x400080 - 0x400000 = 128 bytes from start of segment
    elf.extend(b'\x90' * 8)                # NOP padding (8 bytes)
    
    # Machine code at 0x400080
    # Write "Hello World\n" to stdout
    # rax=1 (sys_write), rdi=1 (stdout), rsi=message, rdx=12
    
    # IMPORTANT FIX: Corrected string address calculation
    # Current RIP when lea executes: 0x400080 + 7 + 7 + 7 = 0x400095
    # String is at: 0x4000c4
    # Offset needed: 0x4000c4 - 0x400095 = 0x2f (47 decimal)
    
    elf.extend(b'\x48\xc7\xc0\x01\x00\x00\x00')  # mov rax, 1
    elf.extend(b'\x48\xc7\xc7\x01\x00\x00\x00')  # mov rdi, 1
    elf.extend(b'\x48\x8d\x35\x2f\x00\x00\x00')  # lea rsi, [rip+0x2f] - FIXED OFFSET
    elf.extend(b'\x48\xc7\xc2\x0c\x00\x00\x00')  # mov rdx, 12
    elf.extend(b'\x0f\x05')                      # syscall
    
    # Exit with code 0
    elf.extend(b'\x48\xc7\xc0\x3c\x00\x00\x00')  # mov rax, 60
    elf.extend(b'\x48\x31\xff')                  # xor rdi, rdi
    elf.extend(b'\x0f\x05')                      # syscall
    
    # Pad to position 0xc4 (196 bytes from start) where string goes
    current_pos = len(elf)
    target_pos = 0xc4
    if current_pos < target_pos:
        elf.extend(b'\x00' * (target_pos - current_pos))
    
    # String data at 0x4000c4
    elf.extend(b'Hello World\n\x00')
    
    # Pad to exactly 512 bytes
    if len(elf) < 0x200:
        elf.extend(b'\x00' * (0x200 - len(elf)))
    
    # Write file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(elf)
    
    os.chmod(output_path, 0o755)
    
    print(f"Created: {output_path} ({len(elf)} bytes)")
    print(f"Entry point: 0x400080")
    print(f"String address: 0x4000c4")
    
    # Calculate the actual offset for verification
    lea_instruction_address = 0x400080 + 14  # After mov rax,1 (7) + mov rdi,1 (7)
    next_instruction_address = lea_instruction_address + 7  # lea is 7 bytes
    string_address = 0x4000c4
    calculated_offset = string_address - next_instruction_address
    print(f"Calculated offset in lea: 0x{calculated_offset:x}")
    
    return True

if __name__ == '__main__':
    output = sys.argv[1] if len(sys.argv) > 1 else 'build/hello.bin'
    try:
        if create_hello_binary(output):
            print("Success!")
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)