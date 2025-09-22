"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from sapiens_machine.optim.optimizer import Optimizer1State
class SGD(Optimizer1State):
    def __init__(self, params, lr, momentum=0, dampening=0, weight_decay=0, nesterov=False, optim_bits=32, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True):
        if momentum == 0: raise NotImplementedError("SGD without momentum is not supported!")
        super().__init__("momentum", params, lr, (momentum, dampening), 0.0, weight_decay, optim_bits, args, min_8bit_size, percentile_clipping, block_wise)
class SGD8bit(Optimizer1State):
    def __init__(self, params, lr, momentum=0, dampening=0, weight_decay=0, nesterov=False, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True):
        if momentum == 0: raise NotImplementedError("SGD without momentum is not supported!")
        super().__init__("momentum", params, lr, (momentum, dampening), 0.0, weight_decay, 8, args, min_8bit_size, percentile_clipping, block_wise)
class SGD32bit(Optimizer1State):
    def __init__(self, params, lr, momentum=0, dampening=0, weight_decay=0, nesterov=False, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True):
        if momentum == 0: raise NotImplementedError("SGD without momentum is not supported!")
        super().__init__("momentum", params, lr, (momentum, dampening), 0.0, weight_decay, 32, args, min_8bit_size, percentile_clipping, block_wise)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
