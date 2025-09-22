"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from typing import Dict
import os
def to_be_ignored(env_var: str, value: str) -> bool:
    ignorable = {"PWD", "OLDPWD", "SSH_AUTH_SOCK", "SSH_TTY", "GOOGLE_VM_CONFIG_LOCK_FILE", "HOME", "TMUX", "XDG_DATA_DIRS", "XDG_GREETER_DATA_DIR",
    "XDG_RUNTIME_DIR", "MAIL", "SHELL", "DBUS_SESSION_BUS_ADDRESS", "PATH", "LESSOPEN", "LESSCLOSE", "GOOGLE_VM_CONFIG_LOCK_FILE", "_"}
    return env_var in ignorable
def might_contain_a_path(candidate: str) -> bool: return "/" in candidate
def is_active_conda_env(env_var: str) -> bool: return "CONDA_PREFIX" == env_var
def is_other_conda_env_var(env_var: str) -> bool: return "CONDA" in env_var
def is_relevant_candidate_env_var(env_var: str, value: str) -> bool: return is_active_conda_env(env_var) or (might_contain_a_path(value) and not is_other_conda_env_var(env_var) and not to_be_ignored(env_var, value))
def get_potentially_lib_path_containing_env_vars() -> Dict[str, str]: return {env_var: value for env_var, value in os.environ.items() if is_relevant_candidate_env_var(env_var, value)}
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
