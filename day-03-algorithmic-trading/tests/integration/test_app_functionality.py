#!/usr/bin/env python3
"""
Test script to verify the Streamlit application functionality.
"""

import requests
import time


def test_app_is_running():
    """Test that the Streamlit app is running and responsive."""
    try:
        response = requests.get('http://localhost:8501', timeout=5)
        print(f"✅ App is running - Status Code: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ App is not accessible: {e}")
        return False


def test_app_health():
    """Test the health endpoint of the Streamlit app."""
    try:
        response = requests.get(
            'http://localhost:8501/_stcore/health', timeout=5)
        print(f"✅ Health endpoint - Status Code: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Health endpoint not available: {e}")
        return False


if __name__ == '__main__':
    print('🚀 Testing Streamlit Application...')

    # Test basic connectivity
    app_running = test_app_is_running()
    health_ok = test_app_health()

    if app_running:
        print('🎉 Application is successfully running!')
        print('🌐 You can access it at: http://localhost:8501')
        print('\n📋 Available Features:')
        print('   - Live Trading Dashboard')
        print('   - Order Management')
        print('   - Position Monitoring')
        print('   - Market Data Visualization')
        print('   - Strategy Performance Analytics')
    else:
        print('❌ Application is not running properly')

    print(f'\n📊 Test Results:')
    print(f'   - App Running: {"✅" if app_running else "❌"}')
    print(f'   - Health Check: {"✅" if health_ok else "⚠️"}')
