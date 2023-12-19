import argparse
import ui
from base import *

parser = argparse.ArgumentParser(description='Plex Debrid')

parser.add_argument('--config-dir', '-c', type=str, default='.', help='Configuration directory')
parser.add_argument('--service', '-s', default=True, action='store_true', help='Run in service mode')

args = parser.parse_args()

settings_path = f"{args.config_dir}/settings.json"

if __name__ == "__main__":
    ui.run(args.config_dir, args.service)
