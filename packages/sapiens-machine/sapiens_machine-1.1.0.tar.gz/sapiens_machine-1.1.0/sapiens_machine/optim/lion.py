"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from sapiens_machine.optim.optimizer import Optimizer1State
class Lion(Optimizer1State):
    def __init__(self, params, lr=1e-4, betas=(0.9, 0.99), weight_decay=0, optim_bits=32, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True, is_paged=False): super().__init__("lion", params, lr, betas, 0., weight_decay, optim_bits, args, min_8bit_size, percentile_clipping, block_wise, is_paged=is_paged)
class Lion8bit(Optimizer1State):
    def __init__(self, params, lr=1e-4, betas=(0.9, 0.99), weight_decay=0, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True, is_paged=False): super().__init__("lion", params, lr, betas, 0., weight_decay, 8, args, min_8bit_size, percentile_clipping, block_wise, is_paged=is_paged)
class Lion32bit(Optimizer1State):
    def __init__(self, params, lr=1e-4, betas=(0.9, 0.99), weight_decay=0, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True, is_paged=False): super().__init__("lion", params, lr, betas, 0., weight_decay, 32, args, min_8bit_size, percentile_clipping, block_wise, is_paged=is_paged)
class PagedLion(Optimizer1State):
    def __init__(self, params, lr=1e-4, betas=(0.9, 0.99), weight_decay=0, optim_bits=32, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True): super().__init__("lion", params, lr, betas, 0., weight_decay, optim_bits, args, min_8bit_size, percentile_clipping, block_wise, is_paged=True)
class PagedLion8bit(Optimizer1State):
    def __init__(self, params, lr=1e-4, betas=(0.9, 0.99), weight_decay=0, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True): super().__init__("lion", params, lr, betas, 0., weight_decay, 8, args, min_8bit_size, percentile_clipping, block_wise, is_paged=True)
class PagedLion32bit(Optimizer1State):
    def __init__(self, params, lr=1e-4, betas=(0.9, 0.99), weight_decay=0, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True): super().__init__("lion", params, lr, betas, 0., weight_decay, 32, args, min_8bit_size, percentile_clipping, block_wise, is_paged=True)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
