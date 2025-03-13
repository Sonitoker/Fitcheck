import { useState, useEffect } from "react";
import { Text, View, Button, Image, StyleSheet, ScrollView, TouchableOpacity, Alert } from "react-native";
import * as ImagePicker from "expo-image-picker";
import { WebView } from "react-native-webview";

const categories = [
  "Dresses",
  "Shirts & Tops",
  "Pants",
  "Shoes",
  "Handbags",
  "Coats & Jackets",
  "Skirts",
];

export default function Index() {
  const [image, setImage] = useState<any>(null);
  const [itemType, setItemType] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [recommendations, setRecommendations] = useState<any[]>([]);


  useEffect(() => {
    const requestPermissions = async () => {
      const { status: cameraStatus } = await ImagePicker.requestCameraPermissionsAsync();
      const { status: galleryStatus } = await ImagePicker.requestMediaLibraryPermissionsAsync();

      if (cameraStatus !== "granted" || galleryStatus !== "granted") {
        Alert.alert(
          "Permissions Required",
          "Camera and gallery permissions are required to use this feature."
        );
      }
    };

    requestPermissions();
  }, []);

  const pickImageFromGallery = async () => {
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  const captureImageFromCamera = async () => {
    let result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  const handleSubmit = async () => {
    if (!image || !itemType) {
      alert("Please select a category and upload an image.");
      return;
    }

    setLoading(true);

    let formData = new FormData();
    formData.append("image", {
      uri: image,
      name: "photo.jpg",
      type: "image/jpeg",
    });
    formData.append("product_type", itemType);

    try {
      const response = await fetch("http://192.168.68.117:5000/recommend", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setRecommendations(data.recommendations);

      setLoading(false);
    } catch (error) {
      console.error(error);
      alert("Error uploading file");
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>FitCheck</Text>
      <ScrollView style={styles.results}>
        <View style={styles.uploadSection}>
          <Text style={styles.text}>Select a Category:</Text>
          <View style={styles.categoryList}>
            {categories.map((category, index) => (
              <TouchableOpacity
                key={index}
                style={[
                  styles.categoryButton,
                  itemType === category && styles.selectedCategoryButton,
                ]}
                onPress={() => setItemType(category)}
              >
                <Text
                  style={[
                    styles.categoryButtonText,
                    itemType === category && styles.selectedCategoryButtonText,
                  ]}
                >
                  {category}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          <View style={styles.imageOptions}>
            <TouchableOpacity onPress={pickImageFromGallery}>
              <Image
                source={require("../assets/images/gallery.png")} // שנה לנתיב התמונה שלך
                style={styles.optionImage}
              />
            </TouchableOpacity>
            <TouchableOpacity onPress={captureImageFromCamera}>
              <Image
                source={require("../assets/images/camera.png")}
                style={styles.optionImage}
              />
            </TouchableOpacity>
          </View>
          {image && <Image source={{ uri: image }} style={styles.image} />}
          <TouchableOpacity
            style={styles.uploadButton}
            onPress={handleSubmit}
            disabled={loading}
          >
            <Text style={[styles.uploadButtonText, loading && styles.disabledText]}>
              Get Recommendations
            </Text>
          </TouchableOpacity>
        </View>
        {loading && <Text>Processing your image...</Text>}

        {recommendations.length > 0 && (
          <View>
            {recommendations.map((product, index) => (
              <View key={index} style={styles.productCard}>
                <Image
                  source={{
                    uri: product.image_path.startsWith("http")
                      ? product.image_path
                      : `http://192.168.68.117:5000/${product.image_path.replace("./", "")}`,
                  }}
                  style={styles.productImage}

                />
                <Text>{product.product_type}</Text>
              </View>
            ))}
          </View>
        )}
        <View style={styles.chatBotContainer}>
          <WebView
            source={{ uri: "https://www.chatbase.co/chatbot-iframe/SWd_rNKsUmIkroGHabdek" }}
            style={styles.webView}
          />
        </View>
      </ScrollView>
    </View>
  );
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FFF",
    alignItems: "center",
    padding: 20,
  },
  header: {
    fontSize: 30,
    fontWeight: "bold",
    color: "#B76E79",
    marginBottom: 30,
    fontFamily: "Arial",
    textTransform: "uppercase",
  },
  uploadSection: {
    marginBottom: 20,
    alignItems: "center",
    width: "100%",
    padding: 20,
    backgroundColor: "#FFF0F5",
    borderRadius: 10,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 5,
  },
  text: {
    fontSize: 16,
    color: "#B76E79",
    marginBottom: 10,
    fontFamily: "Arial",
    fontWeight: "bold",
  },
  categoryList: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "center",
    marginBottom: 20,
  },
  categoryButton: {
    backgroundColor: "#E6A8D7",
    borderRadius: 8,
    padding: 10,
    margin: 5,
  },
  selectedCategoryButton: {
    backgroundColor: "#B76E79",
  },
  categoryButtonText: {
    color: "#FFF",
    fontSize: 14,
  },
  selectedCategoryButtonText: {
    fontWeight: "bold",
  },
  image: {
    width: 300,
    height: 230,
    marginTop: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#B76E79",
  },
  results: {
    marginTop: 20,
    width: "100%",
  },
  productCard: {
    margin: 50,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "#B76E79",
    borderRadius: 8,
    padding: 0,
    backgroundColor: "#FFF0F5",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 5,
    overflow: "hidden",
    alignItems: "center",
     height: 200,
  },
  productImage: {
    width: "100%",
    height: 200,
    resizeMode: "contain",
     alignSelf: "stretch",
  },
  uploadButton: {
    borderRadius: 8,
    padding: 10,
    margin: 10,
    alignItems: "center",
  },
  uploadButtonText: {
    color: "#B76E79",
    fontSize: 20,
    fontWeight: "bold",
  },
   disabledText: {
      color: "#ccc",
    },
    chatBotContainer: {
      width: "100%",
      marginTop: 20,
      height: 350,
      borderTopWidth: 1,
      borderTopColor: "#B76E79",
    },
    webView: {
      flex: 1,
    },

    imageOptions: {
      flexDirection: "row",
      justifyContent: "center",
      alignItems: "center",
      width: "100%",
    },
    optionImage: {

      width: 80,
      height: 80,
      margin: 10,
      borderColor: "#B76E79",

    },
});
