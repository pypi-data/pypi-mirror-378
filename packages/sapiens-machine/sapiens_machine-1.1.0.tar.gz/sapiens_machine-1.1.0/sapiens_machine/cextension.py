"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from .cuda_setup.main import CUDASetup
from pathlib import Path
import ctypes as ct
import torch
import os
setup = CUDASetup.get_instance()
if setup.initialized != True: setup.run_cuda_setup()
lib = setup.lib
try:
    if lib is None and torch.cuda.is_available():
        CUDASetup.get_instance().generate_instructions()
        CUDASetup.get_instance().print_log_stack()
        raise
    lib.get_context.restype = ct.c_void_p
    lib.get_cusparse.restype = ct.c_void_p
    lib.cget_managed_ptr.restype = ct.c_void_p
    COMPILED_WITH_CUDA = True
except AttributeError as ex: COMPILED_WITH_CUDA = False
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
