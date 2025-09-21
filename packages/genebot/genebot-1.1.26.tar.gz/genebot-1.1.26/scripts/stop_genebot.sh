#!/bin/bash
# Emergency stop script for GeneBot processes
# This script forcefully stops all GeneBot-related processes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 GeneBot Emergency Stop Script${NC}"
echo -e "${BLUE}=================================${NC}"

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ ${1}${NC}"
}

print_error() {
    echo -e "${RED}❌ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  ${1}${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  ${1}${NC}"
}

# Check for running processes
print_info "Checking for GeneBot processes..."

# Find all GeneBot-related processes
PIDS=$(pgrep -f "trading_bot|market_aware_trading_bot|main\.py|genebot" 2>/dev/null || true)

if [ -z "$PIDS" ]; then
    print_info "No GeneBot processes found running"
    exit 0
fi

echo "Found running processes:"
for pid in $PIDS; do
    ps -p $pid -o pid,etime,command 2>/dev/null | tail -n +2 | while read line; do
        echo "  📊 $line"
    done
done

echo
read -p "Do you want to stop these processes? [y/N]: " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Operation cancelled"
    exit 0
fi

# Stop processes
stopped_count=0

for pid in $PIDS; do
    print_info "Stopping process $pid..."
    
    # Try graceful shutdown first
    if kill -TERM $pid 2>/dev/null; then
        print_info "Sent SIGTERM to $pid"
        
        # Wait up to 5 seconds for graceful shutdown
        for i in {1..5}; do
            if ! kill -0 $pid 2>/dev/null; then
                print_success "Process $pid terminated gracefully"
                stopped_count=$((stopped_count + 1))
                break
            fi
            sleep 1
        done
        
        # If still running, force kill
        if kill -0 $pid 2>/dev/null; then
            print_warning "Force killing process $pid..."
            if kill -KILL $pid 2>/dev/null; then
                print_success "Process $pid force killed"
                stopped_count=$((stopped_count + 1))
            else
                print_error "Failed to kill process $pid"
            fi
        fi
    else
        print_warning "Process $pid already terminated or permission denied"
    fi
done

# Clean up PID files
print_info "Cleaning up PID files..."
pid_files=("trading_bot.pid" "market_aware_bot.pid" "bot.pid" "main.pid" "genebot.pid")
removed_files=0

for pid_file in "${pid_files[@]}"; do
    if [ -f "$pid_file" ]; then
        rm -f "$pid_file"
        print_info "Removed $pid_file"
        removed_files=$((removed_files + 1))
    fi
done

if [ $removed_files -eq 0 ]; then
    print_info "No PID files found"
fi

# Final verification
print_info "Verifying shutdown..."
sleep 1

REMAINING_PIDS=$(pgrep -f "trading_bot|market_aware_trading_bot|main\.py|genebot" 2>/dev/null || true)

if [ -n "$REMAINING_PIDS" ]; then
    print_warning "Some processes are still running:"
    for pid in $REMAINING_PIDS; do
        ps -p $pid -o pid,etime,command 2>/dev/null | tail -n +2 | while read line; do
            echo "  📊 $line"
        done
    done
    echo
    print_warning "You may need to manually kill these processes:"
    print_warning "sudo kill -9 $REMAINING_PIDS"
else
    print_success "All GeneBot processes stopped successfully!"
fi

echo
print_success "Emergency stop completed!"
print_success "Stopped $stopped_count process(es)"

# Show how to restart
echo
print_info "To restart GeneBot:"
print_info "  python3 genebot.py start"
print_info "  python3 genebot.py monitor"