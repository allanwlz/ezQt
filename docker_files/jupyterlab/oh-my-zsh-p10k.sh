#!/bin/bash

set -e

if [[ "$OSTYPE" == "darwin"* ]]; then
    ostype="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    ostype="Linux"
else
    echo "Unsupported OS"
    exit 1
fi

check_and_install() {
    if ! command -v $1 &> /dev/null; then
        echo "$1 is not installed. Installing..."
        if [[ "$ostype" == "macOS" ]]; then
            echo "Please install $1 using Homebrew or Xcode Command Line Tools."
            exit 1
        elif [[ "$ostype" == "Linux" ]]; then
            if sudo -v; then
                sudo apt install $1 -y
            else
                echo "This script requires sudo permissions. Please ask the administrator to install the necessary packages."
                exit 1
            fi
        else
            echo "Unsupported OS"
            exit 1
        fi
    fi
}

check_and_install "git"
check_and_install "zsh"

# oh-my-zsh
OMZ_DIR=$HOME/.oh-my-zsh
if [ ! -d "$OMZ_DIR" ]; then
    git clone https://github.com/ohmyzsh/ohmyzsh.git "$OMZ_DIR"
else
    echo "oh-my-zsh already cloned, skipping"
fi
if [ ! -f "$HOME/.zshrc" ]; then
    cp "$OMZ_DIR/templates/zshrc.zsh-template" "$HOME/.zshrc"
fi

# download plugins of oh-my-zsh
ZSH_CUSTOM="$OMZ_DIR/custom"
check_and_clone_plugin() {
    local plugin_name=$1
    local plugin_dir="$ZSH_CUSTOM/plugins/$plugin_name"
    if [ ! -d "$plugin_dir" ]; then
        git clone "https://github.com/zsh-users/$plugin_name.git" "$plugin_dir"
    else
        echo "$plugin_name already cloned, skipping"
    fi
}

check_and_clone_plugin "zsh-syntax-highlighting"
check_and_clone_plugin "zsh-autosuggestions"
check_and_clone_plugin "zsh-completions"

# edit config and theme
## add compinit
if ! grep -q "autoload -U compinit && compinit" ~/.zshrc; then
    echo "autoload -U compinit && compinit" >> ~/.zshrc
fi

# use p10k theme
P10K_DIR="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k"
if [ ! -d "$P10K_DIR" ]; then
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$P10K_DIR"
else
    echo "powerlevel10k theme already cloned, skipping"
fi
echo P10K_DIR=${P10K_DIR} >> ~/.zshrc
echo 'source ${P10K_DIR}/powerlevel10k.zsh-theme' >> ~/.zshrc

# Add plugins
if [[ "$ostype" == "macOS" ]]; then
    printf '%s\n' '/^plugins=/c\' 'plugins=(git sudo z zsh-syntax-highlighting zsh-autosuggestions zsh-completions)' | sed -i '' -f - ~/.zshrc
    printf '%s\n' "/^# zstyle ':omz:update' mode disabled/c\\" "zstyle ':omz:update' mode disabled  # disable automatic updates" | sed -i '' -f - ~/.zshrc
    printf '%s\n' '/^ZSH_THEME=/c\' 'ZSH_THEME="powerlevel10k/powerlevel10k"' | sed -i '' -f - ~/.zshrc
    echo 'source ~/powerlevel10k/powerlevel10k.zsh-theme' >>~/.zshrc
else
    sed -i '/^plugins=/c\plugins=(git sudo z zsh-syntax-highlighting zsh-autosuggestions zsh-completions)' ~/.zshrc
    sed -i "/^# zstyle ':omz:update' mode disabled/c\zstyle ':omz:update' mode disabled  # disable automatic updates" ~/.zshrc
fi

# change default shell
if [ ! -f ~/.bash_profile ]; then
    touch ~/.bash_profile
    echo ".bash_profile created"
fi
changeshell="exec $(which zsh) -l"
if ! grep -q "$changeshell" ~/.bash_profile; then
    echo "$changeshell" >> ~/.bash_profile
fi

echo "Installation complete!"
