#!/usr/bin/env bash

# Define system packages required for the project
pkgs=(build-essential python3 python3-dev python3-pip python3-venv)

# Add sudo to elevated commands when not running as root already
CMD_PREFIX=
if [ ! "$EUID" -eq 0 ]; then
  CMD_PREFIX=sudo
fi

# Install missing system packages
$CMD_PREFIX apt update
$CMD_PREFIX apt-get -y --ignore-missing install "${pkgs[@]}"

username=$(whoami)
groupname=$(id -gn)
root_path=$(pwd)
config_path=${1:-/etc/self-operating-computer/self-operating-computer.env}
source_path=${2:-$root_path/deploy/config/defaults.env}

rm -fr venv
python3 -m venv venv
source venv/bin/activate

pip install -e .

sudo rm -fr "$config_path"
sudo mkdir -p "$(dirname "$config_path")"
sudo cp "$source_path" "$config_path"
sudo chown -R "$username:$groupname" "$(dirname "$config_path")"

export SOC_ENV_FILE=$config_path
