"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from sapiens_machine.optim.optimizer import Optimizer1State
class Adagrad(Optimizer1State):
    def __init__(self, params, lr=1e-2, lr_decay=0, weight_decay=0, initial_accumulator_value=0, eps=1e-10, optim_bits=32, args=None, min_8bit_size=4096,
    percentile_clipping=100, block_wise=True):
        if not 0.0 <= lr: raise ValueError(f"Invalid learning rate: {lr}")
        if not 0.0 <= weight_decay: raise ValueError(f"Invalid weight_decay value: {weight_decay}")
        if not 0.0 <= eps: raise ValueError(f"Invalid epsilon value: {eps}")
        if initial_accumulator_value != 0.0: raise ValueError("Initial accumulator value != 0.0 not supported!")
        if lr_decay != 0.0: raise ValueError("Lr Decay != 0.0 not supported!")
        super().__init__("adagrad", params, lr, (0.0, 0.0), eps, weight_decay, optim_bits, args, min_8bit_size, percentile_clipping, block_wise)
class Adagrad8bit(Optimizer1State):
    def __init__(self, params, lr=1e-2, lr_decay=0, weight_decay=0, initial_accumulator_value=0, eps=1e-10, optim_bits=8, args=None, min_8bit_size=4096,
    percentile_clipping=100, block_wise=True):
        if not 0.0 <= lr: raise ValueError(f"Invalid learning rate: {lr}")
        if not 0.0 <= weight_decay: raise ValueError(f"Invalid weight_decay value: {weight_decay}")
        if not 0.0 <= eps: raise ValueError(f"Invalid epsilon value: {eps}")
        if initial_accumulator_value != 0.0: raise ValueError("Initial accumulator value != 0.0 not supported!")
        if lr_decay != 0.0: raise ValueError("Lr Decay != 0.0 not supported!")
        assert block_wise
        super().__init__("adagrad", params, lr, (0.0, 0.0), eps, weight_decay, 8, args, min_8bit_size, percentile_clipping, block_wise)
class Adagrad32bit(Optimizer1State):
    def __init__(self, params, lr=1e-2, lr_decay=0, weight_decay=0, initial_accumulator_value=0, eps=1e-10, optim_bits=32, args=None, min_8bit_size=4096,
    percentile_clipping=100, block_wise=True):
        if not 0.0 <= lr: raise ValueError(f"Invalid learning rate: {lr}")
        if not 0.0 <= weight_decay: raise ValueError(f"Invalid weight_decay value: {weight_decay}")
        if not 0.0 <= eps: raise ValueError(f"Invalid epsilon value: {eps}")
        if initial_accumulator_value != 0.0: raise ValueError("Initial accumulator value != 0.0 not supported!")
        if lr_decay != 0.0: raise ValueError("Lr Decay != 0.0 not supported!")
        super().__init__("adagrad", params, lr, (0.0, 0.0), eps, weight_decay, 32, args, min_8bit_size, percentile_clipping, block_wise)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
