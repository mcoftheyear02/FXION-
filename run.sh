#!/bin/bash
# OMNITECH OMEGA v3.0 - Main Run Script

set -e

echo "=============================================="
echo "⚡ OMNITECH OMEGA v3.0"
echo "Autonomous AI Quantization Engine"
echo "=============================================="

# Configuration
export OMNITECH_BASE_MODEL="${OMNITECH_BASE_MODEL:-./models/mistral-7b.f16.gguf}"
export OMNITECH_QUANT_BIN="${OMNITECH_QUANT_BIN:-./llama.cpp/quantize}"
export OMNITECH_OUTPUT_DIR="${OMNITECH_OUTPUT_DIR:-./output}"
export W_TPS="${W_TPS:-0.6}"
export W_ACC="${W_ACC:-30.0}"
export W_SIZE="${W_SIZE:-0.01}"

# Create output directory
mkdir -p "$OMNITECH_OUTPUT_DIR"

# Check if llama.cpp exists, if not offer to clone it
if [ ! -d "./llama.cpp" ]; then
    echo ""
    echo "llama.cpp not found. Would you like to clone it? (y/n)"
    read -r answer
    if [ "$answer" = "y" ]; then
        git clone https://github.com/ggerganov/llama.cpp.git
        cd llama.cpp
        make
        cd ..
    fi
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install flask websockets redis prometheus_client 2>/dev/null || pip install --user flask websockets redis prometheus_client

# Start services
echo ""
echo "Starting OMNITECH OMEGA services..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $API_PID $WS_PID $WORKER_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start API server
echo "🌐 Starting API server on port 5000..."
python api/app.py &
API_PID=$!

# Start WebSocket server
echo "📡 Starting WebSocket server on port 8765..."
python api/stream_server.py &
WS_PID=$!

# Wait for API to start
sleep 2

# Run optimization loop if requested
if [ "$1" = "--run" ] || [ "$1" = "-r" ]; then
    ITERATIONS="${2:-10}"
    echo ""
    echo "🚀 Running RL optimization loop ($ITERATIONS iterations)..."
    python core/quantizer_rl.py --iterations "$ITERATIONS"
fi

echo ""
echo "=============================================="
echo "✅ Services started successfully!"
echo ""
echo "📊 Dashboard: http://localhost:5000"
echo "🔌 WebSocket: ws://localhost:8765"
echo "💚 Health:    http://localhost:5000/health"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=============================================="

# Keep running
wait
