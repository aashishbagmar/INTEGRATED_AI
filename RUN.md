pandas
numpy
scikit-learn
transformers
torch

## How to Run This Project

1. Create a virtual environment:
	- `python -m venv venv`
	- Activate it:
	  - Windows: `./venv/Scripts/Activate.ps1`
	  - macOS/Linux: `source venv/bin/activate`

2. Install dependencies:
	- `pip install -r requirements.txt`

3. Run the project from the parent folder:
	- `python -m Stock_Sentiment_Analysis.main`

4. Enter the stock symbol when prompted (e.g., RELIANCE, TCS, AAPL).

**Note:**
- Do not run with `python main.py` (imports will break).
- First run may take time (model downloads).