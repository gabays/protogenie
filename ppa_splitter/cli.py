from argparse import ArgumentParser
import os
import sys
import shutil

from .defaults import DEFAULT_SENTENCE_MARKERS
from .configs import Configuration
from .dispatch import run
from .cli_utils import check_files, check_ratio


def generate_cli():
    cli = ArgumentParser(
        description="""This tool helps you to split PPA-formated output to training, testing and dev set
This tool expects your data to not have header."""
    )
    cli.add_argument("path", nargs="+", help="A unix wildcard or single file path, eg. 'pandora.tsv' or 'data/*.csv'")
    cli.add_argument("--output", default="empty.yaml", help="The Configuration file to write in")
    cli.add_argument("--input", default=None, help="An input file that has already some configurations in it")

    arguments = cli.parse_args()

    Configuration.generate_blank(
        target_files=arguments.path,
        yaml_file=arguments.output,
        input_file=arguments.input
    )


def dispatch_cli():
    cli = ArgumentParser(
        description="""This tool helps you to split PPA-formated output to training, testing and dev set
    This tool expects your data to not have header."""
    )
    cli.add_argument("path", nargs="+", help="A unix wildcard or single file path, eg. 'pandora.tsv' or 'data/*.csv'")
    cli.add_argument("--train", default=0.8, type=float, help="Ratio of data to use for training")
    cli.add_argument("--test", default=0.2, type=float, help="Ratio of data to use for testing")
    cli.add_argument("--dev", default=0, type=float, help="Ratio of data to use for dev")
    cli.add_argument("--col", dest="col_marker",
                     default="\t", help="Character that separates columns in your files (Default is TAB)")
    cli.add_argument("--output", default="./output", help="Directory in which to save files")
    cli.add_argument("--sentence", dest="sentence_marker", default=DEFAULT_SENTENCE_MARKERS,
                     help="Directory in which to save files")
    cli.add_argument("--config", dest="config", default={}, help="Yaml configuration file for advanced config")
    cli.add_argument("--clear", dest="clear", default=False, action="store_true",
                     help="Remove data in output directory (you'll need to confirm)")

    # Issue when

    arguments = cli.parse_args()

    train, test, dev = check_ratio(arguments.train, arguments.test, arguments.dev)

    try:
        files = check_files(arguments.path)
    except ValueError:
        print("There is no such files")
        sys.exit(0)

    if arguments.clear:
        confirm = ""
        confirm_message = "Are you sure you want to remove data in {} ? [y/n]\t>\t".format(arguments.output)

        while confirm not in ["y", "n"]:
            confirm = input(confirm_message).lower()
            confirm_message = "Are you sure you want to remove data in {} ? [y/n] (your previous answer was wrong)" \
                              "\t>\t".format(arguments.output)

        if confirm == "y":
            print("\tRemoving data in {}".format(arguments.output))
            shutil.rmtree(arguments.output, ignore_errors=True)
        else:
            print("\tData were not removed")

    os.makedirs(arguments.output, exist_ok=True)
    for subset in ["dev", "test", "train"]:
        os.makedirs(os.path.join(arguments.output, subset), exist_ok=True)

    print("=============")
    print("Processing...")
    # I run over each files
    for file, ratios in run(
            files,
            output_folder=arguments.output, verbose=True,
            col_marker=arguments.col_marker, sentence_splitter=arguments.sentence_marker,
            dev_ratio=dev, test_ratio=test, config=arguments.config):

        print("{} has been transformed".format(file))
        for key, value in ratios.items():
            if value:
                print("\t{} tokens in {} dataset".format(value, key))
