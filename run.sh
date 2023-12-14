#!/bin/bash
#
#           SOC Installer Script v0.0.1
#   GitHub: https://github.com/OthersideAI/self-operating-computer
#   Issues: https://github.com/OthersideAI/self-operating-computer/issues
#   Requires: bash, curl/wget, python3, pip, git
#
#   Please open an issue if you notice any bugs.
#
#
#   This script is create by centopw
#
#
clear
echo -e "\e[0m\c"
LOG_FILE="install_log.txt"
# shellcheck disable=SC2016
echo '

 $$$$$$\   $$$$$$\   $$$$$$\  
$$  __$$\ $$  __$$\ $$  __$$\ 
$$ /  \__|$$ /  $$ |$$ /  \__|
\$$$$$$\  $$ |  $$ |$$ |      
 \____$$\ $$ |  $$ |$$ |      
$$\   $$ |$$ |  $$ |$$ |  $$\ 
\$$$$$$  | $$$$$$  |\$$$$$$  |
 \______/  \______/  \______/ 
    
    Self-Operating-Computer
--- Created by OthersideAI ---
    
'


# Function to log errors
log_error() {
    echo "Error at $(date): $1" >> "$LOG_FILE"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to install packages based on the operating system
install_packages() {
    if [ "$os" == "Linux" ]; then
        # Use the appropriate package manager for Linux
        if command_exists apt-get; then
            sudo apt-get install -y "$1" || { log_error "Unable to install $1."; exit 1; }
        elif command_exists yum; then
            sudo yum install -y "$1" || { log_error "Unable to install $1."; exit 1; }
        else
            log_error "Unsupported package manager. Please install $1 manually."
            exit 1
        fi
    elif [ "$os" == "Darwin" ]; then
        # Use Homebrew for macOS
        if command_exists brew; then
            brew install "$1" || { log_error "Unable to install $1."; exit 1; }
        else
            log_error "Homebrew not found. Please install Homebrew and then $1 manually."
            exit 1
        fi
    elif [ "$os" == "MINGW64_NT-10.0" ]; then
        # Use Chocolatey for Windows
        if command_exists choco; then
            choco install "$1" -y || { log_error "Unable to install $1."; exit 1; }
        else
            log_error "Chocolatey not found. Please install Chocolatey and then $1 manually."
            exit 1
        fi
    else
        log_error "Unsupported operating system. Please install $1 manually."
        exit 1
    fi
}

# Function to run a script and log errors
run_script() {
    eval "$1" || { log_error "Error running $1."; exit 1; }
}

# Check the operating system
os=$(uname -s)

# Check if Python is installed
if ! command_exists python3; then
    echo "Python not found. Installing Python..."
    install_packages python3
fi

# Check if pip is installed
if ! command_exists pip; then
    echo "pip not found. Installing pip..."
    install_packages python3-pip
fi

# Check if git is installed
if ! command_exists git; then
    echo "Git not found. Installing Git..."
    install_packages git
fi 

# Create a Python virtual environment
run_script "python3 -m venv venv"

# Activate the virtual environment
source venv/bin/activate || { log_error "Unable to activate the virtual environment."; exit 1; }

# Install project requirements
run_script "pip install -r requirements.txt"

# Install Project and Command-Line Interface
run_script "pip install ."

# Check if the .env file exists and the OPENAI_API_KEY is set in it
if [ -f .env ] && grep -q "OPENAI_API_KEY" .env; then
    echo "OpenAI API key found in .env file. Skipping prompt..."
else
    # Prompt user for Open AI key
    read -p "Enter your OpenAI API key: " openai_key

    # Set the API key as an environment variable
    export OPENAI_API_KEY="$openai_key"

    # Create a new .env file
    touch .env

    # Write the API key to the .env file
    echo "OPENAI_API_KEY='$openai_key'" > .env
fi

# Notify the user about the last step
echo "Final Step: As a last step, the Terminal app will ask for permission for 'Screen Recording' and 'Accessibility' in the 'Security & Privacy' page of Mac's 'System Preferences.'"

echo "Operating system: $os"

if [ "$os" == "Darwin" ]; then
    echo "Attempting to open Security & Privacy settings..."
    open /System/Library/PreferencePanes/Security.prefPane
    read -p "Have you granted the necessary permissions in the Security & Privacy settings? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "Please grant the necessary permissions and then rerun the script."
        exit 1
    fi
else
    echo "Not a macOS system, skipping..."
fi

# End of the script
echo "Installation complete. Enjoy using the Self-Operating Computer Framework!"

# Run the framework
run_script "operate"
