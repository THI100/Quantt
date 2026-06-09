production: pyinstaller -w --clean --onedir --icon ./build/qi.ico --noupx --name QuanttEngine main.py
test: pyinstaller --console --clean --onedir --icon ./build/qi.ico --noupx --name QuanttEngine main.py
