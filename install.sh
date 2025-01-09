#!/bin/bash



echo "This install script is only made for Arch Linux, possibly also Arch-based distros"


sudo pacman -Syuu

if ! command -v hyprctl &> /dev/null; then
    echo "Hyprland is not installed. Installing Hyprland..."
    yay -S hyprland
else
    echo "Hyprland is already installed."
fi

echo "Starting install..."
echo "Proceeding to install packages and dependencies"
chmod +x ./arch-installations.sh
./arch-installations.sh

echo "Installing Gtk-session-lock"
echo "Installing dependencies"
yay -S meson
yay -S python-pywayland
yay -S vala


cd ~
git clone https://github.com/Cu3PO42/gtk-session-lock.git

cd gtk-session-lock
meson setup build
ninja -C build
sudo ninja -C build install
sudo ldconfig



cd ~

echo "Attempting to install libcvc"

git clone https://github.com/Fabric-Development/fabric.git
chmod +x ~/scripts/install_libcvc/install_libcvc.sh
~/scripts/install_libcvc/install_libcvc.sh


cd ~
git clone https://github.com/AnasDEV2005/my-scripts.git
cd my-scripts
sudo cp ./gitscript usr/local/bin
sudo cp ./stopwatch usr/local/bin

cd ~ 
touch fabric-notes.txt 


echo "installing dotfiles"

cd ~
git clone https://github.com/zsh-users/zsh-autosuggestions

sudo mv ~/.config/LobOS/hypr/.zshrc ~/.zshrc

sudo cp ~/.config/LobOS/hypr ~/.config

sudo cp ~/.config/LobOS/alacritty ~/.config

sudo cp ~/.config/LobOS/nvim ~/.config

sudo cp ~/.config/LobOS/neofetch ~/.config 

sudo cp ~/.config/LobOS/vesktop ~/.config

echo "Verifying python packages"

cd ~/.config/hypr 
source ./fabric-venv/bin/activate
pip install loguru
pip install psutil
pip install subprocess
pip install pam










