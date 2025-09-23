from argparse import ArgumentParser
import sys

from pytestifyx import __description__, __version__
from pytestifyx.utils.parse.fiddler import trans_saz_to_test
from pytestifyx.utils.parse.scaffold import main_scaffold
from pytestifyx.utils.parse.config import generate_default_config
from pytestifyx.utils.parse.openapi import trans_openapi_to_test


def main():
    # 命令行处理程序入口
    arg_parser = ArgumentParser(description=__description__)
    arg_parser.add_argument("-V", "--version", dest="version", action="store_true", help="show version")
    arg_parser.add_argument("-P", "--project", dest="project", action="store_true", help="Create an pytestifyx test project")
    arg_parser.add_argument("-T", "--parse", dest="parse", action="store_true", help="fiddler saz file parse to pytestifyx test case")
    arg_parser.add_argument("-O", "--openapi", dest="openapi", action="store_true", help="OpenAPI/Swagger file parse to pytestifyx test case")
    arg_parser.add_argument("-C", "--config", dest="config", action="store_true", help="Generate default config.yaml template")

    if sys.argv[1] in ["-V", "--version"]:
        print(f"{__version__}")
    elif sys.argv[1] in ["-h", "--help"]:
        arg_parser.print_help()
    elif sys.argv[1] in ["-P", "--project"]:
        arg_parser.print_help()
        main_scaffold()
    elif sys.argv[1] in ["-T", "--parse"]:
        arg_parser.print_help()
        trans_saz_to_test()
    elif sys.argv[1] in ["-O", "--openapi"]:
        arg_parser.print_help()
        trans_openapi_to_test()
    elif sys.argv[1] in ["-C", "--config"]:
        result = generate_default_config()
        print(result)
    else:
        print(f"Unknown command: {sys.argv[1]}")
        arg_parser.print_help()
        sys.exit(0)
