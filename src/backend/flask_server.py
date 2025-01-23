import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import tempfile
from werkzeug.utils import secure_filename
import logging

# Import the custom image recommender
from src.recommender import CustomImageRecommender

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the recommender
recommender = CustomImageRecommender()

# Configure upload folder
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/')
def index():
    return render_template('index2.html')


@app.route('/data/fashion_v2/train_single/<path:filename>')
def serve_image(filename):
    try:
        return send_from_directory('C:/Users/soni/AI project/FitCheck/src/dataset/data/fashion_v2/train_single', filename)
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")
        return jsonify({'error': 'Image not found'}), 404

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Log incoming request data
        logger.debug(f"Files in request: {request.files}")
        logger.debug(f"Form data in request: {request.form}")

        # Check if image exists in request
        if 'image' not in request.files:
            logger.error("No image file in request")
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({'error': 'No selected file'}), 400

        # Validate product type
        product_type = request.form.get('product_type')
        if not product_type or not product_type.strip():
            logger.error("Missing product type")
            return jsonify({'error': 'Product type not provided'}), 400

        product_type = product_type.strip()
        logger.info(f"Processing request for product type: {product_type}")

        if not file or not allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type'}), 400

        # Save and process the file
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)

        try:
            file.save(temp_path)
            logger.info(f"File saved temporarily at: {temp_path}")

            # Generate recommendations
            recommendations = recommender.get_recommendations_for_image(temp_path, product_type)

            # Process recommendations to ensure all paths are web-friendly
            processed_recommendations = []
            for rec in recommendations:
                processed_rec = rec.copy()
                # Convert image paths to web-friendly URLs
                if 'image_path' in processed_rec:
                    processed_rec['image_path'] = processed_rec['image_path'].replace('\\', '/')
                processed_recommendations.append(processed_rec)

            logger.info(f"Generated {len(processed_recommendations)} recommendations")
            print(processed_recommendations)

            return jsonify({
                'recommendations': processed_recommendations
            })

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return jsonify({'error': f"Error processing image: {str(e)}"}), 500

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.debug(f"Cleaned up temporary file: {temp_path}")

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)