# Pure Binary Hello World

## Project Overview

This project demonstrates the most fundamental level of programming: creating an executable program by writing raw binary machine code that communicates directly with hardware. Unlike traditional software development that relies on compilers, interpreters, or high-level system abstractions, this approach works with the processor at the level of 0s and 1s.

The resulting executable is a minimal ELF (Executable and Linkable Format) file that contains both the executable structure and machine code instructions to output "Hello World" to the terminal, using direct Linux system calls without any intermediate libraries or kernel abstractions beyond the basic execution environment.

## How It Works

Traditional programs undergo multiple layers of translation and abstraction:
1. Source code (C, Python, etc.)
2. Compilation/interpretation
3. Library function calls
4. Kernel system call interfaces
5. Hardware execution

This project eliminates all intermediate layers. The Python script `make_binary.py` manually constructs:
- **ELF headers** that define the executable structure
- **Program headers** that describe memory layout
- **Raw x86-64 machine code** that makes direct `sys_write` and `sys_exit` system calls
- **String data** embedded within the executable

The generated binary file contains precisely the bytes that the Linux executable loader expects, with instructions that run directly on the CPU.

## Building and Execution

### Prerequisites
- Python 3.x
- Linux operating system (or Docker for non-Linux systems)
- Basic build tools (make, file, hexdump recommended)

### Building the Binary

#### Using Make (Recommended)
```bash
# Clean any previous builds
make clean

# Build the binary
make build

# This will:
# 1. Create the build directory
# 2. Generate hello.bin using make_binary.py
# 3. Set executable permissions
# 4. Verify the file type
```

#### Manual Building
```bash
# Create build directory
mkdir -p build

# Generate the binary
python3 src/make_binary.py build/hello.bin

# Make it executable
chmod +x build/hello.bin

# Verify the file format
file build/hello.bin
# Should show: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked
```

### Executing the Binary

#### Direct Execution (Linux)
```bash
./build/hello.bin
```
This should output: `Hello World`

If your system prevents direct execution or you encounter permission errors, use the Docker method below.

#### Verification and Inspection

After building, verify the binary structure:
```bash
# Run the verification script
python3 verify_binary.py

# Examine the raw bytes
hexdump -C build/hello.bin | head -30

# Check ELF headers
readelf -h build/hello.bin

# Disassemble the machine code (if objdump is available)
objdump -D -b binary -m i386:x86-64 build/hello.bin
```

For deeper inspection:
```bash
# Trace system calls
strace ./build/hello.bin 2>&1 | grep -A5 -B5 "write"

# Debug with gdb
gdb -q ./build/hello.bin -ex 'run' -ex 'quit'
```

### Docker Execution

Use Docker if your operating system doesn't support direct execution of the binary or for testing in a clean environment:

```bash
# Build the Docker image
docker build -t pure-hello-world .

# Run the container
docker run --rm pure-hello-world

# Alternative: mount and test locally built binary
docker run --rm -v $(pwd)/build:/app alpine /app/hello.bin
```

The Docker container provides a consistent Linux environment that guarantees the binary will execute correctly, regardless of your host operating system or configuration.

## Project Structure

```
pure-hello-world/
├── LICENSE                     # MIT License
├── README.md                   # This file
├── Makefile                    # Build automation
├── Dockerfile                  # Container definition
├── .gitignore                  # Git ignore rules
├── src/
│   └── make_binary.py          # Binary generator script
├── verify_binary.py            # Binary verification script
└── build/                      # Output directory (generated)
    └── hello.bin               # Generated binary
```

## Manual Verification Commands

To fully understand what the binary contains, use these inspection commands:

1. **File Type Verification**
   ```bash
   file build/hello.bin
   ```

2. **Hex Dump Analysis**
   ```bash
   # View first 512 bytes in hex and ASCII
   hexdump -C build/hello.bin
   
   # View only ELF header (first 64 bytes)
   hexdump -C build/hello.bin | head -20
   ```

3. **String Extraction**
   ```bash
   strings build/hello.bin
   ```

4. **Size Analysis**
   ```bash
   wc -c build/hello.bin
   ls -lh build/hello.bin
   ```

5. **Run Verification Script**
   ```bash
   python3 verify_binary.py
   ```

## Makefile Targets

The included Makefile provides these commands:

- `make build` - Generate the binary and verify its format
- `make test` - Build and run the binary locally
- `make docker` - Build and run using Docker
- `make clean` - Remove build artifacts and Docker images
- `make all` - Build both local and Docker versions

## Technical Details

### ELF Structure
The binary contains:
- **ELF Header**: Identifies file as executable, specifies 64-bit x86-64 architecture
- **Program Header**: Single loadable segment with read/write/execute permissions
- **Machine Code**: x86-64 instructions for sys_write and sys_exit
- **Data Section**: "Hello World" string with newline

### System Calls
The program uses raw Linux system calls:
- `sys_write(1, "Hello World\n", 12)` - Output to stdout
- `sys_exit(0)` - Clean termination

### Addressing Mode
The code uses RIP-relative addressing (`lea rsi, [rip+offset]`) to locate the string data, ensuring correct memory access regardless of where the binary is loaded.

## Educational Value

This project serves as an educational tool to understand:
- How executable files are structured at the binary level
- How processors execute machine instructions
- How system calls interface with the operating system
- The ELF file format used by Linux
- x86-64 assembly and machine code encoding

By eliminating all software abstraction layers, it provides insight into what happens at the most fundamental level when a program runs.

## License

MIT License - See LICENSE file for details.

Copyright (c) 2026 CodeWithBotina