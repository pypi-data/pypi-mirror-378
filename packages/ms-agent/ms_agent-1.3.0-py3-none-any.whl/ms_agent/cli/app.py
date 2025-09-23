# Copyright (c) Alibaba, Inc. and its affiliates.
import argparse

from modelscope.cli.base import CLICommand


def subparser_func(args):
    """ Function which will be called for a specific sub parser.
    """
    return AppCMD(args)


class AppCMD(CLICommand):
    name = 'app'

    def __init__(self, args):
        self.args = args

    @staticmethod
    def define_args(parsers: argparse.ArgumentParser):
        """
        Define args for the app command.
        """
        parser: argparse.ArgumentParser = parsers.add_parser(AppCMD.name)
        group = parser.add_mutually_exclusive_group(required=True)

        group.add_argument(
            '--doc_research',
            action='store_true',
            help='Launch the `Doc Research` app.')

        parser.add_argument(
            '--server_name',
            type=str,
            default='0.0.0.0',
            help='The gradio server name to bind to.')

        parser.add_argument(
            '--server_port',
            type=int,
            default=7860,
            help='The gradio server port to bind to.')

        parser.add_argument(
            '--share',
            action='store_true',
            help='Whether to share the gradio app publicly.')

        parser.set_defaults(func=subparser_func)

    def execute(self):

        if self.args.doc_research:
            from ms_agent.app.doc_research import launch_server as launch_doc_research
            launch_doc_research(
                server_name=self.args.server_name,
                server_port=self.args.server_port,
                share=self.args.share)
        else:
            raise ValueError('Unsupported app type.')
