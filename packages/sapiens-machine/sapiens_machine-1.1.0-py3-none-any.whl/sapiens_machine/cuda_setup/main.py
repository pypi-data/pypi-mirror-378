"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from .env_vars import get_potentially_lib_path_containing_env_vars
from typing import Set, Union
from itertools import product
from pathlib import Path
import ctypes as ct
import errno
import torch
import os
CUDA_RUNTIME_LIBS: list = ["libcudart.so", 'libcudart.so.11.0', 'libcudart.so.12.0']
backup_paths = []
backup_paths.append('$CONDA_PREFIX/lib/libcudart.so.11.0')
class CUDASetup:
    _instance = None
    def __init__(self): raise RuntimeError("Call get_instance() instead")
    def generate_instructions(self):
        if getattr(self, 'error', False): return
        self.error = True
        if not self.cuda_available: return
        if self.cudart_path is None: return
        make_cmd = f'CUDA_VERSION={self.cuda_version_string}'
        if len(self.cuda_version_string) < 3: make_cmd += ' make cuda92'
        elif self.cuda_version_string == '110': make_cmd += ' make cuda110'
        elif self.cuda_version_string[:2] == '11' and int(self.cuda_version_string[2]) > 0: make_cmd += ' make cuda11x'
        elif self.cuda_version_string == '100': return
        has_cublaslt = is_cublasLt_compatible(self.cc)
        if not has_cublaslt: make_cmd += '_nomatmul'
    def initialize(self):
        if not getattr(self, 'initialized', False):
            self.has_printed = False
            self.lib = None
            self.initialized = False
            self.error = False
    def manual_override(self):
        if torch.cuda.is_available():
            if 'BNB_CUDA_VERSION' in os.environ:
                if len(os.environ['BNB_CUDA_VERSION']) > 0: self.binary_name = self.binary_name[:-6] + f'{os.environ["BNB_CUDA_VERSION"]}.so'
    def run_cuda_setup(self):
        self.initialized = True
        self.cuda_setup_log = []
        binary_name, cudart_path, cc, cuda_version_string = evaluate_cuda_setup()
        self.cudart_path = cudart_path
        self.cuda_available = torch.cuda.is_available()
        self.cc = cc
        self.cuda_version_string = cuda_version_string
        self.binary_name = binary_name
        self.manual_override()
        package_dir = Path(__file__).parent.parent
        binary_path = package_dir / self.binary_name
        try:
            if not binary_path.exists():
                legacy_binary_name = "lib_sapiens_machine_cpu.so"
                binary_path = package_dir / legacy_binary_name
                if not binary_path.exists() or torch.cuda.is_available():
                    self.generate_instructions()
                    raise Exception('CUDA SETUP: Setup Failed!')
                self.lib = ct.cdll.LoadLibrary(binary_path)
            else: self.lib = ct.cdll.LoadLibrary(binary_path)
        except Exception as ex: self.add_log_entry(str(ex))
    def add_log_entry(self, msg, is_warning=False): self.cuda_setup_log.append((msg, is_warning))
    def print_log_stack(self): pass
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.initialize()
        return cls._instance
def is_cublasLt_compatible(cc):
    has_cublaslt = False
    if cc is not None:
        cc_major, cc_minor = cc.split('.')
        if int(cc_major) < 7 or (int(cc_major) == 7 and int(cc_minor) < 5): CUDASetup.get_instance().add_log_entry("WARNING: Compute capability < 7.5 detected! Only slow 8-bit matmul is supported for your GPU!", is_warning=True)
        else: has_cublaslt = True
    return has_cublaslt
def extract_candidate_paths(paths_list_candidate: str) -> Set[Path]: return {Path(ld_path) for ld_path in paths_list_candidate.split(":") if ld_path}
def remove_non_existent_dirs(candidate_paths: Set[Path]) -> Set[Path]:
    existent_directories: Set[Path] = set()
    for path in candidate_paths:
        try:
            if path.exists(): existent_directories.add(path)
        except PermissionError as pex: pass
        except OSError as exc:
            if exc.errno != errno.ENAMETOOLONG: raise exc
    non_existent_directories: Set[Path] = candidate_paths - existent_directories
    if non_existent_directories: CUDASetup.get_instance().add_log_entry(f"The following directories listed in your path were found to be non-existent: {non_existent_directories}", is_warning=False)
    return existent_directories
def get_cuda_runtime_lib_paths(candidate_paths: Set[Path]) -> Set[Path]:
    paths = set()
    for libname in CUDA_RUNTIME_LIBS:
        for path in candidate_paths:
            try:
                if (path / libname).is_file(): paths.add(path / libname)
            except PermissionError: pass
    return paths
def resolve_paths_list(paths_list_candidate: str) -> Set[Path]: return remove_non_existent_dirs(extract_candidate_paths(paths_list_candidate))
def find_cuda_lib_in(paths_list_candidate: str) -> Set[Path]: return get_cuda_runtime_lib_paths(resolve_paths_list(paths_list_candidate))
def warn_in_case_of_duplicates(results_paths: Set[Path]) -> None: pass
def determine_cuda_runtime_lib_path() -> Union[Path, None]:
    candidate_env_vars = get_potentially_lib_path_containing_env_vars()
    cuda_runtime_libs = set()
    if "CONDA_PREFIX" in candidate_env_vars:
        conda_libs_path = Path(candidate_env_vars["CONDA_PREFIX"]) / "lib"
        conda_cuda_libs = find_cuda_lib_in(str(conda_libs_path))
        warn_in_case_of_duplicates(conda_cuda_libs)
        if conda_cuda_libs: cuda_runtime_libs.update(conda_cuda_libs)
        CUDASetup.get_instance().add_log_entry(f'{candidate_env_vars["CONDA_PREFIX"]} did not contain {CUDA_RUNTIME_LIBS} as expected! Searching further paths...', is_warning=True)
    if "LD_LIBRARY_PATH" in candidate_env_vars:
        lib_ld_cuda_libs = find_cuda_lib_in(candidate_env_vars["LD_LIBRARY_PATH"])
        if lib_ld_cuda_libs: cuda_runtime_libs.update(lib_ld_cuda_libs)
        warn_in_case_of_duplicates(lib_ld_cuda_libs)
        CUDASetup.get_instance().add_log_entry(f'{candidate_env_vars["LD_LIBRARY_PATH"]} did not contain {CUDA_RUNTIME_LIBS} as expected! Searching further paths...', is_warning=True)
    remaining_candidate_env_vars = {env_var: value for env_var, value in candidate_env_vars.items() if env_var not in {"CONDA_PREFIX", "LD_LIBRARY_PATH"}}
    cuda_runtime_libs = set()
    for env_var, value in remaining_candidate_env_vars.items(): cuda_runtime_libs.update(find_cuda_lib_in(value))
    if len(cuda_runtime_libs) == 0:
        CUDASetup.get_instance().add_log_entry('CUDA_SETUP: WARNING! libcudart.so not found in any environmental path. Searching in backup paths...')
        cuda_runtime_libs.update(find_cuda_lib_in('/usr/local/cuda/lib64'))
    warn_in_case_of_duplicates(cuda_runtime_libs)
    cuda_setup = CUDASetup.get_instance()
    cuda_setup.add_log_entry(f'DEBUG: Possible options found for libcudart.so: {cuda_runtime_libs}')
    return next(iter(cuda_runtime_libs)) if cuda_runtime_libs else None
def get_cuda_version():
    major, minor = map(int, torch.version.cuda.split("."))
    if major < 11: CUDASetup.get_instance().add_log_entry('CUDA SETUP: CUDA version lower than 11 are currently not supported for LLM.int8(). You will be only to use 8-bit optimizers and quantization routines!!')
    return f'{major}{minor}'
def get_compute_capabilities():
    ccs = []
    for i in range(torch.cuda.device_count()):
        cc_major, cc_minor = torch.cuda.get_device_capability(torch.cuda.device(i))
        ccs.append(f"{cc_major}.{cc_minor}")
    return ccs
def evaluate_cuda_setup():
    cuda_setup = CUDASetup.get_instance()
    if not torch.cuda.is_available(): return 'lib_sapiens_machine_cpu.so', None, None, None
    cudart_path = determine_cuda_runtime_lib_path()
    ccs = get_compute_capabilities()
    ccs.sort()
    cc = ccs[-1]
    cuda_version_string = get_cuda_version()
    cuda_setup.add_log_entry(f"CUDA SETUP: PyTorch settings found: CUDA_VERSION={cuda_version_string}, Highest Compute Capability: {cc}.")
    has_cublaslt = is_cublasLt_compatible(cc)
    if has_cublaslt: binary_name = f"lib_sapiens_machine_cuda{cuda_version_string}.so"
    else: binary_name = f"lib_sapiens_machine_cuda{cuda_version_string}_nocublaslt.so"
    return binary_name, cudart_path, cc, cuda_version_string
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
