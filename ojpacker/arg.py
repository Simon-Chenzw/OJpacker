from __future__ import absolute_import

import argparse
from typing import Optional, Sequence, Text

from . import config, demo, ui, workflow
from .ui import log


def get_parser() -> argparse.ArgumentParser:
    # main command
    parser = argparse.ArgumentParser(
        prog='ojpacker',
        usage=
        "ojpacker [-option]         packing data\n    or ojpacker [subcommand]      others",
        description=
        "a script can packer test data for Olympic informatics Online Judge",
        epilog=
        "For more detailed information and document, please see: https://github.com/Simon-Chenzw/OJpacker",
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
        action="version",
        version="use 'pip show ojpacker' or 'pip3 show ojpacker'",
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
        metavar="FILENAME",
        dest="name",
    )
    parser.add_argument(  # print detail
        "-show",
        nargs='?',  # can't use "-show input output"
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
        help="the file codename that to make input, or 'skip'.",
        metavar="NAME",
        dest="input_exec_type",
    )
    parser.add_argument(
        "-output",
        default="",
        type=str,
        help="the file codename that to make output, or 'skip'.",
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
        "-multiprocess",
        nargs='?',
        type=int,
        const=0,
        default=-1,
        help="Use multiprocess when executing programs",
        metavar="Max",
        dest="max_process",
    )

    # config
    config = sub.add_parser(
        "config",
        usage="ojpacker config [-option]",
        description="setting config",
        help="setting config",
    )
    config.set_defaults(func=config_call)
    config.add_argument(
        "-create",
        action="store_true",
        help="Use the configuration in the demo to create a configuration file",
        dest="create_demo_config")
    config.add_argument(
        "-copyto",
        choices=["user", "local"],
        help="copy config file between user/local",
        metavar="user/local",
        dest="config_copyto",
    )

    # demo
    demo = sub.add_parser(
        "demo",
        usage="ojpacker demo [-option]",
        description="make demo folder",
        help="make demo folder",
    )
    demo.set_defaults(func=demo_call)
    demo.add_argument("-dir",
                      nargs='?',
                      const=".",
                      default="ojpacker-demo",
                      help="Select the directory to generate the demo",
                      metavar="directory",
                      dest="demo_dir")

    return parser


def analyze(argv: Optional[Sequence[Text]]) -> None:
    parser = get_parser()
    ans = parser.parse_args(argv)
    ui.set_log_level(ans.log_level)
    ui.detail("argv:", argv)
    ans.func(ans)


# call workflow
@log
def run_call(args: argparse.Namespace) -> None:
    config.load_setting()
    config.zip_name = args.name or config.zip_name
    if args.input_exec_type:
        config.set_input_exec(args.input_exec_type)
    if args.output_exec_type:
        config.set_output_exec(args.output_exec_type)
    config.input_dir = args.input_dir
    config.show_input = "input" in args.show
    config.show_output = "output" in args.show
    config.will_zip = args.zip
    config.zip_list = args.zip_list
    config.max_process = args.max_process
    workflow.work()


# call config
@log
def config_call(args: argparse.Namespace) -> None:
    if args.create_demo_config:
        demo.make_config()
    if args.config_copyto is not None:
        config.copyto(args.config_copyto)


# call demo
@log
def demo_call(args: argparse.Namespace) -> None:
    demo.make_demo(args.demo_dir)
