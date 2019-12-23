import argparse
import configparser
import logging
import sys

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
        config.read(conf_path)

        return config
