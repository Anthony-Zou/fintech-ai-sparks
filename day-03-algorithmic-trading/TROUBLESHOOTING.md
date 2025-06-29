# Troubleshooting Guide

This document provides solutions to common issues you might encounter when setting up and running the Algorithmic Trading Platform.

## Common Error Messages

### Error: "cannot convert float NaN to integer"

**Description**: This error occurs in the market data processing when trying to convert NaN values to integers.

**Solution**: This issue has been fixed in the current version. The fix handles NaN values before attempting conversion:

```python
# Handle NaN values before conversion
volume = latest.get("Volume", 0)
volume = 0 if pd.isna(volume) else int(volume)
```

### Error: "AttributeError: 'DataFrame' object has no attribute 'tolist'"

**Description**: This error occurs in the momentum strategy when trying to convert historical price data.

**Solution**: This issue has been fixed to properly handle different DataFrame structures:

- Checks if the DataFrame is multi-index (multiple symbols)
- Ensures the 'Close' column exists before accessing it
- Drops NaN values before conversion to list

### Error: "SyntaxError: 'continue' not properly in loop"

**Description**: This error occurs in the market data processing when a `continue` statement is used outside of a loop.

**Solution**: Replace the `continue` statement with a `return` statement when not in a loop:

```python
# Incorrect:
if data.empty:
    self.logger.warning(f"No data available for {symbol}")
    continue  # Error: not in a loop

# Correct:
if data.empty:
    self.logger.warning(f"No data available for {symbol}")
    return  # or another appropriate action
```

## Docker Issues

### Issue: Container exits immediately after start

**Possible causes and solutions:**

1. **Port conflict**: Another application may be using port 8501

   - Solution: Change the port mapping in the `docker run` command:
     ```bash
     docker run -p 8502:8501 algorithmic-trading-platform
     ```

2. **Missing dependencies**: Some Python libraries might fail to install

   - Solution: Try rebuilding the Docker image with the `--no-cache` flag:
     ```bash
     docker build --no-cache -t algorithmic-trading-platform .
     ```

3. **Memory issues**: Docker might not have enough allocated memory
   - Solution: Increase Docker's memory allocation in Docker Desktop settings

### Issue: Yahoo Finance data not loading

**Possible causes and solutions:**

1. **Network connectivity**: The container might not have internet access

   - Solution: Check your network connectivity and Docker's network settings

2. **API changes or rate limiting**: Yahoo Finance API might have changed or is rate limiting your requests
   - Solution: Update the `yfinance` package to the latest version in requirements.txt
   - Solution: Use the built-in Mock Data feature (see below)

### Using the Mock Data Feature

If you're experiencing persistent issues with the Yahoo Finance API:

1. **When initializing the application**:

   - Check the "Use mock data" checkbox in the initialization panel
   - Select a market scenario (Normal Market, High Volatility, Low Volatility, Market Crash, or Market Rally)
   - This will use generated synthetic data instead of trying to fetch real data

2. **During runtime**:

   - Use the "Data Source Control" panel in the sidebar
   - Toggle the "Use Mock Data" checkbox
   - Select a market scenario from the dropdown
   - Click "Apply Data Source Change"
   - The system will immediately switch between real and mock data sources

3. **Market Scenarios**:

   - **Normal Market**: Standard market behavior with typical volatility
   - **High Volatility**: Highly volatile market with large price swings
   - **Low Volatility**: Calm market with minimal price movement
   - **Market Crash**: Rapidly declining prices across all symbols
   - **Market Rally**: Rapidly increasing prices across all symbols

4. **Automatic fallback**:
   - The system now automatically switches to mock data after multiple API failures
   - You'll see a warning message when this happens
   - You can switch back to live data using the controls mentioned above if desired

## Python Environment Issues

### Issue: ImportError or ModuleNotFoundError

**Solution:**

```bash
pip install -r requirements.txt
```

### Issue: Streamlit command not found

**Solution:**

```bash
pip install streamlit
```

## Application Issues

### Issue: Market data shows "N/A" for all values

**Possible causes and solutions:**

1. **Invalid symbols**: Verify that you're using valid stock symbols
2. **API rate limiting**: Yahoo Finance might be rate-limiting requests
   - Solution: Reduce the update frequency in market_data.py

### Issue: Order matching not working

**Possible causes and solutions:**

1. **No matching orders**: Ensure there are both buy and sell orders at compatible prices
2. **Order book configuration**: Check the order book implementation in order_book.py

## Getting Help

If you're still experiencing issues:

1. Open an issue on the GitHub repository
2. Check the console logs for specific error messages
3. Try running the application outside of Docker for debugging
