from flask import Flask, jsonify


app = Flask(__name__)
@app.route('/') 
def multi_shipping_rates():
    return jsonify({'json_data': 'getting started 🚀'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)