# +-------------------------------------+
# |         ~ Author : Xenely ~         |
# +=====================================+
# | GitHub: https://github.com/Xenely14 |
# | Discord: xenely                     |
# +-------------------------------------+

import ctypes

# Local imports
from .misc import *

# ==-------------------------------------------------------------------== #
# C-consts                                                                #
# ==-------------------------------------------------------------------== #

# Process access flags
PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
PROCESS_QUERY_INFORMATION = 0x0400

# Memory protection constants
PAGE_NOACCESS = 0x01
PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08
PAGE_EXECUTE = 0x10
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
PAGE_GUARD = 0x100
PAGE_NOCACHE = 0x200
PAGE_WRITECOMBINE = 0x400

# Memory state constants
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
MEM_FREE = 0x10000
MEM_PRIVATE = 0x20000
MEM_MAPPED = 0x40000
MEM_IMAGE = 0x1000000

# Memory type constants
MEM_IMAGE = 0x1000000
MEM_MAPPED = 0x40000
MEM_PRIVATE = 0x20000

# ToolHelp32 constants
TH32CS_SNAPPROCESS = 0x00000002
TH32CS_SNAPMODULE = 0x00000008


# ==-------------------------------------------------------------------== #
# C-structs                                                               #
# ==-------------------------------------------------------------------== #
class CLIENT_ID(ctypes.Structure):
    """Client-ID structure that required to open process."""

    _fields_ = [
        ("unique_process", ctypes.c_void_p),
        ("unique_thread", ctypes.c_void_p)
    ]


class OBJECT_ATTRIBUTES(ctypes.Structure):
    """Object attributes structure that can be applied to objects or object handles."""

    _fields_ = [
        ("length", ctypes.c_ulong),
        ("root_directory", ctypes.c_void_p),
        ("object_name", ctypes.c_void_p),
        ("attributes", ctypes.c_ulong),
        ("security_descriptor", ctypes.c_void_p),
        ("security_quality_of_service", ctypes.c_void_p)
    ]


class PROCESSENTRY32(ctypes.Structure):
    """Process entry structure for processes enumeration."""

    _fields_ = [
        ("dw_size", ctypes.c_ulong),
        ("cnt_usage", ctypes.c_ulong),
        ("th32_process_id", ctypes.c_ulong),
        ("th32_default_heap_id", ctypes.c_void_p),
        ("th32_module_id", ctypes.c_ulong),
        ("cnt_threads", ctypes.c_ulong),
        ("th32_parent_process_id", ctypes.c_ulong),
        ("pc_pri_class_base", ctypes.c_long),
        ("dw_flags", ctypes.c_ulong),
        ("sz_exe_file", ctypes.c_char * 260)
    ]

    @property
    def pid(self) -> int:
        """Process ID."""

        return self.th32_process_id

    @property
    def name(self) -> str:
        """Process name."""

        return self.sz_exe_file.decode()


class MODULEENTRY32(ctypes.Structure):
    """Module entry structure, describes an entry from a list of the modules belonging to the specified process."""

    _fields_ = [
        ("dw_size", ctypes.c_ulong),
        ("module_id", ctypes.c_ulong),
        ("process_id", ctypes.c_ulong),
        ("glbl_cnt_usage", ctypes.c_ulong),
        ("proc_cnt_usage", ctypes.c_ulong),
        ("mod_base_addr", ctypes.c_void_p),
        ("mod_base_size", ctypes.c_ulong),
        ("h_module", ctypes.c_void_p),
        ("sz_module", ctypes.c_char * 256),
        ("sz_exe_path", ctypes.c_char * 260)
    ]

    @property
    def name(self) -> str:
        """Process module name."""

        return self.sz_module.decode()

    @property
    def base(self) -> int:
        """Process module base address."""

        return self.mod_base_addr

    @property
    def size(self) -> int:
        """Process module base address."""

        return self.mod_base_size


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    """Memory basic information structure that containg information about a range of pages in the virtual address space of a proces"""

    _fields_ = [
        ("m_base_address", ctypes.c_void_p),
        ("m_allocation_base", ctypes.c_void_p),
        ("m_allocation_protect", ctypes.c_ulong),
        ("m_partition_id", ctypes.c_ushort),
        ("m_region_size", ctypes.c_size_t),
        ("m_state", ctypes.c_ulong),
        ("m_protect", ctypes.c_ulong),
        ("m_type", ctypes.c_ulong)
    ]

    @property
    def base_address(self) -> int:
        """Memory region base address."""

        return self.m_base_address

    @property
    def allocation_base(self) -> int:
        """Memory region allocation base."""

        return self.m_allocation_base

    @property
    def allocation_protect(self) -> int:
        """Memory region allocation protect."""

        return self.m_allocation_protect

    @property
    def partition_id(self) -> int:
        """Memory region partition ID."""

        return self.m_partition_id

    @property
    def region_size(self) -> int:
        """Memory region size."""

        return self.m_region_size

    @property
    def state(self) -> int:
        """Memory region state."""

        return self.m_state

    @property
    def protect(self) -> int:
        """Memory region protect."""

        return self.m_state

    @property
    def type(self) -> int:
        """Memory region type."""

        return self.m_type


# ==-------------------------------------------------------------------== #
# Syscalls                                                                #
# ==-------------------------------------------------------------------== #
_nt_open_process = syscall("NtOpenProcess", result_type=ctypes.c_ulong, arguments_types=[ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(OBJECT_ATTRIBUTES), ctypes.POINTER(CLIENT_ID)])
_nt_close = syscall("NtClose", result_type=ctypes.c_ulong, arguments_types=[ctypes.c_void_p])

_nt_read_virtual_memory = syscall("NtReadVirtualMemory", result_type=ctypes.c_ulong, arguments_types=[ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)])
_nt_write_virtual_memory = syscall("NtWriteVirtualMemory", result_type=ctypes.c_ulong, arguments_types=[ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)])

_nt_virtual_query_memory = syscall("NtQueryVirtualMemory", result_type=ctypes.c_ulong, arguments_types=[ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)])


# ==-------------------------------------------------------------------== #
# Functions                                                               #
# ==-------------------------------------------------------------------== #
def list_processes(include_id: bool = True, include_name: bool = True) -> list[dict[str, int | str]]:
    """List all of the currently active system processes."""

    # If `include_id` and `include_name` disabled both
    if not include_id and not include_name:
        raise Exception("Unable to disable ID and name including at once")

    # Process snapshot functions
    close_handle = ctypes.windll.kernel32.CloseHandle
    process32_next = ctypes.windll.kernel32.Process32Next
    process32_first = ctypes.windll.kernel32.Process32First
    create_tool_help32_snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot

    # Create snapshot to enumerate processes
    if (snapshot := create_tool_help32_snapshot(TH32CS_SNAPPROCESS, 0)) == -1:
        raise Exception("Unable to create snapshot to enumerate processes")

    # Result list of processes
    processes = list()

    # Process enumeration
    try:

        # Process entry to iterate processes
        process_entry = PROCESSENTRY32()
        process_entry.dw_size = ctypes.sizeof(PROCESSENTRY32)

        # Retrieve first process snapshot
        if not process32_first(snapshot, ctypes.byref(process_entry)):
            raise Exception("Unable to get first process to save to snapshot")

        # Iterate all of the processes using snapshot
        while True:

            # Save process to list
            process_dict = dict()

            # If process ID including required
            if include_id:
                process_dict |= {"id": process_entry.pid}

            # If process ID including required
            if include_name:
                process_dict |= {"name": process_entry.name}

            processes.append(process_dict)

            # Snapshot is over
            if not process32_next(snapshot, ctypes.byref(process_entry)):
                break

    finally:

        # Close snapshot handle
        close_handle(snapshot)

    return processes


# ==-------------------------------------------------------------------== #
# Classes                                                                 #
# ==-------------------------------------------------------------------== #
class Process:
    """Basic class of process, have methods to manipulate it."""

    # ==-------------------------------------------------------------------== #
    # Methods                                                                 #
    # ==-------------------------------------------------------------------== #

    def __init__(self, pid_or_name: int | str, access: int = PROCESS_ALL_ACCESS) -> None:
        """Initialize instance to manipulate process."""

        # Open process by it's ID or it's name
        match pid_or_name:

            case pid if type(pid_or_name) is int:
                self.handle, self.name, self.pid = self.__init_with_pid(pid, access)

            case name if type(pid_or_name) is str:
                self.handle, self.name, self.pid = self.__init_with_name(name, access)

            case _:
                raise Exception("Invalid `pid_or_name` argument value, have to be `int` or `str` type")

        # Load SIMD-KMP DLL (Module to blazingly fast pattern scanning)
        self.kmp = ctypes.CDLL("\\".join(__file__.split("\\")[:-1]) + "\\libs\\simdkmp.dll")

    def list_modules(self) -> list[MODULEENTRY32]:
        """List all of the modules loaded to process."""

        # Modules snapshot functions
        close_handle = ctypes.windll.kernel32.CloseHandle
        module32_next = ctypes.windll.kernel32.Module32Next
        module32_first = ctypes.windll.kernel32.Module32First
        create_tool_help32_snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot

        # Create snapshot to enumerate process modules
        if (snapshot := create_tool_help32_snapshot(TH32CS_SNAPMODULE, self.pid)) == -1:
            raise Exception("Unable to create snapshot to enumerate process modules")

        # Result list of process modules
        process_modules = list()

        # Process modules enumeration
        try:

            # Modules entry to iterate process modules
            modules_entry = MODULEENTRY32()
            modules_entry.dw_size = ctypes.sizeof(MODULEENTRY32)

            # Retrieve first process module snapshot
            if not module32_first(snapshot, ctypes.byref(modules_entry)):
                raise Exception("Unable to get first process module to save to snapshot")

            # Iterate all of the process modules using snapshot
            while True:

                # Create deep copy of module entry
                ctypes.memmove(ctypes.byref(module_entry_copy := MODULEENTRY32()), ctypes.byref(modules_entry), ctypes.sizeof(MODULEENTRY32))

                # Save process module to list
                process_modules.append(module_entry_copy)

                # snapshot is over
                if not module32_next(snapshot, ctypes.byref(modules_entry)):
                    break

        finally:

            # Close snapshot handle
            close_handle(snapshot)

        return process_modules

    def list_memory_regions(self, state_filter: int = 0xFFFFFFFF, protect_filter: int = 0xFFFFFFFF, type_filter: int = 0xFFFFFFFF) -> list[MEMORY_BASIC_INFORMATION]:
        """List all of the aviable process memory regions."""

        # Result list of memory regions
        memory_regions = list()

        # Iterate all of the process memory regions
        current_address = 0
        while True:

            # Prepare arguments
            memory_basic_information = MEMORY_BASIC_INFORMATION()

            # Try to get memory region information using it's address
            if (result := _nt_virtual_query_memory(self.handle, ctypes.c_void_p(current_address), 0, ctypes.byref(memory_basic_information), ctypes.sizeof(memory_basic_information), None)):

                # If result failed due out of process memory space bounds
                if result == 0xC000000D:
                    break

                else:
                    raise Exception("NtOpenProcess failed with status: 0x%s" % hex(result)[2:].upper())

            # Save memory region information if filter passed
            if ((memory_basic_information.state & state_filter) == memory_basic_information.state and (memory_basic_information.protect & protect_filter) == memory_basic_information.protect and (memory_basic_information.type & type_filter) == memory_basic_information.type):
                memory_regions.append(memory_basic_information)

            # Move to next memory region
            if (next_address := current_address + memory_basic_information.region_size) <= current_address:
                break

            # Overriding current address
            current_address = next_address

        return memory_regions

    def close(self) -> None:
        """Close opened process using it's handle, have to be called once on stop interacting with process."""

        # Close process
        _nt_close(self.handle)

    # ==-------------------------------------------------------------------== #
    # Private methods                                                         #
    # ==-------------------------------------------------------------------== #
    def __init_with_pid(self, pid: int, access: int, process_name: str | None = None) -> int:
        """Open process handle by it's ID with desired access."""

        # Iterate all of the processes if name not defined
        for process in list_processes():

            # If process have a reqired name
            if process["id"] == pid:

                process_name = process["name"]
                break

        else:
            raise Exception("Process with `%s` ID not found" % pid)

        # Prepare arguments
        object_attributes = OBJECT_ATTRIBUTES()
        object_attributes.length = ctypes.sizeof(OBJECT_ATTRIBUTES)

        client_id = CLIENT_ID()
        client_id.unique_process = pid

        # Try to open process using it's ID
        if (result := _nt_open_process(ctypes.byref(handle := ctypes.c_void_p()), access, ctypes.byref(object_attributes), ctypes.byref(client_id))):

            # If result failed due process ID not found
            if result == 0xC000000B:
                raise Exception("Process with `%s` ID not found" % pid)

            else:
                raise Exception("NtOpenProcess failed with status: 0x%s" % hex(result)[2:].upper())

        return handle.value, process_name, pid

    def __init_with_name(self, name: str, access: int) -> int:
        """Open process hanle by it's name with desired access."""

        # Iterate all of the processes using snapshot
        for process in list_processes():

            # If process have a reqired name
            if process["name"].lower() == name.lower():
                return self.__init_with_pid(process["id"], access, process["name"])

        raise Exception("Process with `%s` name not found" % name)
