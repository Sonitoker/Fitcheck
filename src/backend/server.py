import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from src.recommend import recommend_complementary_products

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data/fashion_v2/train_single/<path:filename>')
def serve_image(filename):
    return send_from_directory('C:/Users/soni/AI project/FitCheck/src/dataset/data/fashion_v2/train_single', filename)

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()

    # Assuming recommend_complementary_products returns the full recommendation dictionary
    recommendations = recommend_complementary_products(product_id=data['product_id'])

    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True, port=5000)