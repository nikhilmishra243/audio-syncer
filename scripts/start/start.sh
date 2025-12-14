#!/bin/bash
# Auto-setup script for Audio Streaming Control Panel
# Handles venv creation, activation, and dependency installation automatically

set -e  # Exit on error

echo "=================================================="
echo "   Audio Streaming Control Panel - Auto Setup"
echo "=================================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed!${NC}"
    echo "Please install Python 3 and try again."
    exit 1
fi

echo -e "${GREEN}✅ Python 3 found${NC}"
echo ""

# Step 1: Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
    echo ""
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
    echo ""
fi

# Step 2: Activate virtual environment
echo -e "${YELLOW}🔌 Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Step 3: Check and install dependencies
echo -e "${YELLOW}📚 Checking dependencies...${NC}"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt not found!${NC}"
    echo "Creating requirements.txt with necessary packages..."
    cat > requirements.txt << EOF
sounddevice>=0.4.6
Flask>=2.3.0
websockets>=11.0
numpy>=1.24.0
psutil>=5.9.0
EOF
    echo -e "${GREEN}✅ requirements.txt created${NC}"
fi

# Check if packages are installed by trying to import them
NEEDS_INSTALL=false

python3 -c "import flask" 2>/dev/null || NEEDS_INSTALL=true
python3 -c "import sounddevice" 2>/dev/null || NEEDS_INSTALL=true
python3 -c "import websockets" 2>/dev/null || NEEDS_INSTALL=true
python3 -c "import psutil" 2>/dev/null || NEEDS_INSTALL=true

if [ "$NEEDS_INSTALL" = true ]; then
    echo -e "${YELLOW}📥 Installing dependencies...${NC}"
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ All dependencies already installed${NC}"
fi

echo ""
echo "=================================================="
echo "   🚀 Starting Control Panel..."
echo "=================================================="
echo ""

# Step 4: Run launcher.py
python3 src/launcher.py

# Deactivate venv when launcher exits
deactivate