# https://mer.vin/2023/11/get-stock-price-with-basic-auth/
from flask import Flask, request, Response
import json, os
import yfinance as yf

app = Flask(__name__)

# API_KEY = "My_API_Key"  # Replace with your actual API key
API_KEY = os.getenv("API_KEY")

def validate_api_key(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False

    try:
        auth_type, provided_api_key = auth_header.split(None, 1)
        if auth_type.lower() != 'basic':
            return False

        return provided_api_key == API_KEY
    except Exception:
        return False

@app.route("/")
def index():
    return f"""
    Hello Quant! 
    API_KEY = {API_KEY}
    ---
    Go to /stock?symbol=AAPL
    """

@app.route('/stock', methods=['GET'])
def get_stock_data():
    if not validate_api_key(request):
        return Response(json.dumps({"error": "Invalid API key"}),
                        status=401,
                        mimetype='application/json')

    symbol = request.args.get('symbol')
    if not symbol:
        return Response(json.dumps({"error": "Symbol parameter is required"}),
                        status=400,
                        mimetype='application/json')

    stock = yf.Ticker(symbol)
    stock_price = stock.history(period="1d")['Close'].iloc[-1]

    if stock_price is None:
        return Response(json.dumps({"error": "No current price data available for the given symbol"}),
                        status=404,
                        mimetype='application/json')

    return Response(json.dumps({"symbol": symbol, "stock_price": stock_price}),
                    mimetype='application/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0', 
            port=8080,
            debug=True
            )