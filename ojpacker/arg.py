from __future__ import absolute_import

import argparse
import os
from typing import Optional, Sequence, Text

from . import config, demo, ui, workflow


def get_parser() -> argparse.ArgumentParser:
    # main command
    parser = argparse.ArgumentParser(
        prog='ojpacker',
        usage=
        "ojpacker [-option]         packing data\n    or ojpacker [subcommand]      others",
        description=
        "a script can packer test data for Olympic informatics Online Judge",
        epilog=
        "Tips: if the executable file name does not exist in json, the program will skip that stage",
    )

    parser.add_argument(
        "-log",
        default="info",
        type=str,
        help="set log level, default is info",
        metavar="LEVEL",
        dest="log_level",
    )
    parser.add_argument(
        "-vesion",
        action='version',
        version='%(prog)s v0.1.0',
    )

    # sub command
    sub = parser.add_subparsers(
        title="subcommand",
        dest="subcmd",
        metavar="",
    )

    # run
    parser.set_defaults(func=run_call)
    parser.add_argument(  # name of the zip
        "-name",
        default="",
        help="name of the zip, without suffix",
        metavar="FILE",
        dest="name",
    )
    parser.add_argument(  # print detail
        "-show",
        nargs='?',
        const=["input", "output"],
        default=[],
        choices=["input", "output"],
        help="print the detail of input or output files",
        metavar="input or output",
        dest="show",
    )
    parser.add_argument(
        "-dir",
        default="temp",
        type=str,
        help="the input directory when you skip making input",
        metavar="directory",
        dest="input_dir",
    )
    parser.add_argument(
        "-input",
        default="",
        type=str,
        help="the file that make input, setting in json.",
        metavar="NAME",
        dest="input_exec_type",
    )
    parser.add_argument(
        "-output",
        default="",
        type=str,
        help="the file that make output, setting in json.",
        metavar="NAME",
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
        nargs='+',
        default=[],
        help="add files to zip before compression",
        metavar="FILE",
        dest="zip_list",
    )
    parser.add_argument(
        "-multithreading",
        action='store_true',
        help="Use multithreading when executing programs",
        dest="multi_thread",
    )

    # config
    config = sub.add_parser(
        "config",
        usage="ojpacker config",
        description="setting config",
        help="setting config",
    )
    config.set_defaults(func=config_call)

    # demo
    demo = sub.add_parser(
        "demo",
        usage="ojpacker demo",
        description="make demo folder",
        help="make demo folder",
    )
    demo.set_defaults(func=demo_call)

    return parser


def analyze(argv: Optional[Sequence[Text]]) -> None:
    parser = get_parser()
    ans = parser.parse_args(argv)
    ui.set_log_level(ans.log_level)
    ui.debug(argv)
    ui.debug(ans)
    ans.func(ans)


# call workflow
def run_call(args: argparse.Namespace) -> None:
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
def config_call(args: argparse.Namespace) -> None:
    config.make_config()


# call demo
def demo_call(args: argparse.Namespace) -> None:
    ui.info(f"make 'ojpacker-demo' at {os.getcwd()}")
    demo.make_demo()
    ui.info("run 'cd ojpacker-demo && ojpacker' have a try")
