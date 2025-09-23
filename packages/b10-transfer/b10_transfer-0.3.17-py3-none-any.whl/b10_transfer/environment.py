"""Environment detection utilities for GPU and CPU cache management.

This module provides functions to generate unique environment keys based on
hardware and driver information for cache compatibility.
"""

import hashlib
import json
import platform

# Optional imports - may not be available in all environments
try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    TORCH_AVAILABLE = False

from .logging_utils import get_b10_logger

logger = get_b10_logger(__name__)

KEY_LENGTH = 16
UNKNOWN_HOSTNAME = "unknown-host"


def get_cache_filename() -> str:
    """Get the cache filename prefix for the current environment.

    This function generates a cache filename prefix that includes the
    environment key to ensure cache files are environment-specific
    and unique per machine.

    Returns:
        str: Cache filename prefix in format "cache_{environment_key}".
    """
    env_key = get_environment_key()
    return f"cache_{env_key}"


def get_environment_key() -> str:
    """Generate unique environment key based on PyTorch/CUDA/GPU or CPU configuration.

    This function creates a deterministic hash key based only on node-specific
    hardware and driver information to ensure cache compatibility across
    different environments with identical configurations.

    Returns:
        str: A 16-character hex hash uniquely identifying the environment.

    Raises:
        RuntimeError: If PyTorch is unavailable or environment key
                     generation fails for any reason.

    Note:
        For GPU environments:
        - Includes all GPU properties that affect Triton kernel generation.
        - Device name: GPU model identification (codecache.py:199)
        - CUDA version: Driver compatibility (codecache.py:200)

        For CPU environments:
        - CPU architecture (x86_64, arm64, etc.)
        - Operating system and platform
        - Available CPU instruction sets/features that affect code generation

        Some GPU properties are commented out because:
        1) They are not explicitly used in the torchinductor_root cache check.
        2) It's not clear but likely that any violation of these properties will cause local re-compilation when the torch guards activate, not full recompilation.
        3) We don't want to over-estimate the number of unique environments since that'll cause more cache misses overall.
        We can add them back if we need to.

        We're also not including the torch and triton versions in the hash, despite the torch compilation cache dependent on these two things.
        This is because we are saving the cache to the `/cache/model` directory, which is already deployment-specific where the torch/triton versions are constant.
    """
    try:
        _validate_torch_environment()

        if torch.cuda.is_available():
            # GPU environment
            device_properties = torch.cuda.get_device_properties(
                torch.cuda.current_device()
            )
            node_data = _extract_gpu_properties(
                device_properties, torch.version.cuda
            )
        else:
            # CPU environment
            node_data = _extract_cpu_properties()

        node_json = json.dumps(node_data, sort_keys=True)
        return hashlib.sha256(node_json.encode("utf-8")).hexdigest()[
            :KEY_LENGTH
        ]

    except (ImportError, RuntimeError, AssertionError) as e:
        logger.error(f"[ENVIRONMENT] Environment unavailable: {e}")
        raise RuntimeError(f"Cannot generate environment key: {e}") from e
    except Exception as e:
        logger.error(
            f"[ENVIRONMENT] Unexpected error during environment key generation: {e}"
        )
        raise RuntimeError(f"Environment key generation failed: {e}") from e


def _validate_torch_environment() -> None:
    """Validate that PyTorch is available.

    Raises:
        ImportError: If PyTorch is not available
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch not available")


def _extract_gpu_properties(
    device_properties: any, cuda_version: str
) -> dict[str, any]:
    """Extract relevant GPU properties for environment key generation.

    Args:
        device_properties: CUDA device properties object
        cuda_version: CUDA version string
        SEE docstring of get_environment_key() for more details and why certain properties are excluded.

    Returns:
        Dict containing GPU properties that affect kernel generation
    """
    return {
        "device_name": device_properties.name,  # GPU model
        "cuda_version": cuda_version,  # Driver version
        # "compute_capability": (device_properties.major, device_properties.minor),  # GPU features
        # "multi_processor_count": device_properties.multi_processor_count,  # SM count for occupancy
        # "warp_size": device_properties.warp_size,  # Thread grouping size
        # "regs_per_multiprocessor": getattr(device_properties, "regs_per_multiprocessor", None),  # Register limits
        # "max_threads_per_multi_processor": getattr(device_properties, "max_threads_per_multi_processor", None),  # Thread limits
    }


def _extract_cpu_properties() -> dict[str, any]:
    """Extract relevant CPU properties for environment key generation.

    Returns:
        Dict containing CPU properties that affect kernel generation
    """
    return {
        "device_type": "cpu",
        "cpu_architecture": platform.machine(),  # x86_64, arm64, etc.
        "platform_system": platform.system(),  # Linux, Darwin, Windows
    }
