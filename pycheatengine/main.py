from pycheatengine.utils.logging_config import setup_logging

setup_logging()

import psutil
import ctypes
import struct
import numpy as np
import numba
from numba import njit, prange, typed

PROCESS_ALL_ACCESS = 0x1F0FFF
PAGE_READWRITE = 0x04
PAGE_READONLY = 0x02
MEM_COMMIT = 0x1000

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.c_ulong),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.c_ulong),
        ("Protect", ctypes.c_ulong),
        ("Type", ctypes.c_ulong),
    ]

@njit(parallel=True)
def match_values(buffer, value_bytes):
    """Find all occurrences of value_bytes in the buffer."""
    matches = typed.List.empty_list(numba.int64)  # Numba-compatible list
    buffer_length = len(buffer)
    value_length = len(value_bytes)
    for i in prange(buffer_length - value_length + 1):
        match = True
        for j in range(value_length):
            if buffer[i + j] != value_bytes[j]:
                match = False
                break
        if match:
            matches.append(i)
    return matches

def scan_memory(h_process, value, buffer_size=1024 * 1024):
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    ReadProcessMemory = kernel32.ReadProcessMemory
    VirtualQueryEx = kernel32.VirtualQueryEx

    value_bytes = np.frombuffer(struct.pack("i", value), dtype=np.uint8)  # Convert value to NumPy array
    matches = []

    buffer = np.zeros(buffer_size, dtype=np.uint8)  # Use NumPy for the buffer
    mbi = MEMORY_BASIC_INFORMATION()
    address = 0

    while True:
        if VirtualQueryEx(h_process, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0:
            break

        if mbi.State == MEM_COMMIT and (mbi.Protect & (PAGE_READWRITE | PAGE_READONLY)):
            current_address = address
            region_size = mbi.RegionSize
            while current_address < address + region_size:
                chunk_size = min(buffer_size, address + region_size - current_address)
                buffer = np.zeros(chunk_size, dtype=np.uint8)  # Adjust buffer size for the region
                buffer_ptr = buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
                bytes_read = ctypes.c_size_t()

                if ReadProcessMemory(h_process, ctypes.c_void_p(current_address), buffer_ptr, chunk_size, ctypes.byref(bytes_read)):
                    buffer_array = buffer[:bytes_read.value]  # Slice the valid portion
                    relative_matches = match_values(buffer_array, value_bytes)
                    matches.extend([current_address + match for match in relative_matches])
                current_address += chunk_size

        address += mbi.RegionSize

    return matches

def list_processes(user_only=False):
    """List all processes."""
    print("{:<10} {:<30} {}".format("PID", "Process Name", "User"))
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            username = proc.info['username'] if proc.info['username'] else "SYSTEM"
            if not user_only or username != "SYSTEM":
                print("{:<10} {:<30} {}".format(proc.info['pid'], proc.info['name'][:29], username))
        except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
            pass

def open_process(pid):
    """Open a process with full access."""
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h_process:
        raise ctypes.WinError(ctypes.get_last_error())
    return h_process

def main():
    print("Process List:")
    list_processes(user_only=True)

    pid = int(input("\nEnter the PID of the process to scan: "))
    value = int(input("Enter the integer value to search for: "))

    try:
        h_process = open_process(pid)
        print(f"Scanning process {pid} for value {value}...")
        matches = scan_memory(h_process, value)

        if matches:
            print(f"Value {value} found at addresses:")
            for match in matches:
                print(f"0x{match:08X}")
        else:
            print("No matches found.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()