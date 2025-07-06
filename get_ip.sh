#!/bin/bash

# Quick IP Address Discovery for Mobile Testing
echo "📱 Mobile Access Setup"
echo "====================="

# Get local IP address
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')

if [ -z "$LOCAL_IP" ]; then
    echo "❌ Could not automatically determine local IP address"
    echo ""
    echo "🔍 Manual IP discovery:"
    echo "   Run: ifconfig | grep inet"
    echo "   Look for an address like 192.168.x.x or 10.x.x.x"
else
    echo "✅ Your local IP address: $LOCAL_IP"
    echo ""
    echo "📱 Mobile URLs:"
    echo "   Frontend: http://$LOCAL_IP:3000"
    echo "   API:      http://$LOCAL_IP:8000"
    echo ""
    echo "📋 Mobile Testing Steps:"
    echo "   1. Connect your phone to the same WiFi network"
    echo "   2. Open http://$LOCAL_IP:3000 in your mobile browser"
    echo "   3. Look for green 'API Connected' indicator"
    echo "   4. Test camera upload by tapping the upload area"
fi

echo ""
echo "🖥️  Desktop URLs:"
echo "   Frontend: http://localhost:3000"
echo "   API:      http://localhost:8000"
echo "   Docs:     http://localhost:8000/docs"