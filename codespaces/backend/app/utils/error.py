from fastapi import HTTPException, status


class Error(Exception):

    TEACHER_NOT_FOUND_EXCEPTION = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Teacher not found."
    )
    
    PUPIL_NOT_FOUND_EXCEPTION = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Pupil not found."
    )
    
    LOGIN_EXISTS = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Login already exists."
    )
    
    UNAUTHORIZED_INVALID = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect login or password."
    )
    
    