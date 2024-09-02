import os
import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv
from fastapi import status
from motor.motor_asyncio import AsyncIOMotorClient
from mv.main import app
from mv.auth import get_current_user
from mv.schema import UserBase





load_dotenv()

MongoDB_details = os.getenv("MongoDB_details","MONGO_DB_CONNECTION_URI" )


@pytest.fixture(autouse=True)
def initialize_db():
    test_client = AsyncIOMotorClient(MongoDB_details)
    test_database = test_client.Test_db
    global test_collection
    test_collection = test_database.get_collection("test")
    yield
    test_client.drop_database("Test_db")

# def override_get_db():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# app.dependency_overrides[get_db] = override_get_db



@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# client = TestClient(app)


@pytest.mark.parametrize("username, password", [("mana", "123")])
def test_signup( client,initialize_db,username,password):
 response = client.post(
        "/signup",
        json={"username": username, "password": password}
    )
 assert response.status_code == status.HTTP_200_OK
 assert response.json()["username"] == username
    # Then login the user

@pytest.mark.parametrize("username, password", [("mana", "123")])
def test_login(client,initialize_db,username, password):

    response = client.post(
        "/login",
        data = {"username": username, "password": password}
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert data["token_type"] == "bearer"

@pytest.mark.parametrize("username, password", [("mana", "123")])
def test_create_movie(client,initialize_db,username,password):
    

    response = client.post(
        "/login",
        data = {"username": username, "password": password}
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    token = response.json()["access_token"]

    response = client.post("/MoviesCreate", headers={"Authorization":f"Bearer{token}"}, json={"title":"lambic ", "description":"some description","release_year":2020,"producer":"some producer","user_id":"17177171"})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["title"] == "lambic"



@pytest.mark.parametrize("username,  password", [("mana", "123")])
def test_get_movies(client,initialize_db,username, password):                    
   

    # response = client.post(
    #     "/login",
    #     data = {"username": username, "password": password}
    # )
    # data = response.json()
    # assert response.status_code == status.HTTP_200_OK
    # assert "access_token" in response.json()
    # token = response.json()["access_token"]

    # create a movie
    movie_data = {"title": "Test Movie", "description":"Test Description","release_year":2020,"producer":"matt"}
    response = client.post("/MoviesCreate", json=movie_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    response = client.get("/Movies")
    assert response.status_code == status.HTTP_200_OK
    
@pytest.mark.parametrize("username,  password", [("mana", "123")])
def test_update_movie(client,initialize_db,username, password):
    

    response = client.post(
        "/login",
        data = {"username": username, "password": password}
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert data["token_type"] == "bearer"
    token = response.json()["access_token"]
 
    movie_data = {"title": "Test Movie", "description":"Test Description","release_year":2020,"producer":"matt"}
    response = client.post("/MoviesCreate", json=movie_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()


    movie_data = {"title": "Updated Test Movie", "description": "Updated Test Description","release_year":2020,"producer":"matt"}
    response = client.put("/MovieEdit", json=movie_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().get("title") == "Updated Test Movie"
    assert response.json().get("description") == "Updated Test Description"
    assert response.json() == {
       "id": response.json()['id'],
        "title": "Updated Test Movie",
        "description": "Updated Test Description",
        "release_date": f"{response.json()['release_date']}",
        "updated_at": f"{response.json()['updated_at']}"
    }
    
@pytest.mark.parametrize("username,  password", [("mana", "123")])
def test_delete_movie(client,initialize_db,username, password):


    response = client.post(
        "/login",
        data = {"username": username, "password": password}
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert data["token_type"] == "bearer"
    token = response.json()["access_token"]

    movie_data = {"title": "Test Movie", "description":"Test Description","release_year":2020,"producer":"matt"}

    response = client.post("/MoviesCreate", json=movie_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    response = client.delete("/MovieDelete", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.get("/Movie", headers={"Authorization": f"Bearer{token}" })
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Movie not found"




@pytest.mark.parametrize("username,  password", [("mana", "123")])
def test_get_movie_ratings(client,initialize_db,username, password):
   
    # Then login the user
    response = client.post(
        "/login",
        data = {"username": username, "password": password}
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    token = data["token_type"] == "bearer"
    
    response = client.post(
        "/ratings",
        json={
            "movie_id" : "1",
            
            "rate_comments":"dndndnn",
            "rating": 7,
            
        },
       
    )
    
    #Get the ratings of the movie 
    response = client.get("/ratings")
    assert response.status_code == status.HTTP_200_OK
    # assert response.json() == "average_rating : 6.5"
    # assert response.json().get("detail") == "message" "No movies found"
