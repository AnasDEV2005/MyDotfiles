#!/bin/bash

PACKAGES=(
    "git"
    "neovim"
    "htop"
    "python-fabric-git"
    "yazi"
    "zellij"
    "haruna"
    "flameshot-git"
    "zen-browser"
    "obs-studio"
    "krita"
    "obsidian"
    "tahoma2d"
    "libreoffice-fresh"
    "neofetch"
    "auto-cpufreq"
    "virtualbox"
    "wine-staging-git"
    "wine-valve"
    "winegui-bin"
    "wine" # dunno abt this
    "winetricks"
    "lsd"
    "pacseek"
    "gtk3"
    "cairo"
    "gtk-layer-shell"
    "libgirepository"
    "gobject-introspection"
    "gobject-introspection-runtime"
    "python"
    "python-pip"
    "python-gobject"
    "python-cairo"
    "python-loguru"
    "pkgconf"
    "megacubo-bin"
    "megasync"
    "cava"
    "heroic-games-launcher-bin"
    "acpi"
    # Add more packages here
)


# TODO : add installing the lock gtk lib 
# and uuuh... some other install scripts


command_exists() {
    command -v "$1" >/dev/null 2>&1
}

install_yay() {
    echo "Installing 'yay' (AUR helper)..."
    sudo pacman -S --needed --noconfirm base-devel git
    git clone https://aur.archlinux.org/yay.git
    cd yay || exit
    makepkg -si --noconfirm
    cd ..
    rm -rf yay
}

main() {
    if ! command_exists yay; then
        echo "'yay' is not installed. Installing..."
        install_yay
    else
        echo "'yay' is already installed."
    fi

    echo "Updating system packages..."
    yay -Syu --noconfirm

    echo "Installing packages..."
    for pkg in "${PACKAGES[@]}"; do
        if yay -Qi "$pkg" >/dev/null 2>&1; then
            echo "Package '$pkg' is already installed."
        else
            echo "Installing '$pkg'..."
            yay -S --noconfirm "$pkg"
        fi
    done

    echo "All done!"
}

main
