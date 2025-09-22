"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import argparse
from .config import config_command_parser
from .config_args import default_config_file, load_config_from_file
from .default import default_command_parser
from .update import update_command_parser
def get_config_parser(subparsers=None):
    parent_parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    config_parser = config_command_parser(subparsers)
    subcommands = config_parser.add_subparsers(title="subcommands", dest="subcommand")
    default_command_parser(subcommands, parents=[parent_parser])
    update_command_parser(subcommands, parents=[parent_parser])
    return config_parser
def main():
    config_parser = get_config_parser()
    args = config_parser.parse_args()
    if not hasattr(args, "func"):
        config_parser.print_help()
        exit(1)
    args.func(args)
if __name__ == "__main__": main()
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
