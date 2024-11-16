#!/bin/bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip3 install -r requirements.txt

# Build application
pyinstaller tvheadend_recorder.spec

# Create AppImage (optional)
# You'll need appimagetool installed
# wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
# chmod +x appimagetool-x86_64.AppImage

echo "Linux build complete! Check dist/ directory"
