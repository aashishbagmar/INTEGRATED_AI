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



FOR Indian stocks 

1. Go to Stock_Sentiment_Analysis\services\price_service.py

2. Comment the current def _load_price_data(symbol: str):

3. UN-comment the commented def _load_price_data(symbol: str):
