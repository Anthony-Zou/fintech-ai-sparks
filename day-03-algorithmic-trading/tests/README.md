# Tests Directory

This directory contains comprehensive tests for the algorithmic trading platform.

## Test Structure

```
tests/
├── run_all_tests.py          # Main test runner script
├── quick_test.py             # Quick smoke test
├── diagnostics/              # Order Books diagnostic tests
│   ├── test_bid_ask_bug.py   # Specific bid/ask placement testing
│   ├── diagnose_order_books.py # Comprehensive Order Books diagnostics
│   ├── test_order_books.py   # Core Order Books functionality
│   ├── test_order_books_ui.py # UI functionality testing
│   └── validate_order_books.py # End-to-end validation
├── integration/              # Integration tests
│   ├── integration_test.py   # Core integration tests
│   ├── end_to_end_test.py    # Full workflow testing
│   └── test_app_functionality.py # App-level testing
└── [unit tests]              # Individual component unit tests
    ├── test_trading_engine.py
    ├── test_order_book.py
    ├── test_position_manager.py
    └── ...
```

## Running Tests

### Run All Tests
```bash
python tests/run_all_tests.py
```

### Run Specific Test Categories

**Diagnostic Tests (Order Books focus):**
```bash
python tests/diagnostics/test_bid_ask_bug.py
python tests/diagnostics/diagnose_order_books.py
```

**Integration Tests:**
```bash
python tests/integration/integration_test.py
python tests/integration/end_to_end_test.py
```

**Quick Smoke Test:**
```bash
python tests/quick_test.py
```

**Unit Tests (with pytest):**
```bash
python -m pytest tests/ -v
```

## Test Categories

### 🔍 Diagnostic Tests
These tests were created to investigate and validate the Order Books functionality:
- **test_bid_ask_bug.py**: Specifically tests for the reported bid/ask placement issue
- **diagnose_order_books.py**: Comprehensive end-to-end Order Books workflow validation
- **test_order_books_ui.py**: UI-focused testing with user guidance validation
- **validate_order_books.py**: User experience and workflow validation

### 🔗 Integration Tests
These tests validate component interaction and full system behavior:
- **integration_test.py**: Core system integration testing
- **end_to_end_test.py**: Complete trading workflow validation
- **test_app_functionality.py**: Application-level functionality testing

### 🧪 Unit Tests
Individual component testing (using pytest framework):
- Trading engine functionality
- Order book operations
- Position management
- Market data handling
- Strategy execution

## Test Results Summary

Recent comprehensive testing has validated:
- ✅ BUY orders correctly placed in bids
- ✅ SELL orders correctly placed in asks  
- ✅ Order book metrics calculation
- ✅ UI display and user guidance
- ✅ Empty order book handling
- ✅ Multi-symbol support

**Conclusion**: No bid/ask placement bug found. System working correctly.

## Troubleshooting

If tests fail:
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check Python path and module imports
3. Verify no cached bytecode issues: `find . -name "*.pyc" -delete`
4. Review test output for specific error messages

## Contributing

When adding new tests:
1. Place unit tests in the main `tests/` directory
2. Place diagnostic tests in `tests/diagnostics/`
3. Place integration tests in `tests/integration/`
4. Update this README if adding new test categories
5. Ensure tests are included in `run_all_tests.py`
