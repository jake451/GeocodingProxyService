# Entry point for app
from . import geocodex
import configparser
import os
import sys


def main(args=None):
    if len (sys.argv) < 2:
        print('Config file parameter needed to access services.  See example config.ini.')
        return
    config_file = sys.argv[1]
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        geocodex.run(config=config)

if __name__ == "__main__":
    main()
