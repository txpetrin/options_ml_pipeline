# Example Flask endpoint
from flask import Flask, request, jsonify
import yfinance as yf

app = Flask(__name__)

@app.route('/api/stock-data')
def stock_data():
    ticker = request.args.get('ticker', 'AAPL')
    period = request.args.get('period', '1mo')
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return jsonify({
        'dates': hist.index.strftime('%Y-%m-%d').tolist(),
        'prices': hist['Close'].tolist()
    })

if __name__ == '__main__':
    app.run(debug=True)