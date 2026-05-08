============================================
   MZ Verifier - Setup Guide
============================================

REQUIREMENTS:
- Windows 10 or 11
- Python 3.10 or higher (download from https://www.python.org/downloads/)
- Internet connection (for email verification)

FIRST TIME SETUP:
1. Install Python (check "Add Python to PATH" during installation)
2. Double-click 'setup.bat'
3. Wait for setup to complete

DAILY USE:
1. Double-click 'run.bat'
2. Browser will open automatically
3. Use the tool
4. To stop: close the black command window

FEATURES:
- Single email verification
- Bulk CSV upload (up to 50,000 emails)
- Parallel processing for speed
- Results: ok, catch_all, invalid, disposable, unknown
- Download results as CSV

TROUBLESHOOTING:
- If 'setup.bat' says "Python not found": Install Python and check "Add to PATH"
- If browser doesn't open: manually go to http://localhost:8501
- If app crashes on large files: try smaller batches (10,000 at a time)

============================================