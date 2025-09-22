"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from sapiens_machine.utils import OutlierTracer, find_outlier_dims
from typing import Optional, TypeVar, Union, overload
from sapiens_machine.optim import GlobalOptimManager
from torch import Tensor, device, dtype, nn
import sapiens_machine as sapiens
import torch.nn.functional as F
import torch
T = TypeVar("T", bound="torch.nn.Module")
class LinearFP8Mixed(nn.Linear):
    def __init__(self, input_features, output_features, bias=True):
        super().__init__(input_features, output_features, bias)
        self.bw_code = None
        self.fw_code = None
        array = [4096, 2048, 1024, 512, 256, 128, 64, 0]
        for i, k in enumerate(array):
            if input_features > array[i + 1]:
                self.bsz = k
                break
        for i, k in enumerate(array):
            if output_features > array[i + 1]:
                self.bsz2 = k
                break
    def forward(self, x: torch.Tensor):
        if self.fw_code is None:
            self.bw_code = sapiens.functional.create_fp8_map(True, 5, 2, 8).to(x.device)
            self.fw_code = sapiens.functional.create_fp8_map(True, 4, 3, 8).to(x.device)
        out = sapiens.research.matmul_fp8_mixed(x, self.weight.t(), fw_code=self.fw_code, bw_code=self.bw_code, bsz=self.bsz, bsz2=self.bsz2)
        if self.bias is not None: out += self.bias
        return out
class LinearFP8Global(nn.Linear):
    def __init__(self, input_features, output_features, bias=True):
        super().__init__(input_features, output_features, bias)
        self.bw_code = None
        self.fw_code = None
        array = [4096, 2048, 1024, 512, 256, 128, 64, 0]
        for i, k in enumerate(array):
            if input_features > array[i + 1]:
                self.bsz = k
                break
        for i, k in enumerate(array):
            if output_features > array[i + 1]:
                self.bsz2 = k
                break
    def forward(self, x: torch.Tensor):
        if self.fw_code is None:
            self.bw_code = sapiens.functional.create_fp8_map(True, 5, 2, 8).to(x.device)
            self.fw_code = sapiens.functional.create_fp8_map(True, 4, 3, 8).to(x.device)
        out = sapiens.matmul_fp8_global(x, self.weight.t(), fw_code=self.fw_code, bw_code=self.bw_code, bsz=self.bsz, bsz2=self.bsz2)
        if self.bias is not None: out += self.bias
        return out
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
