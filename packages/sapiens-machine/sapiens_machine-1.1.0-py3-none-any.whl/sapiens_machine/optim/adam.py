"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from sapiens_machine.optim.optimizer import Optimizer2State
import sapiens_machine.functional as F
import torch.distributed as dist
import torch
import math
import os
class Adam(Optimizer2State):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, amsgrad=False, optim_bits=32, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True, is_paged=False):
        super().__init__( "adam", params, lr, betas, eps, weight_decay, optim_bits, args, min_8bit_size, percentile_clipping, block_wise, is_paged=is_paged)
class Adam8bit(Optimizer2State):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, amsgrad=False, optim_bits=32, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True, is_paged=False):
        super().__init__( "adam", params, lr, betas, eps, weight_decay, 8, args, min_8bit_size, percentile_clipping, block_wise, is_paged=is_paged)
class Adam32bit(Optimizer2State):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, amsgrad=False, optim_bits=32, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True, is_paged=False):
        super().__init__( "adam", params, lr, betas, eps, weight_decay, 32, args, min_8bit_size, percentile_clipping, block_wise, is_paged=is_paged)
class PagedAdam(Optimizer2State):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, amsgrad=False, optim_bits=32, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True, is_paged=False):
        super().__init__( "adam", params, lr, betas, eps, weight_decay, optim_bits, args, min_8bit_size, percentile_clipping, block_wise, is_paged=True)
class PagedAdam8bit(Optimizer2State):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, amsgrad=False, optim_bits=32, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True, is_paged=False):
        super().__init__( "adam", params, lr, betas, eps, weight_decay, 8, args, min_8bit_size, percentile_clipping, block_wise, is_paged=True)
class PagedAdam32bit(Optimizer2State):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, amsgrad=False, optim_bits=32, args=None, min_8bit_size=4096, percentile_clipping=100, block_wise=True, is_paged=False):
        super().__init__( "adam", params, lr, betas, eps, weight_decay, 32, args, min_8bit_size, percentile_clipping, block_wise, is_paged=True)
class AnalysisAdam(torch.optim.Optimizer):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, amsgrad=False, sapiens_analysis="dynamic-blockwise", savedir=None):
        defaults = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay, amsgrad=amsgrad)
        super().__init__(params, defaults)
        self.analysis = sapiens_analysis
        self.savedir = savedir
    @property
    def supports_memory_efficient_fp16(self): return True
    @property
    def supports_flat_params(self): return True
    def step(self, closure=None):
        loss = None
        if closure is not None: loss = closure()
        for group in self.param_groups:
            for p_id, p in enumerate(group["params"]):
                if p.grad is None: continue
                grad = p.grad.data
                if grad.dtype in {torch.float16, torch.bfloat16}: grad = grad.float()
                if grad.is_sparse: raise RuntimeError("Adam does not support sparse gradients, please consider SparseAdam instead")
                amsgrad = group.get("amsgrad", False)
                assert not amsgrad
                p_data_fp32 = p.data
                if p.data.dtype in {torch.float16, torch.bfloat16}: p_data_fp32 = p_data_fp32.float()
                state = self.state[p]
                if len(state) == 0:
                    state["step"] = 0
                    state["exp_avg"] = torch.zeros_like(p_data_fp32)
                    state["exp_avg_sq"] = torch.zeros_like(p_data_fp32)
                    state["abserrors"] = torch.zeros((256, 256), device=p_data_fp32.device)
                    state["relerrors"] = torch.zeros((256, 256), device=p_data_fp32.device)
                    state["counts"] = torch.zeros((256, 256), device=p_data_fp32.device)
                    if amsgrad: state["max_exp_avg_sq"] = torch.zeros_like(p_data_fp32)
                else:
                    state["exp_avg"] = state["exp_avg"].to(p_data_fp32)
                    state["exp_avg_sq"] = state["exp_avg_sq"].to(p_data_fp32)
                    if amsgrad: state["max_exp_avg_sq"] = state["max_exp_avg_sq"].to(p_data_fp32)
                state["step"] += 1
                beta1, beta2 = group["betas"]
                bias_correction1 = 1 - beta1 ** state["step"]
                bias_correction2 = 1 - beta2 ** state["step"]
                step_size = (group["lr"] * math.sqrt(bias_correction2) / bias_correction1)
                e = state["abserrors"]
                rele = state["relerrors"]
                counts = state["counts"]
                if group["weight_decay"] != 0: p_data_fp32.add_(p_data_fp32, alpha=-group["weight_decay"] * group["lr"])
                exp_avg, exp_avg_sq = state["exp_avg"], state["exp_avg_sq"]
                if amsgrad: max_exp_avg_sq = state["max_exp_avg_sq"]
                exp_avg.mul_(beta1).add_(grad, alpha=1 - beta1)
                exp_avg_sq.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)
                denom = exp_avg_sq.sqrt().add_(group["eps"])
                update_fp32 = exp_avg / denom
                if (p_data_fp32.numel() <= 8192 or p_data_fp32.numel() > 50000 * 1000): p_data_fp32 += -step_size * update_fp32
                else:
                    if self.analysis == "dynamic-blockwise":
                        code1 = F.create_dynamic_map(signed=True).to(p.device)
                        code2 = F.create_dynamic_map(signed=False).to(p.device)
                        C1, S1 = F.quantize_blockwise(exp_avg, code=code1)
                        state1 = F.dequantize_blockwise(C1, S1)
                        C2, S2 = F.quantize_blockwise(exp_avg_sq, code=code2)
                        state2 = F.dequantize_blockwise(C2, S2)
                    elif self.analysis == "dynamic":
                        code1 = F.create_dynamic_map(signed=True).to(p.device)
                        code2 = F.create_dynamic_map(signed=False).to(p.device)
                        C1, S1 = F.quantize(exp_avg, code=code1)
                        state1 = F.dequantize(C1, S1)
                        C2, S2 = F.quantize(exp_avg_sq, code=code2)
                        state2 = F.dequantize(C2, S2)
                    elif self.analysis == "linear":
                        code1 = F.create_linear_map(signed=True).to(p.device)
                        code2 = F.create_linear_map(signed=False).to(p.device)
                        C1, S1 = F.quantize(exp_avg, code=code1)
                        state1 = F.dequantize(C1, S1)
                        C2, S2 = F.quantize(exp_avg_sq, code=code2)
                        state2 = F.dequantize(C2, S2)
                    elif self.analysis == "quantile":
                        code1 = F.estimate_quantiles(exp_avg)
                        code2 = F.estimate_quantiles(exp_avg_sq)
                        C1 = F.quantize_no_absmax(exp_avg, code=code1)
                        state1 = F.dequantize_no_absmax(C1, code1)
                        C2 = F.quantize_no_absmax(exp_avg_sq, code=code2)
                        state2 = F.dequantize_no_absmax(C2, code2)
                    elif self.analysis == "my-quantization-routine": pass
                    else: raise ValueError(f"Invalid analysis value: {self.analysis}!")
                    denom = state2.sqrt().add_(group["eps"])
                    update_8bit = state1 / denom
                    abserr = torch.abs(update_8bit - update_fp32)
                    relerr = abserr / torch.abs(update_fp32 + 1e-6)
                    C1, C2 = C1.int(), C2.int()
                    F.histogram_scatter_add_2d(e, C1.int(), C2.int(), abserr)
                    F.histogram_scatter_add_2d(rele, C1.int(), C2.int(), relerr)
                    F.histogram_scatter_add_2d(counts, C1.int(), C2.int(), torch.ones_like(abserr))
                    p_data_fp32 += -step_size * update_fp32
                    if not dist.is_initialized() or dist.get_rank() == 0:
                        if self.savedir != "" and state["step"] % 100 == 0:
                            if not os.path.exists(self.savedir): os.makedirs(self.savedir)
                            shapestr = "_".join([str(dim) for dim in p_data_fp32.shape])
                            pathe = os.path.join(self.savedir, f"{p_id}_{shapestr}_abserr.pkl")
                            pathrele = os.path.join(self.savedir, f"{p_id}_{shapestr}_relerr.pkl")
                            pathcounts = os.path.join(self.savedir, f"{p_id}_{shapestr}_counts.pkl")
                            torch.save(e, pathe)
                            torch.save(rele, pathrele)
                            torch.save(counts, pathcounts)
                if p.data.dtype in {torch.float16, torch.bfloat16}: p.data.copy_(p_data_fp32)
        return loss
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
