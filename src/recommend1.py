import pickle

from src.config import config as cfg
from src.dataset.Dataloader import FashionCompleteTheLookDataloader, FashionProductSTLDataloader
from src.utils.similarity import calculate_similarity





def recommend_complementary_products(product_id, task_name="compatible_product", top_n=5):
    """takes in the product id and returns the top 5 compatible product to the input product"""
    # get extracted features
    with (
        open(f"{cfg.PACKAGE_ROOT}/features/cached_embeddings/{task_name}_embedding.pickle", "rb")
    ) as file:
        all_compatible_products_features = pickle.load(file)

    # get dataset metadata dataframe
    data_loader = FashionCompleteTheLookDataloader().single_data_loader()
    metadata = data_loader.dataset.metadata[
        ["product_id", "image_single_signature", "product_type", "image_path"]
    ]

    # Function to get a valid random product
    def get_valid_product():
        for _ in range(10):  # Try up to 10 times
            random_product = metadata.sample(1).to_dict(orient="records")[0]
            if random_product["product_id"] in all_compatible_products_features:
                return random_product
        return None

    # Fetch product metadata or select a random fallback if not found
    product_metadata = metadata[metadata["product_id"] == product_id].to_dict(orient="records")
    if not product_metadata:
        product_metadata = get_valid_product()
        if not product_metadata:  # Final fallback: empty result
            return {"input_product": {}, "recommended_compatible_products": []}
    else:
        product_metadata = product_metadata[0]

    # Fetch product feature vector safely
    try:
        product_feature_vec = all_compatible_products_features[product_metadata["product_id"], :]
    except KeyError:
        fallback_product = get_valid_product()
        if fallback_product:
            product_feature_vec = all_compatible_products_features[fallback_product["product_id"], :]
        else:
            return {"input_product": {}, "recommended_compatible_products": []}

    # Calculate compatibility score
    compatibility_score = calculate_similarity(
        product_feature_vec, all_compatible_products_features, "cosine"
    )

    # Filter metadata to exclude input product category
    input_product_category = product_metadata["product_type"]
    metadata["compatibility_score"] = compatibility_score.cpu().numpy()

    recommended_products_metadata_all_cat = (
        metadata[(metadata["product_type"] != input_product_category)]
        .sort_values(by="compatibility_score", ascending=False)
        .groupby("product_type")
        .head(1)
    )

    # Return the top N compatible products
    return {
        "input_product": product_metadata,
        "recommended_compatible_products": recommended_products_metadata_all_cat
        .sort_values(by="compatibility_score", ascending=False)
        .head(top_n)
        .to_dict(orient="records"),
    }

if __name__ == "__main__":
    import random

    #similar_recommendations = recommend_similar_products(product_id=random.randint(1, 38000))
    compatible_recommendations = recommend_complementary_products(
        product_id=random.randint(1, 454000)
    )

    from utils.image_utils import display_compatible_images, display_recommended_products

    print(compatible_recommendations)
    display_recommended_products(
        compatible_recommendations["input_product"]["image_path"],
        *[
            rec["image_path"]
            for rec in compatible_recommendations["recommended_compatible_products"]
        ],
        [
            round(rec["compatibility_score"], 3)
            for rec in compatible_recommendations["recommended_compatible_products"]
        ],
        save_image=True,
    )
