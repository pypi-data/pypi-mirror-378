import setuptools
from pathlib import Path

# Define versions
TORCH_VERSION = "2.7.0"
CUDA_VERSION = "cu128"
torch = f"torch=={TORCH_VERSION}"

HERE = Path(__file__).parent
with open(HERE / "requirements.txt") as f:
    requirements = f.read().splitlines()

# Define optional dependencies
extras_require = {
    "cpu": [    
        torch,
        "torchvision",
        "torchaudio",
    ],
    "cuda": [
        # "xformers>=0.0.20",
        # "triton>=2.0.0",
        # "flash-attn>=2.0.0",
        # f"torch=={TORCH_VERSION} --index-url https://download.pytorch.org/whl/{CUDA_VERSION}",
        f"{torch}+{CUDA_VERSION}",
        "torchvision",
        "torchaudio",
        "xformers",
    ],
    "mac": [
        torch,
        "torchvision",
        "torchaudio",
    ],
    "rocm": [
        torch,
        "torchvision",
        "torchaudio",
        # Add any ROCM specific packages here
    ],
    "intel": [
        torch,
        "torchvision",
        "torchaudio",
        # --index-url https://download.pytorch.org/whl/test/xpu
    ],
}

setuptools.setup(
    name="tts_webui",
    # name="tts_webui_deps",
    # packages=setuptools.find_namespace_packages(),
    # packages=["tts_webui"],
    # packages=setuptools.find_namespace_packages(
    #     include=[
    #         "tts_webui.*",
    #     ]
    # ),
    # include_package_data=True,
    packages=[],
    version="0.0.1",
    author="rsxdalv",
    description="TTS WebUI / Harmonica",
    long_description=open(HERE / "README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rsxdalv/tts-webui",
    project_urls={},
    scripts=[],
    install_requires=requirements,
    # install_requires=[],
    extras_require=extras_require,
    dependency_links=[
        # "https://download.pytorch.org/whl/cu128",
    ],
    package_data={"": ["*.json"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
