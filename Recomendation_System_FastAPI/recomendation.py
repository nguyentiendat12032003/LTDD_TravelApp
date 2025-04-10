import firebase_admin
from firebase_admin import credentials, db
from fastapi import FastAPI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Khởi tạo Firebase
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://travelapp-8b759-default-rtdb.firebaseio.com/"})

app = FastAPI()

@app.get("/recommend/{user_id}")
def recommend(user_id: str):
    ref = db.reference("/")
    data = ref.get()

    # Lấy thông tin user
    user = data["Users"].get(user_id)
    if not user:
        return []

    user_preferences = " ".join(user["preferences"])  # Ghép preferences thành 1 câu

    # Lấy danh sách tour
    tours = data["Popular"]
    
    # Chuẩn bị dữ liệu cho TF-IDF
    descriptions = [tours[tour]["description"] for tour in tours]
    descriptions.insert(0, user_preferences)  # Thêm user preferences vào đầu danh sách

    # Vector hóa bằng TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(descriptions)
    
    # Tính Cosine Similarity giữa user_preferences và các tour
    user_vector = tfidf_matrix[0]
    tour_vectors = tfidf_matrix[1:]
    similarities = cosine_similarity(user_vector, tour_vectors)[0]

    # Xếp hạng tour theo độ tương đồng
    ranked_tours = sorted(zip(tours.keys(), similarities), key=lambda x: x[1], reverse=True)
    top_4 = [tour for tour, _ in ranked_tours[:4]]

       # In ra console
    print(f"User: {user_id}")
    print(f"Preferences: {user_preferences}")
    print(f"Top 4 recommended tours: {top_4}")

    # Lấy top 4 tour có điểm cao nhất
    return [tour for tour, _ in ranked_tours[:4]]
