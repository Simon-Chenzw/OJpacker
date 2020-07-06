from __future__ import absolute_import

import argparse
from ojpacker.config import input_exec
from . import config, workflow, filetype
"""
subcommand:
    run
    config
    demo
"""


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='ojpacker',
        usage="ojpacker [name] [-option]",
        description="data packer for Online Judge",
    )
    # main command
    # run
    parser.set_defaults(func=run_cmd)
    parser.add_argument(  # name of the zip
        "name",
        nargs='?',
        default="",
        help="name of the zip",
        # dest="zip_name",
    )
    parser.add_argument(  # print detail
        "-show",
        nargs='?',
        const=["input", "output"],
        default=[],
        choices=["input", "output"],
        help="print the detail of input or output files",
        dest="show",
    )
    parser.add_argument(
        "-dir",
        default="temp",
        type=str,
        help="the input file dir when you don't need make input",
        dest="input_dir",
    )
    parser.add_argument(
        "-input",
        default="",
        type=str,
        help="the language that make input",
        dest="input_exec_type",
    )
    parser.add_argument(
        "-output",
        default="",
        type=str,
        help="the language that make output",
        dest="output_exec_type",
    )
    parser.add_argument(
        "-unzip",
        action='store_false',
        help="don't compress the data",
        dest="zip",
    )
    parser.add_argument(
        "-addzip",
        nargs='?',
        default=[],
        help="add file into the zip",
        metavar="FILE",
        dest="zip_list",
    )
    parser.add_argument(
        "-multi",
        action='store_true',
        help="multi thread",
        dest="multi_thread",
    )
    parser.add_argument(
        "-log",
        default="info",
        type=str,
        help="the log level",
        dest="log_level",
    )
    parser.add_argument(
        "-vesion",
        action='version',
        version='%(prog)s v0.1.0',
    )

    # # sub command
    # sub = parser.add_subparsers(dest="subcmd")
    # # config
    # config = sub.add_parser("config", help="config")
    # config.set_defaults(func=config_cmd)

    return parser


def analyze() -> None:
    parser = get_parser()
    ans = parser.parse_args()
    ans.func(ans)


from . import ui


# call workflow
def run_cmd(args: argparse.Namespace) -> None:
    ui.debug(args)
    ui.set_log_level(args.log_level)
    config.load_setting()
    workflow.work(
        zip_name=args.name or config.defalut_zip_name,
        state_name=config.state_name,
        input_data_name=config.input_data_name,
        output_data_name=config.output_data_name,
        input_exec=config.get_input_exec(args.input_exec_type
                                         or config.input_default_exec),
        output_exec=config.get_output_exec(args.output_exec_type
                                           or config.output_default_exec),
        input_dir=args.input_dir,
        show_input="input" in args.show,
        show_output="output" in args.show,
        zip=args.zip,
        zip_list=args.zip_list,
        multi_thread=args.multi_thread,
    )


# call config
def config_cmd(args: argparse.Namespace) -> None:
    pass
