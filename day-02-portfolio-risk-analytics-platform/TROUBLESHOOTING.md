# Portfolio Risk Analytics Platform - Troubleshooting

## Common Issues and Solutions

### "Expected 'Adj Close' column not found in data" Error

If you encounter this error:

1. **Cause**: Yahoo Finance API sometimes changes its response structure or doesn't return 'Adj Close' data for certain tickers.

2. **Solution**: The app now has robust error handling that will:

   - Try to use 'Close' prices if 'Adj Close' is not available
   - Handle both single and multiple ticker data structures
   - Show appropriate warnings when falling back to alternative data

3. **Docker-specific issues**:
   - Make sure the app_fixed.py is being used (check Dockerfile)
   - Ensure all dependencies are installed properly

### Testing with Docker

To test the application with Docker:

```bash
# Make the test script executable
chmod +x docker-test.sh

# Run the script
./docker-test.sh
```

Then access the application at http://localhost:8501.

### Manual Fixes

If you're still encountering issues:

1. Try running in demo mode first to ensure the application works correctly
2. Check if the tickers you entered are valid and available on Yahoo Finance
3. Try with a smaller set of well-known tickers (like SPY, AAPL) first
4. Use a longer data period (1-5 years) to ensure enough historical data
