"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from sapiens_machine.optim.optimizer import Optimizer2State
class LAMB(Optimizer2State):
    def __init__(self, params, lr=1e-3, bias_correction=True, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, amsgrad=False, adam_w_mode=True, optim_bits=32,
    args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=False, max_unorm=1.0):
        super().__init__("lamb", params, lr, betas, eps, weight_decay, optim_bits, args, min_8bit_size, percentile_clipping, block_wise, max_unorm=1.0)
class LAMB8bit(Optimizer2State):
    def __init__(self, params, lr=1e-3, bias_correction=True, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, amsgrad=False, adam_w_mode=True, args=None,
    min_8bit_size=4096, percentile_clipping=100, block_wise=False, max_unorm=1.0):
        super().__init__("lamb", params, lr, betas, eps, weight_decay, 8, args, min_8bit_size, percentile_clipping, block_wise, max_unorm=1.0)
class LAMB32bit(Optimizer2State):
    def __init__(self, params, lr=1e-3, bias_correction=True, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, amsgrad=False, adam_w_mode=True, args=None,
    min_8bit_size=4096, percentile_clipping=100, block_wise=False, max_unorm=1.0):
        super().__init__("lamb", params, lr, betas, eps, weight_decay, 32, args, min_8bit_size, percentile_clipping, block_wise, max_unorm=1.0)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
