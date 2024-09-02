from fastapi import FastAPI, HTTPException,Depends,status
from fastapi.security import OAuth2PasswordRequestForm
from mv.crud import user_crud_service,crud_service,comments_crud,rate_crud
from mv.schema import UserCreate,UserBase,MovieCreate,UserDB,Movie,UserRead,Comment,CommentEdit,RatingCreate,Subcomment
from mv.auth import pwd_context, authenticate_user, create_access_token, get_current_user
from mv.logger import get_logger


logger = get_logger(__name__)

app = FastAPI()

@app.post("/signup")
def signup(user: UserCreate):
    logger.info("creating user")
    db_user = user_crud_service.get_user_by_username(username=user.username)
    if db_user:
        logger.exception(f"user with username {user.username} already exists")
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(user.password)
    logger.info("user successfully created")
    return user_crud_service.create_user(user_data=user, hashed_password=hashed_password)

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info("logging in user")
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.get('username')})
    
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.get('id')}



@app.post("/MoviesCreate",status_code= status.HTTP_201_CREATED)
def create_movie(movie_in: MovieCreate,user:UserBase = Depends(get_current_user)):
    logger.info(f"creating movie by user {user['username']}")
    movie = crud_service.create_movie(movie_in)
    if not movie:
        raise HTTPException(status_code=400, detail={"message": "Invalid input"})
    return {
        "message": "movie created successfully!", "data": movie}


@app.get("/Movies")
def get_all_movies():
    movies = crud_service.get_all_movies()
    logger.info("fetching all movies")
    if not movies:
        raise HTTPException(status_code=404, detail={"message": "No movies found"})
    return {"mesage":"successfull","data":movies}




@app.put("/MovieEdit")
def update_movie(movie_id: str, movie_update_in:Movie,user:UserRead = Depends(get_current_user)):
    logger.info(f"updating movie by user {user['username']}")
    movie = crud_service.update_movie(movie_id, movie_update_in)
    if movie["user_id"] != user ["id"]:
        raise HTTPException(status_code=403, detail={"message": "You are not authorized to update this movie"})
    if not movie:
        raise HTTPException(status_code=404, detail={"message": "movie does not exists"})
    return {"message": "movie updated successfully", "data": movie}


@app.delete("/MovieDelete")
def delete_movie(movie_id: str,user:UserBase = Depends(get_current_user)):
    logger.info(f"deleting movie by user {user['username']}")
    movie = crud_service.delete_movie(movie_id)
    if movie["user_id"] != user ["id"]:
        raise HTTPException(status_code=403, detail={"message": "You are not authorized to update this movie"})

    if not movie:
        raise HTTPException(status_code=404, detail={"message": "movie does not exists"})
    return {"message": "movie deleted successfully"}


@app.get("/comment")
def get_comments() -> list:
    comments = comments_crud.get_all_comments()
    if not comments:
        raise HTTPException(status_code=404, detail={"message": "No comments found for this movie"})
    return [comments]

@app.post("/comment")
def create_comment(comment_in:Comment,user:UserBase = Depends(get_current_user)):
    logger.info(f"creating comment by user {user['username']}")
    comment = comments_crud.create_comment(comment_in)
    if not comment:
        raise HTTPException(status_code=400, detail={"message": "Invalid input"})
    return {
        "message": "comment created successfully!", "data": comment}

@app.post("/subcomment")
def create_reply_comment(comment_in:Subcomment, user: UserBase = Depends(get_current_user)):
    logger.info(f"creating reply comment by user {user['username']}")
    comment = comments_crud.create_sub_comment(comment_in)
    if not comment:
        raise HTTPException(status_code=400, detail={"message": "Invalid input"})
    return {
        "message": "comment created successfully!", "data": comment}

@app.put("/comments")
def update_comment(comment_id: str, comment_update_in: CommentEdit,user: UserBase = Depends(get_current_user)):
    logger.info(f"updating comment by user {user['username']}")
    comment = comments_crud.update_comment(comment_id, comment_update_in)
    
   
    if not comment:
        raise HTTPException(status_code=404, detail={"message": "comment does not exists"})
    return {"message": "comment updated successfully", "data": comment}

@app.delete("/comments")
def delete_comment(comment_id: str, user: UserRead = Depends(get_current_user)):
    logger.info(f"deleting comment by user {user['username']}")
    # 
    results = comments_crud.delete_comment(comment_id)
    
    if  results:
     return {"message": "comment deleted successfully"}

@app.post("/ratings")
def create_rating(rating_in: RatingCreate, user: UserBase = Depends(get_current_user)):
    logger.info(f"creating rating by user {user['username']}")
    rating = rate_crud.create_rating(rating_in)
    if not rating:
        raise HTTPException(status_code=400, detail={"message": "Invalid input"})
    return {
        "message": "rating created successfully!", "data": rating}

@app.get("/ratings")
def get_ratings():
    ratings = rate_crud.get_all_ratings()
    if not ratings:
        raise HTTPException(status_code=404, detail={"message": "No ratings found for this movie"})
    return ratings