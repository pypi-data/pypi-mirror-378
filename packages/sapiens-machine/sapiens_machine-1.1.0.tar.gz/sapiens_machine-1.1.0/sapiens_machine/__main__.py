"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from os.path import isdir
from typing import Tuple
import subprocess
import shlex
import torch
import sys
import os
HEADER_WIDTH = 60
def execute_and_return(command_string: str) -> Tuple[str, str]:
    def _decode(subprocess_err_out_tuple): return tuple(to_decode.decode("UTF-8").strip() for to_decode in subprocess_err_out_tuple)
    def execute_and_return_decoded_std_streams(command_string): return _decode(subprocess.Popen(shlex.split(command_string), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
    std_out, std_err = execute_and_return_decoded_std_streams(command_string)
    return std_out, std_err
def find_file_recursive(folder, filename):
    cmd = f'find {folder} -name {filename}'
    out, err = execute_and_return(cmd)
    if len(err) > 0: raise RuntimeError('Something when wrong when trying to find file. Maybe you do not have a linux system?')
    return out
def generate_bug_report_information():
    print_header("")
    print_header("BUG REPORT INFORMATION")
    print_header("")
    print('')
    if 'CONDA_PREFIX' in os.environ:
        paths = find_file_recursive(os.environ['CONDA_PREFIX'], '*cuda*so')
        print_header("ANACONDA CUDA PATHS")
        print(paths)
        print('')
    if isdir('/usr/local/'):
        paths = find_file_recursive('/usr/local', '*cuda*so')
        print_header("/usr/local CUDA PATHS")
        print(paths)
        print('')
    if isdir(os.getcwd()):
        paths = find_file_recursive(os.getcwd(), '*cuda*so')
        print_header("WORKING DIRECTORY CUDA PATHS")
        print(paths)
        print('')
    print_header("LD_LIBRARY CUDA PATHS")
    if 'LD_LIBRARY_PATH' in os.environ:
        lib_path = os.environ['LD_LIBRARY_PATH'].strip()
        for path in set(lib_path.split(':')):
            try:
                if isdir(path):
                    print_header(f"{path} CUDA PATHS")
                    paths = find_file_recursive(path, '*cuda*so')
                    print(paths)
            except: print(f'Could not read LD_LIBRARY_PATH: {path}')
    print('')
def print_header(txt: str, width: int = HEADER_WIDTH, filler: str = "+") -> None: pass
def print_debug_info() -> None: pass
from . import COMPILED_WITH_CUDA, PACKAGE_GITHUB_URL
from .cuda_setup.env_vars import to_be_ignored
from .cuda_setup.main import get_compute_capabilities
try:
    from .optim import Adam
    p = torch.nn.Parameter(torch.rand(10, 10).cuda())
    a = torch.rand(10, 10).cuda()
    p1 = p.data.sum().item()
    adam = Adam([p])
    out = a * p
    loss = out.sum()
    loss.backward()
    adam.step()
    p2 = p.data.sum().item()
    assert p1 != p2
    sys.exit(0)
except ImportError: sys.exit(0)
except Exception as e: sys.exit(1)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
