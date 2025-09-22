"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from sapiens_accelerator.commands.config import get_config_parser
from sapiens_accelerator.commands.env import env_command_parser
from sapiens_accelerator.commands.estimate import estimate_command_parser
from sapiens_accelerator.commands.launch import launch_command_parser
from sapiens_accelerator.commands.merge import merge_command_parser
from sapiens_accelerator.commands.test import test_command_parser
from sapiens_accelerator.commands.tpu import tpu_command_parser
from sapiens_accelerator.commands.utils import CustomArgumentParser
def main():
    parser = CustomArgumentParser("SapiensAccelerator CLI tool", usage="sapiens_accelerator <command> [<args>]", allow_abbrev=False)
    subparsers = parser.add_subparsers(help="sapiens_accelerator command helpers")
    get_config_parser(subparsers=subparsers)
    estimate_command_parser(subparsers=subparsers)
    env_command_parser(subparsers=subparsers)
    launch_command_parser(subparsers=subparsers)
    merge_command_parser(subparsers=subparsers)
    tpu_command_parser(subparsers=subparsers)
    test_command_parser(subparsers=subparsers)
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        exit(1)
    args.func(args)
if __name__ == "__main__": main()
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
