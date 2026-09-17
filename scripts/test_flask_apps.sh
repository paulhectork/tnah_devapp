#!/usr/bin/env bash

set -e

# colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# configuration
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR="$SCRIPT_DIR/.."
VENV_DIR="$ROOT_DIR/.venv"
APPS_DIR="$ROOT_DIR/apps"
REQUIREMENTS_FILE="$ROOT_DIR/requirements.txt"

# number of seconds each app is tested
TIMEOUT_SECONDS=5
# state: does a venv exist before running the script ? (if so, drop it, create a clean one for the script, recreate a clean one at the end)
VENV_EXISTS="false"

# Track results
declare -a FAILED_APPS=()
declare -a PASSED_APPS=()

echo "******************************************"
echo "flask apps testing"
echo "******************************************"
echo ""

# Step 1: Create virtual environment
echo -e "${YELLOW}[1/4] setting up virtual environment...${NC}"
if [ -d "$VENV_DIR" ]; then
    echo "$VENV_DIR exists. removing and recreating from scratch"
    rm -r "$VENV_DIR"
    VENV_EXISTS="true"
fi
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "created $VENV_DIR"
fi

# activate venv
source "$VENV_DIR/bin/activate"
echo "activated $VENV_DIR"
echo ""

# step 2: Install requirements
echo -e "${YELLOW}[2/4] installing requirements...${NC}"
if [ -f "$REQUIREMENTS_FILE" ]; then
    pip install --quiet -r "$REQUIREMENTS_FILE"
    echo "requirements installed"
else
    echo -e "${RED}error: $REQUIREMENTS_FILE not found. exiting..."
    exit 1
fi
echo ""

# step 3: Find all app start files
echo -e "${YELLOW}[3/4] finding Flask apps...${NC}"
APP_FILES=($(find "$APPS_DIR" -name "main.py" -path "*/s*/main.py" 2>/dev/null || true))

if [ ${#APP_FILES[@]} -eq 0 ]; then
    echo -e "${RED}no app files found matching ./apps/s*/main.py${NC}"
    exit 1
fi

echo "found ${#APP_FILES[@]} app(s):"
for app in "${APP_FILES[@]}"; do
    echo "  - $app"
done
echo ""

# step 4: test each app
echo -e "${YELLOW}[4/4] testing apps...${NC}"
echo ""

for app_file in "${APP_FILES[@]}"; do
    app_dir=$(dirname "$app_file")
    app_name=$(basename "$app_dir")
    
    echo -n "testing $app_name... "
    
    # run the app with timeout and capture output
    app_output=$(mktemp)
    app_error=$(mktemp)
    
    # start the app in the background with timeout
    timeout "$TIMEOUT_SECONDS" python "$app_file" > "$app_output" 2> "$app_error" &
    app_pid=$!
    
    # wait for the app to finish or timeout
    wait $app_pid 2>/dev/null || exit_code=$?
    
    # read the error output
    error_content=$(cat "$app_error")
    output_content=$(cat "$app_output")
    
    # check for actual errors (ignore timeout exit code 124 as that means app ran successfully)
    # flask apps run indefinitely, so a timeout is expected
    if [ "$exit_code" = "124" ] || [ -z "$error_content" ] || [[ "$error_content" =~ "Traceback" && ! "$error_content" =~ "KeyboardInterrupt" ]]; then
        # if it's a timeout, all good (app was running)
        if [ "$exit_code" = "124" ]; then
            echo -e "${GREEN}✓ passed${NC}"
            PASSED_APPS+=("$app_name")
        # if there's a real traceback error, it failed
        elif [[ "$error_content" =~ "Traceback" ]] && [[ ! "$error_content" =~ "KeyboardInterrupt" ]]; then
            echo -e "${RED}✗ failed${NC}"
            FAILED_APPS+=("$app_name")
            echo "  Error: $error_content" | head -n 5
        else
            echo -e "${GREEN}✓ passed${NC}"
            PASSED_APPS+=("$app_name")
        fi
    else
        echo -e "${GREEN}✓ passed${NC}"
        PASSED_APPS+=("$app_name")
    fi
    
    # cleanup
    rm -f "$app_output" "$app_error"
done

echo ""
echo "******************************************"
echo "test results"
echo "******************************************"
echo -e "${GREEN}passed: ${#PASSED_APPS[@]}${NC}"
for app in "${PASSED_APPS[@]}"; do
    echo "  ✓ $app"
done

if [ ${#FAILED_APPS[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}failed: ${#FAILED_APPS[@]}${NC}"
    for app in "${FAILED_APPS[@]}"; do
        echo "  ✗ $app"
    done
    echo ""
    ERROR_STATUS=1
else
    echo ""
    echo -e "${GREEN}all tests passed!${NC}"
    ERROR_STATUS=0
fi

# delete the .venv created by the script. if a .venv existed, recreate it 
deactivate
rm -r "$VENV_DIR"
if [ "$VENV_EXISTS" = "true" ]; then
    echo -e "${GREEN}creating a clean .venv at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate" 
    pip install --quiet -r "$REQUIREMENTS_FILE"
fi

exit "$ERROR_STATUS"
