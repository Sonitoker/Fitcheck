import torch
from PIL import Image
from torchvision import transforms
import pickle
import os
from typing import Dict, List
import pandas as pd
import logging
from src.config import config as cfg
from src.models.Model import CompatibilityModel
from src.dataset.Dataloader import FashionCompleteTheLookDataloader
from src.utils.similarity import calculate_similarity

logger = logging.getLogger(__name__)

class CustomImageRecommender:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        self.model = self._load_model()
        self.transform = self._get_transforms()
        self.cached_features = self._load_cached_features()
        self.metadata = self._load_metadata()

    def _get_transforms(self):
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def _load_model(self):
        try:
            model_path = f"{cfg.TRAINED_MODEL_DIR}/trained_compatibility_model_epoch5.pth"
            logger.info(f"Loading model from: {model_path}")

            model = CompatibilityModel()
            model.load_state_dict(
                torch.load(model_path, map_location=self.device)["model_state_dict"]
            )
            model.to(self.device)
            model.eval()
            return model

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def _load_cached_features(self):
        try:
            features_path = f"{cfg.PACKAGE_ROOT}/features/cached_embeddings/compatible_product_embedding.pickle"
            logger.info(f"Loading cached features from: {features_path}")

            with open(features_path, "rb") as file:
                cached_features = pickle.load(file)
                features_tensor = torch.tensor(cached_features, device=self.device).float()
                logger.info(f"Cached features loaded. Shape: {features_tensor.shape}")
                return features_tensor

        except Exception as e:
            logger.error(f"Error loading cached features: {str(e)}")
            raise

    def _load_metadata(self):
        try:
            metadata = FashionCompleteTheLookDataloader().single_data_loader().dataset.metadata
            logger.info(f"Metadata loaded. Shape: {metadata.shape}")

            # Ensure metadata is a DataFrame
            if not isinstance(metadata, pd.DataFrame):
                metadata = pd.DataFrame(metadata)

            return metadata

        except Exception as e:
            logger.error(f"Error loading metadata: {str(e)}")
            raise

    def get_recommendations_for_image(self, image_path: str, product_type: str, top_k: int = 5) -> List[Dict]:
        try:
            logger.info(f"Processing image: {image_path} for product type: {product_type}")

            # Validate image path
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")

            # Step 1: Load and preprocess the image
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)

            # Step 2: Generate features for the query image using the pre-trained model
            with torch.no_grad():
                query_features = self.model(image_tensor)
                logger.debug(f"Generated features for the input image. Shape: {query_features.shape}")

            # Step 3: Calculate cosine similarity between the query image features and all cached product features
            similarity_scores = calculate_similarity(
                query_features.cpu().squeeze(0),
                self.cached_features.cpu(),
                'cosine'
            )

            # Step 4: Ensure self.metadata is a DataFrame
            if not isinstance(self.metadata, pd.DataFrame):
                raise TypeError("Expected self.metadata to be a Pandas DataFrame, but got: {type(self.metadata)}")

            # Step 5: Add similarity scores to metadata
            self.metadata["similarity_score"] = similarity_scores.cpu()

            # Step 6: Filter out the products from the same category as the input image
            filtered_metadata = self.metadata[self.metadata["product_type"] != product_type]

            # Step 7: Sort the products by similarity score and pick the top product from each category
            recommended_products_metadata_all_cat = (
                filtered_metadata.sort_values(by="similarity_score", ascending=False)
                .groupby("product_type")
                .first()
            )

            # Get top N recommendations as a list of dictionaries
            top_recommendations = recommended_products_metadata_all_cat.sort_values(
                by="similarity_score", ascending=False
            ).head(top_k).to_dict(orient="records")

            # Return just the list of recommended products to match the return type annotation
            return top_recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations for image {image_path}: {str(e)}")
            raise