"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from setuptools import setup, find_packages
extras = {}
extras["quality"] = ["black~=23.1", "hf-doc-builder==0.5.0", "ruff~=0.6.4"]
extras["docs"] = []
extras["test_prod"] = ["pytest>=7.2.0,<=8.0.0", "pytest-xdist==3.6.1", "pytest-subtests==0.14.1", "parameterized==0.9.0"]
extras["test_dev"] = ["datasets==3.0.1", "diffusers==0.32.2", "evaluate==0.4.3", "torchdata==0.10.1", "torchpippy==0.2.0", "transformers==4.45.2", "scipy==1.15.1", "scikit-learn==1.5.0", "tqdm==4.66.4", "sapiens-machine==1.0.9", "timm==1.0.14"]
extras["testing"] = extras["test_prod"] + extras["test_dev"]
extras["deepspeed"] = ["deepspeed"]
extras["rich"] = ["rich"]
extras["test_trackers"] = ["wandb==0.19.5", "comet-ml==3.48.1", "tensorboard==2.18.0", "dvclive==3.48.1"]
extras["dev"] = extras["quality"] + extras["testing"] + extras["rich"]
extras["sagemaker"] = ["sagemaker==2.239.0"]
setup(
    name="sapiens_accelerator",
    version="1.0.6",
    license="Proprietary Software",
    author="OPENSAPI",
    url="https://github.com/sapiens-technology/sapiens_accelerator",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "sapiens-accelerator=accelerate.commands.accelerate_cli:main",
            "sapiens-accelerator-config=accelerate.commands.config:main",
            "sapiens-accelerator-estimate-memory=accelerate.commands.estimate:main",
            "sapiens-accelerator-launch=accelerate.commands.launch:main",
            "sapiens-accelerator-merge-weights=accelerate.commands.merge:main"
        ]
    },
    python_requires=">=3.9.0",
    install_requires=["numpy", "packaging==24.2", "psutil==6.1.1", "PyYAML==6.0.2", "torch", "huggingface-hub==0.28.1", "safetensors==0.5.2"],
    extras_require=extras
)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
