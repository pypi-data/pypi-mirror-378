"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import argparse
class _StoreAction(argparse.Action):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        new_option_strings = []
        for option_string in self.option_strings:
            new_option_strings.append(option_string)
            if "_" in option_string[2:]: new_option_strings.append(option_string.replace("_", "-"))
        self.option_strings = new_option_strings
    def __call__(self, parser, namespace, values, option_string=None): setattr(namespace, self.dest, values)
class _StoreConstAction(_StoreAction):
    def __init__(self, option_strings, dest, const, default=None, required=False, help=None): super().__init__(option_strings=option_strings, dest=dest, nargs=0, const=const, default=default, required=required, help=help)
    def __call__(self, parser, namespace, values, option_string=None): setattr(namespace, self.dest, self.const)
class _StoreTrueAction(_StoreConstAction):
    def __init__(self, option_strings, dest, default=None, required=False, help=None): super().__init__(option_strings=option_strings, dest=dest, const=True, default=default, required=required, help=help)
class CustomArgumentGroup(argparse._ArgumentGroup):
    def _add_action(self, action):
        args = vars(action)
        if isinstance(action, argparse._StoreTrueAction): action = _StoreTrueAction(args["option_strings"], args["dest"], args["default"], args["required"], args["help"])
        elif isinstance(action, argparse._StoreConstAction): action = _StoreConstAction(args["option_strings"], args["dest"], args["const"], args["default"], args["required"], args["help"])
        elif isinstance(action, argparse._StoreAction): action = _StoreAction(**args)
        action = super()._add_action(action)
        return action
class CustomArgumentParser(argparse.ArgumentParser):
    def add_argument(self, *args, **kwargs):
        if "action" in kwargs:
            if kwargs["action"] == "store_true": kwargs["action"] = _StoreTrueAction
        else: kwargs["action"] = _StoreAction
        super().add_argument(*args, **kwargs)
    def add_argument_group(self, *args, **kwargs):
        group = CustomArgumentGroup(self, *args, **kwargs)
        self._action_groups.append(group)
        return group
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
