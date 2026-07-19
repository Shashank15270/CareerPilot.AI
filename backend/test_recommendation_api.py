import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_status_endpoint():
    print("\n--- Testing GET /api/ status endpoint ---")
    response = client.get("/api/")
    assert response.status_code == 200
    json_data = response.json()
    print("Response JSON:", json_data)
    assert json_data == {"message": "Recommendation API Running"}
    print("GET /api/ passed!")


def test_invalid_file_format():
    print("\n--- Testing POST /api/recommend with invalid file format ---")
    # Send a dummy text file instead of PDF/DOCX
    files = {"resume": ("resume.txt", b"dummy content", "text/plain")}
    response = client.post("/api/recommend", files=files, data={"query": "python", "top_k": "5"})
    print("Response status code:", response.status_code)
    print("Response JSON:", response.json())
    assert response.status_code == 400
    assert "Only PDF and DOCX files are accepted" in response.json()["detail"]
    print("Invalid file format validation passed!")


def test_valid_recommendation():
    print("\n--- Testing POST /api/recommend with valid PDF file ---")
    # We will use an existing PDF in the uploads folder
    test_pdf_path = "uploads/1f0986e69c1b47628ddbd226b4291dbb.pdf"
    
    if not os.path.exists(test_pdf_path):
        print(f"Skipping valid recommendation test because '{test_pdf_path}' does not exist on disk.")
        return

    with open(test_pdf_path, "rb") as f:
        files = {"resume": ("test_resume.pdf", f, "application/pdf")}
        response = client.post("/api/recommend", files=files, data={"query": "python", "top_k": "3"})
        
    print("Response status code:", response.status_code)
    assert response.status_code == 200
    
    recommendations = response.json()
    print(f"Received {len(recommendations)} recommendations:")
    for idx, rec in enumerate(recommendations, 1):
        print(f"#{idx}: {rec.get('title')} at {rec.get('company')} (Score: {rec.get('similarity_score')})")
        assert "title" in rec
        assert "company" in rec
        assert "similarity_score" in rec

    assert len(recommendations) <= 3
    print("Valid recommendation API request passed!")


if __name__ == "__main__":
    test_status_endpoint()
    test_invalid_file_format()
    test_valid_recommendation()
    print("\nAll recommendation API tests passed successfully!")
