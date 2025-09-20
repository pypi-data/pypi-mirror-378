#!/bin/bash

set -e

FUERO_DIR="$HOME/.fuero"
BIN_DIR="$HOME/.local/bin"
REPO_URL="https://github.com/ogcae/fuero"

echo "installing fuero programming language..."

# check python
if ! command -v python3 &> /dev/null; then
    echo "python3 is required but not installed"
    echo "please install python3 and try again"
    exit 1
fi

# check pip
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is required but not installed"
    echo "please install pip3 and try again"
    exit 1
fi

# create directories
mkdir -p "$BIN_DIR"
mkdir -p "$FUERO_DIR"

# download or clone fuero
if [ -d "$FUERO_DIR" ]; then
    echo "updating existing fuero installation..."
    cd "$FUERO_DIR"
    git pull origin main
else
    echo "downloading fuero..."
    git clone "$REPO_URL" "$FUERO_DIR"
    cd "$FUERO_DIR"
fi

# install dependencies
echo "installing dependencies..."
pip3 install --user -r requirements.txt

# install fuero package
echo "installing fuero package..."
pip3 install --user -e .

# create executable script
cat > "$BIN_DIR/fuero" << 'EOF'
#!/bin/bash
python3 -m fuero.cli "$@"
EOF

chmod +x "$BIN_DIR/fuero"

# add to path if not already there
SHELL_RC=""
if [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.profile"
fi

if [ -f "$SHELL_RC" ]; then
    if ! grep -q "$BIN_DIR" "$SHELL_RC"; then
        echo "adding fuero to PATH in $SHELL_RC..."
        echo "" >> "$SHELL_RC"
        echo "# fuero programming language" >> "$SHELL_RC"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
        echo "please run: source $SHELL_RC"
        echo "or restart your terminal"
    fi
fi

echo ""
echo "fuero installed!"
echo ""
echo "usage:"
echo "  fuero run script.fuero   # run a fuero file"
echo "  fuero repl               # interactive mode"
echo "  fuero --version          # show version"
echo "  fuero --help             # show help"
echo ""
echo "if 'fuero' command is not found, add ~/.local/bin to your PATH:"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "documentation: $FUERO_DIR/docs/"
echo "examples: $FUERO_DIR/examples/"