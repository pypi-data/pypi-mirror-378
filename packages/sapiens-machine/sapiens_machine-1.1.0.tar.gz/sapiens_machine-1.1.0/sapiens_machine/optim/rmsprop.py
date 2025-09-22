"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from sapiens_machine.optim.optimizer import Optimizer1State
class RMSprop(Optimizer1State):
    def __init__(self, params, lr=1e-2, alpha=0.99, eps=1e-8, weight_decay=0, momentum=0, centered=False, optim_bits=32, args=None,
    min_8bit_size=4096, percentile_clipping=100, block_wise=True):
        if alpha == 0: raise NotImplementedError("RMSprop with alpha==0.0 is not supported!")
        if centered: raise NotImplementedError("Centered RMSprop is not supported!")
        super().__init__("rmsprop", params, lr, (alpha, momentum), eps, weight_decay, optim_bits, args, min_8bit_size, percentile_clipping, block_wise)
class RMSprop8bit(Optimizer1State):
    def __init__(self, params, lr=1e-2, alpha=0.99, eps=1e-8, weight_decay=0, momentum=0, centered=False, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True):
        if alpha == 0: raise NotImplementedError("RMSprop with alpha==0.0 is not supported!")
        if centered: raise NotImplementedError("Centered RMSprop is not supported!")
        super().__init__("rmsprop", params, lr, (alpha, momentum), eps, weight_decay, 8, args, min_8bit_size, percentile_clipping, block_wise)
class RMSprop32bit(Optimizer1State):
    def __init__(self, params, lr=1e-2, alpha=0.99, eps=1e-8, weight_decay=0, momentum=0, centered=False, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True):
        if alpha == 0: raise NotImplementedError("RMSprop with alpha==0.0 is not supported!")
        if centered: raise NotImplementedError("Centered RMSprop is not supported!")
        super().__init__("rmsprop", params, lr, (alpha, momentum), eps, weight_decay, 32, args, min_8bit_size, percentile_clipping, block_wise)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
