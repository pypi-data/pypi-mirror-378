# SMC Screener 📈

A Python package for **Smart Money Concepts (SMC)** analysis and stock screening, designed to identify key market levels such as swing highs/lows, order blocks, fair value gaps (FVGs), and premium/discount zones.

## Features ✨
- **SMC Analysis**: Identifies swing highs/lows, order blocks, FVGs, and market structure breaks using `yfinance` data. 📊
- **Stock Screener**: Screens stocks near key SMC levels based on a proximity percentage. 🔍
- **Visualization**: Generates candlestick charts with SMC levels using `matplotlib`. 📉
- **Output Options**: Saves results to CSV files and/or Google Sheets. 📄📑
- **Interactive CLI**: Choose tasks (analysis, screener, or both) and stock lists (e.g., Nifty 50, F&O). 🖥️

## Installation 🚀

1. **Install via pip**:
   ```bash
   pip install smc-screener
   ```
   *Note*: The package is not yet on PyPI. To install locally, use the wheel file (see [Development Setup](#development-setup) 🛠️).

2. **Install Dependencies**:
   The package requires the following Python libraries:
   - `yfinance>=0.2.44`
   - `pandas>=2.2.2`
   - `numpy>=1.26.4`
   - `matplotlib>=3.9.2`
   - `gspread>=6.1.2` (optional, for Google Sheets)
   - `oauth2client>=4.1.3` (optional, for Google Sheets)
   - `tqdm>=4.66.5`

   Install them manually if needed:
   ```bash
   pip install yfinance pandas numpy matplotlib gspread oauth2client tqdm
   ```

3. **Google Sheets Setup** (optional, for `output_format="google_sheets"` or `"both"`) 📑:
   - Create a Google Cloud project and enable the **Google Sheets API** and **Google Drive API**. 🔧
   - Create a service account and download the JSON credentials file. 🔑
   - Save the JSON file as `Credentials/credentials.json` in your project directory.
   - Share your Google Sheet with the service account’s email (found in the JSON file) with edit access.
   - Update the `spreadsheet_id` in `main_pipeline.py` with your Google Sheet ID (from the URL: `https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit`).

## Usage 🛠️

### Command-Line Interface
Run the package directly from the command line:
```bash
smc-trading
```
This launches an interactive CLI where you can:
- **Select a task**: SMC Analysis, SMC Screener, or both. 🔄
- **Choose a stock list**: Nifty Top 10, Nifty 50, F&O, or Nifty 500. 📋

Example interaction:
```
Select the task to run:
1. SMC Analysis
2. SMC Screener
3. Both (Analysis + Screener)
Enter your choice (1, 2, or 3): 3

Select the stock list to process:
1. Nifty Top 10
2. Nifty 50
3. F&O
4. Nifty 500
Enter your choice (1, 2, 3, or 4): 1

Selected stock list: Nifty Top 10 (10 stocks)
Step 1: Running SMC Analysis... 📊
Step 2: Running SMC Screener... 🔍
Task 'both' completed for Nifty Top 10! 🎉
```

### Programmatic Usage
Run the pipeline programmatically:
```python
from smc_trading import main_pipeline
import asyncio
asyncio.run(main_pipeline.run_full_pipeline())
```

### Customizing Parameters
Edit `main_pipeline.py` to customize:
- **Stock Lists**: Modify `nifty_top_10`, `nifty_50`, `fn_o_stocks`, or `nifty_500`. 📋
- **Period/Interval**: Change `period` (e.g., `"1y"`, `"max"`) and `interval` (e.g., `"1d"`, `"1h"`) for `yfinance` data. ⏳
- **Output Format**: Set `output_format` to `"csv"`, `"google_sheets"`, or `"both"`. 📄
- **Proximity Percentage**: Adjust `proximity_percentage` (default `2.0`) for the screener. 📏
- **Visualization**: Set `visualize=True` for charts or `False` for faster execution. 📉
- **Clear Output**: Set `clear=True` to overwrite existing CSV files or Google Sheets. 🗑️

Example:
```python
await main_pipeline.main_analysis(
    stock_codes=["RELIANCE.NS"],
    spreadsheet_id="your_spreadsheet_id",
    period="6mo",
    interval="1h",
    visualize=True,
    output_format="both"
)
main_pipeline.main_screener(
    proximity_percentage=1.5,
    output_csv="screener_results.csv",
    spreadsheet_id="your_spreadsheet_id",
    output_format="both"
)
```

## Output 📈
- **SMC Analysis**:
  - **CSV**: Saves to `analysis/smc_analysis_summaries.csv` (summary data) and `analysis/smc_analysis_levels.csv` (key levels). 📄
  - **Google Sheets**: Saves to `Summaries` and `Levels` worksheets (if enabled). 📑
  - **Visualization**: Candlestick charts with SMC levels (if `visualize=True`). 📉
- **SMC Screener**:
  - **CSV**: Saves to `screener_results.csv` with stocks near SMC levels. 📄
  - **Google Sheets**: Saves to `Screener_Results` worksheet (if enabled). 📑
  - **Console**: Displays a table of stocks near key levels. 🖥️

## Project Structure 🛠️

   ```
   smc_trading/
   ├── smc_trading/
   │   ├── __init__.py
   │   ├── smc_analysis.py
   │   ├── smc_screener.py
   │   └── main_pipeline.py
   ├── Credentials/
   │   └── credentials.json
   ├── pyproject.toml
   ├── README.md
   ├── LICENSE
   └── requirements.txt
   ```

## yfinance Period & Interval Reference 📅
- **Period**: `"1d"`, `"5d"`, `"1mo"`, `"3mo"`, `"6mo"`, `"1y"`, `"2y"`, `"5y"`, `"10y"`, `"ytd"`, `"max"`
- **Interval**: `"1m"`, `"2m"`, `"5m"`, `"15m"`, `"30m"`, `"60m"`, `"90m"`, `"1h"`, `"1d"`, `"5d"`, `"1wk"`, `"1mo"`, `"3mo"`
- **Restrictions**:
  - `"1m"` interval: Only last 7 days max.
  - Intraday intervals (`"1m"`, `"1h"`, etc.): `period ≤ 60d`.
  - Daily/weekly/monthly: Longer periods allowed.

## Troubleshooting 🐞
- **yfinance Rate Limits**: Reduce `batch_size` or increase `delay` in `main_pipeline.py`. 🕒
- **Google Sheets Errors**: Verify `Credentials/credentials.json` and share the Google Sheet with the service account. 🔑
- **No Data**: Check ticker validity (e.g., `RELIANCE.NS`). Use `yf.Ticker("TICKER").info` to verify. 📊
- **Visualization Issues**: Ensure `matplotlib` is installed and `visualize=True`. 📉
- **Screener Empty**: Run SMC Analysis first to generate `smc_analysis_levels.csv` and `smc_analysis_summaries.csv`. 🔍

## License 📜
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing 🤝
Contributions are welcome! Please submit a pull request or open an issue on the repository.

Happy trading! 🎉