"""
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

DEFAULT_PROJECT_COMMIT = "main"
DEFAULT_SEED_FRAMEWORK = "jax"
DEFAULT_SEED_CONFIG_FILE = "jax_seed.yaml"
DEFAULT_PYTHON_VERSION = "3.12"
DEFAULT_HARDWARE = "tpu"
DEFAULT_BUILD_PROJECT = False
SUPPORTED_HARDWARE = ["tpu", "gpu"]

# TODO(kanglant): Add a function to list deps following the pattern "nvidia-*"
GPU_SPECIFIC_DEPS = [
  "nvidia-cublas-cu12",
  "nvidia-cuda-cupti-cu12",
  "nvidia-cuda-nvcc-cu12",
  "nvidia-cuda-nvrtc-cu12",  # Remove?
  "nvidia-cuda-runtime-cu12",
  "nvidia-cudnn-cu12",
  "nvidia-cufft-cu12",
  "nvidia-cusolver-cu12",
  "nvidia-cusparse-cu12",
  "nvidia-nccl-cu12",
  "nvidia-nvjitlink-cu12",
  "nvidia-nvshmem-cu12",
  "nvidia-nvshmem-cu13",
  "nvidia-cublas",
  "nvidia-cuda-crt",
  "nvidia-cuda-cupti",
  "nvidia-cuda-nvcc",
  "nvidia-cuda-nvrtc",
  "nvidia-cuda-runtime",
  "nvidia-cudnn-cu13",
  "nvidia-cufft",
  "nvidia-cusolver",
  "nvidia-cusparse",
  "nvidia-nccl-cu13",
  "nvidia-nvjitlink",
  "nvidia-nvvm",
  "jax-cuda12-plugin",
  "jax-cuda13-plugin",
  "jax-cuda12-pjrt",
  "jax-cuda13-pjrt",
  "transformer-engine",
]

TPU_SPECIFIC_DEPS = [
  "libtpu",
]
