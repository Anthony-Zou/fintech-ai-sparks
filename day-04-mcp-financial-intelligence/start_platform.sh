#!/bin/bash

# MCP Financial Intelligence Platform Quick Start Script
# Launches the complete unified financial intelligence platform

echo "🚀 MCP Financial Intelligence Platform"
echo "==============================================="
echo "Starting the world's first MCP-powered financial intelligence platform..."
echo ""

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Docker detected - Starting with Docker Compose..."
    
    # Create necessary directories
    mkdir -p logs data monitoring/grafana/dashboards monitoring/grafana/datasources
    
    # Start the platform with Docker
    echo "📦 Building and starting all services..."
    docker-compose up -d --build
    
    # Wait for services to start
    echo "⏳ Waiting for services to initialize..."
    sleep 30
    
    # Health check
    echo "🏥 Checking service health..."
    
    # Check MCP server
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "✅ MCP Server: Running"
    else
        echo "❌ MCP Server: Not responding"
    fi
    
    # Check Streamlit dashboard
    if curl -f http://localhost:8501 &> /dev/null; then
        echo "✅ Streamlit Dashboard: Running"
    else
        echo "❌ Streamlit Dashboard: Not responding"
    fi
    
    echo ""
    echo "🌟 Platform Access URLs:"
    echo "   📊 Streamlit Dashboard: http://localhost:8501"
    echo "   🔧 MCP Server API: http://localhost:8000"
    echo "   📈 Prometheus: http://localhost:9090"
    echo "   📊 Grafana: http://localhost:3000 (admin/admin123)"
    echo ""
    echo "🎯 Next Steps:"
    echo "   1. Open Streamlit Dashboard: http://localhost:8501"
    echo "   2. Click 'Connect to MCP Server' in the sidebar"
    echo "   3. Start exploring unified financial intelligence!"
    echo ""
    echo "📚 Documentation: README.md"
    echo "🧪 Run Tests: python test_mcp_integration.py"
    echo "🎬 Run Demo: python demo_mcp_platform.py"
    
else
    echo "🐍 Docker not available - Starting with Python..."
    
    # Check Python dependencies
    if ! python -c "import streamlit, mcp" &> /dev/null; then
        echo "📦 Installing dependencies..."
        pip install -r requirements.txt
    fi
    
    # Start MCP server in background
    echo "🔧 Starting MCP Server..."
    python -m mcp_server.main &
    MCP_PID=$!
    
    # Wait for MCP server to start
    echo "⏳ Waiting for MCP server to initialize..."
    sleep 10
    
    # Start Streamlit dashboard
    echo "📊 Starting Streamlit Dashboard..."
    streamlit run client/streamlit_dashboard.py &
    STREAMLIT_PID=$!
    
    # Wait for services
    sleep 5
    
    echo ""
    echo "🌟 Platform Access URLs:"
    echo "   📊 Streamlit Dashboard: http://localhost:8501"
    echo "   🔧 MCP Server: Running in background (PID: $MCP_PID)"
    echo ""
    echo "🎯 Next Steps:"
    echo "   1. Open browser: http://localhost:8501"
    echo "   2. Click 'Connect to MCP Server' in the sidebar"
    echo "   3. Explore the unified financial intelligence platform!"
    echo ""
    echo "⏹️ To stop the platform:"
    echo "   kill $MCP_PID $STREAMLIT_PID"
    echo ""
    
    # Keep script running
    echo "Press Ctrl+C to stop the platform..."
    wait
fi
