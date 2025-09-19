# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import gettext
import inspect
import io
import os
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, RawTextHelpFormatter
from contextlib import redirect_stdout
from typing import TextIO

from ._categories import DefaultCategoryRules
from ._cli import create_validation_parser
from ._requirements import RequirementsRegistry


def _generate_rules_documentation(fptr: TextIO, capabilities_uri: str) -> None:
    fptr.write(
        inspect.cleandoc(
            """
                Rules
                #####

                .. automodule:: omni.asset_validator
                    :noindex:
                    :platform: Windows-x86_64, Linux-x86_64
            """
        )
    )
    fptr.write(os.linesep)

    for item in DefaultCategoryRules:
        for rule in item.rules:
            requirements = RequirementsRegistry().get_requirements(rule)
            requirements_codes = [
                f"`{req.code} <{capabilities_uri}/{req.path}>`_" if req.path else f"{req.code}" for req in requirements
            ]
            codes_string = " ".join(requirements_codes)
            if codes_string:
                fptr.write(
                    inspect.cleandoc(
                        f"""
                            .. autoclass:: {rule.__name__}()

                            .. list-table::
                                :width: 100%

                                * - Requirements
                                * - {codes_string}
                        """
                    )
                )
            else:
                fptr.write(
                    inspect.cleandoc(
                        f"""
                            .. autoclass:: {rule.__name__}()
                        """
                    )
                )
            fptr.write(os.linesep)


def _generate_categories_documentation(fptr: TextIO) -> None:
    """
    Dumps this for documentation in reStructuredText.

    Args:
        fptr: A file-like object.
    """
    fptr.write(
        inspect.cleandoc(
            """
                Categories
                ##########

                .. automodule:: omni.asset_validator
                    :noindex:
                    :platform: Windows-x86_64, Linux-x86_64
            """
        )
    )
    fptr.write(os.linesep)
    for item in DefaultCategoryRules:
        fptr.write(
            inspect.cleandoc(
                f"""
                    {item.category}
                    {"*" * len(item.category)}
                """
            )
        )
        fptr.write(os.linesep)
        for rule in item.rules:
            fptr.write(
                inspect.cleandoc(
                    f"""
                        :py:class:`{rule.__name__}()`
                    """
                )
            )
            fptr.write(os.linesep)


def _generate_requirements_documentation(fptr: TextIO, capabilities_uri: str) -> None:
    """
    Dumps this for documentation in reStructuredText.

    Args:
        fptr: A file-like object.
    """
    fptr.write(
        inspect.cleandoc(
            """
                .. mdinclude:: howtorequirements.md

                Requirements
                ############

                .. automodule:: omni.asset_validator
                    :noindex:
                    :platform: Windows-x86_64, Linux-x86_64
            """
        )
    )
    fptr.write(os.linesep)
    for requirement in RequirementsRegistry().requirements:
        if rule := RequirementsRegistry().get_validator(requirement):
            link = f"`Link <{capabilities_uri}/{requirement.path}>`__" if requirement.path else ""
            fptr.write(
                inspect.cleandoc(
                    f"""
                        {requirement.code}
                        {"*" * len(requirement.code)}

                        .. list-table::
                           :width: 100%

                           * - Message
                             - Rule
                             - Link
                           * - {requirement.message}
                             - :py:class:`{rule.__name__}`
                             - {link}
                    """
                )
            )
            fptr.write(os.linesep)


def _generate_cli_documentation(fptr: TextIO) -> None:
    """
    Dumps this for documentation in reStructuredText.
    """
    fptr.write(
        inspect.cleandoc(
            """
                Command Line Interface
                ######################
            """
        )
    )
    fptr.write(os.linesep)

    parser = create_validation_parser()
    f = io.StringIO()
    with redirect_stdout(f):
        parser.print_help()
    stdout = f.getvalue()
    stdout = stdout.replace(" " * 24, " " * 24 + "| ")
    for category in DefaultCategoryRules:
        for rule in category.rules:
            stdout = stdout.replace(f" {rule.__name__}", f" :py:class:`{rule.__name__}`")
    for category in DefaultCategoryRules:
        stdout = stdout.replace(f" {category.category}", f" :py:class:`{category.category}`")
    for requirement in RequirementsRegistry().requirements:
        stdout = stdout.replace(f" {requirement.code}", f" :py:class:`{requirement.code}`")
    fptr.write(inspect.cleandoc(stdout))
    fptr.write(os.linesep)


class _ArgFormatter(RawTextHelpFormatter, ArgumentDefaultsHelpFormatter):
    pass


class _ArgParser(ArgumentParser):
    def error(self, message):
        self.print_help()
        args = {"prog": self.prog, "message": message}
        self.exit(2, gettext.gettext("%(prog)s: error: %(message)s\n") % args)


if __name__ == "__main__":
    parser = _ArgParser()
    parser.prog = "config"
    parser.formatter_class = _ArgFormatter
    parser.description = inspect.cleandoc(
        """
        Utilities for configuration.
        """
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--capabilities-uri",
        type=str,
        required=True,
    )
    args = parser.parse_args()
    output_dir: str = args.output_dir
    capabilities_uri: str = args.capabilities_uri
    with open(os.path.join(output_dir, "rules.rst"), "w") as fptr:
        _generate_rules_documentation(fptr, capabilities_uri)
    with open(os.path.join(output_dir, "categories.rst"), "w") as fptr:
        _generate_categories_documentation(fptr)
    with open(os.path.join(output_dir, "requirements.rst"), "w") as fptr:
        _generate_requirements_documentation(fptr, capabilities_uri)
    with open(os.path.join(output_dir, "cli.rst"), "w") as fptr:
        _generate_cli_documentation(fptr)
