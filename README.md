# icon-splash-generator-ios-android

A very simple python program to generate icon and splash for android and ios platforms.
Designed to cordova/ionic projects.

# Dependences:
ImageMagick

run this in your terminal to install:
brew install imagemagick

# How to use:
Put the "icon-splash-generator" folder in root of your ionic project.

you needs two images inside resources folder: 
icon.png --> 1024 × 1024px with no alpha
splash.pn --> 2732 × 2732px with no alpha

go to "icon-splash-generator" and run:
run.py

will be generate all icons and splahs inside resouces folder.

use "ionic cordova prepare ios" to updade your project.

