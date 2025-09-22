"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import argparse
import os
import subprocess
from packaging.version import Version, parse
from sapiens_accelerator.commands.config.config_args import default_config_file, load_config_from_file
_description = "Run commands across TPU VMs for initial setup before running `sapiens_accelerator launch`."
def tpu_command_parser(subparsers=None):
    if subparsers is not None: parser = subparsers.add_parser("tpu-config", description=_description)
    else: parser = argparse.ArgumentParser("SapiensAccelerator tpu-config command", description=_description)
    config_args = parser.add_argument_group("Config Arguments", "Arguments that can be configured through `sapiens_accelerator config`.")
    config_args.add_argument("--config_file", type=str, default=None, help="Path to the config file to use for sapiens_accelerator.")
    config_args.add_argument("--tpu_name", default=None, help="The name of the TPU to use. If not specified, will use the TPU specified in the config file.")
    config_args.add_argument("--tpu_zone", default=None, help="The zone of the TPU to use. If not specified, will use the zone specified in the config file.")
    pod_args = parser.add_argument_group("TPU Arguments", "Arguments for options ran inside the TPU.")
    pod_args.add_argument("--use_alpha", action="store_true", help="Whether to use `gcloud alpha` when running the TPU training script instead of `gcloud`.")
    pod_args.add_argument("--command_file", default=None, help="The path to the file containing the commands to run on the pod on startup.")
    pod_args.add_argument("--command", action="append", nargs="+", help="A command to run on the pod. Can be passed multiple times.")
    pod_args.add_argument("--install_sapiens_accelerator", action="store_true", help="Whether to install sapiens_accelerator on the pod. Defaults to False.")
    pod_args.add_argument("--sapiens_accelerator_version", default="latest", help="The version of sapiens_accelerator to install on the pod. If not specified, will use the latest pypi version. Specify 'dev' to install from GitHub.")
    pod_args.add_argument("--debug", action="store_true", help="If set, will print the command that would be run instead of running it.")
    if subparsers is not None: parser.set_defaults(func=tpu_command_launcher)
    return parser
def tpu_command_launcher(args):
    defaults = None
    if args.config_file is not None or os.path.isfile(default_config_file):
        defaults = load_config_from_file(args.config_file)
        if not args.command_file and defaults.command_file is not None and not args.command: args.command_file = defaults.command_file
        if not args.command and defaults.commands is not None: args.command = defaults.commands
        if not args.tpu_name: args.tpu_name = defaults.tpu_name
        if not args.tpu_zone: args.tpu_zone = defaults.tpu_zone
    if args.sapiens_accelerator_version == "latest": args.sapiens_accelerator_version = "sapiens_accelerator -U"
    elif isinstance(parse(args.sapiens_accelerator_version), Version): args.sapiens_accelerator_version = f"sapiens_accelerator=={args.sapiens_accelerator_version}"
    if not args.command_file and not args.command: raise ValueError("You must specify either a command file or a command to run on the pod.")
    if args.command_file:
        with open(args.command_file) as f: args.command = [f.read().splitlines()]
    if isinstance(args.command[0], list): args.command = [line for cmd in args.command for line in cmd]
    new_cmd = ["cd /usr/share"]
    if args.install_sapiens_accelerator: new_cmd += [f"pip install {args.sapiens_accelerator_version}"]
    new_cmd += args.command
    args.command = "; ".join(new_cmd)
    cmd = ["gcloud"]
    if args.use_alpha: cmd += ["alpha"]
    cmd += ["compute", "tpus", "tpu-vm", "ssh", args.tpu_name, "--zone", args.tpu_zone, "--command", args.command, "--worker", "all"]
    if args.debug: return
    subprocess.run(cmd)
def main():
    parser = tpu_command_parser()
    args = parser.parse_args()
    tpu_command_launcher(args)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
