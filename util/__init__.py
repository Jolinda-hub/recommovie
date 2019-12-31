import argparse
import configparser
import logging
import sys

DEFAULT_PATH = 'config.ini'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)


class Util:
    @staticmethod
    def parse_arguments():
        """
        Argument parser

        :return: arguments
        :rtype: dict
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--c',
            help='how many movies',
            type=int,
            required=False,
            default=100000
        )
        parser.add_argument(
            '--w',
            help='how many workers',
            type=int,
            required=False,
            default=8
        )
        parser.add_argument(
            '--u',
            help='is update?',
            action='store_true',
            required=False
        )

        args, _ = parser.parse_known_args()
        return args.__dict__

    @staticmethod
    def set_logger(name):
        """
        :param str name: logger name
        :return: logger
        :rtype: logger object
        """
        return logging.getLogger(name)

    @staticmethod
    def get_params():
        config = configparser.ConfigParser()
        conf_path = sys.argv[-1:][0]

        if not conf_path.endswith('ini'):
            conf_path = DEFAULT_PATH

        config.read(conf_path)
        return config
