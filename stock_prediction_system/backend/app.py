from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from scripts.predict import predict_stock
from config import Config

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if API is running"""
    return jsonify({
        'status': 'healthy',
        'message': 'Stock Prediction API is running'
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Predict a single stock
    
    Expected JSON body:
    {
        "symbol": "AAPL",
        "company_name": "Apple Inc" (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        symbol = data.get('symbol', '').upper().strip()
        company_name = data.get('company_name', '').strip()
        
        if not symbol:
            return jsonify({'error': 'Stock symbol is required'}), 400
        
        if symbol not in Config.STOCK_SYMBOLS:
            return jsonify({
                'error': f'{symbol} not in trained stocks list'
            }), 400
        
        # Make prediction
        result = predict_stock(symbol, company_name)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/stocks', methods=['GET'])
def get_all_stocks():
    """Get list of all available stocks"""
    return jsonify({
        'total': len(Config.STOCK_SYMBOLS),
        'stocks': Config.STOCK_SYMBOLS
    })

@app.route('/api/models/status', methods=['GET'])
def models_status():
    """Check training status"""
    try:
        # Count .pkl files in models directory
        if not os.path.exists(Config.MODEL_DIR):
            trained_count = 0
        else:
            trained_count = len([
                f for f in os.listdir(Config.MODEL_DIR) 
                if f.endswith('.pkl')
            ])
        
        total_stocks = len(Config.STOCK_SYMBOLS)
        
        return jsonify({
            'total_stocks': total_stocks,
            'trained_models': trained_count,
            'remaining': total_stocks - trained_count,
            'progress_percentage': round((trained_count / total_stocks) * 100, 1),
            'status': 'ready' if trained_count == total_stocks else 'incomplete'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/models/list', methods=['GET'])
def list_trained_models():
    """List all trained model symbols"""
    try:
        if not os.path.exists(Config.MODEL_DIR):
            return jsonify({'models': []})
        
        models = [
            f.replace('.pkl', '') 
            for f in os.listdir(Config.MODEL_DIR) 
            if f.endswith('.pkl')
        ]
        
        return jsonify({
            'count': len(models),
            'models': sorted(models)
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("   STOCK PREDICTION API SERVER")
    print("="*60)
    print("  Server running at: http://localhost:5000")
    print("  API Documentation:")
    print("    - GET  /api/health       - Check server status")
    print("    - POST /api/predict      - Predict a stock")
    print("    - GET  /api/stocks       - List all stocks")
    print("    - GET  /api/models/status - Check training progress")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)