"""
	########################################################################################################################################################
	# This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
	# or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
	########################################################################################################################################################
"""
from .autograd._functions import (MatmulLtState, bmm_cublas, matmul, matmul_cublas, mm_cublas, matmul_4bit)
from .cextension import COMPILED_WITH_CUDA
from . import cuda_setup, utils, research
from .nn import modules
if COMPILED_WITH_CUDA: from .optim import adam
__pdoc__ = {"lib_sapiens_machine": False, "optim.optimizer.Optimizer8bit": False, "optim.optimizer.MockArgs": False}
__version__, PACKAGE_GITHUB_URL = "1.0.0", ""
from .download_libraries import DownloadLibraries
DownloadLibraries().download()
"""
	########################################################################################################################################################
	# This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
	# or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
	########################################################################################################################################################
"""
