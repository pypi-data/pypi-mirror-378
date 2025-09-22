"""
	########################################################################################################################################################
	# This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
	# or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
	########################################################################################################################################################
"""
from .adamw import AdamW, AdamW8bit, AdamW32bit, PagedAdamW, PagedAdamW8bit, PagedAdamW32bit
from .adam import Adam, Adam8bit, Adam32bit, PagedAdam, PagedAdam8bit, PagedAdam32bit
from .lion import Lion, Lion8bit, Lion32bit, PagedLion, PagedLion8bit, PagedLion32bit
from sapiens_machine.cextension import COMPILED_WITH_CUDA
from .lars import LARS, LARS8bit, LARS32bit, PytorchLARS
from .adagrad import Adagrad, Adagrad8bit, Adagrad32bit
from .rmsprop import RMSprop, RMSprop8bit, RMSprop32bit
from .lamb import LAMB, LAMB8bit, LAMB32bit
from .optimizer import GlobalOptimManager
from .sgd import SGD, SGD8bit, SGD32bit
"""
	########################################################################################################################################################
	# This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
	# or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
	########################################################################################################################################################
"""
