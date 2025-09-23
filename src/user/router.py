from fastapi import APIRouter, status, Query
from typing import List, Optional

from src.user.dto import (
    UpdateUserDTO,
    UserDTO,
    FindUserDTO,
    UpdatePasswordDTO
)

from src.user.depends.service import IUserService, UserService
from src.user.entity import UserEntity

from src.protection import RequireAdminToken

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[RequireAdminToken])

@router.post(
    "/",
    response_model=UserDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Creates a new user with the provided details. Requires admin privileges."
)
async def create_user(user_entity: UserEntity, service: IUserService):
    """
    **Description**: Creates a new user in the system.

    **Parameters**:
    - `user_entity`: *UserEntity* - Data for the new user (e.g., name, login, password).
    - `service`: *IUserService* - Dependency-injected user service instance.

    **Returns**:
    - *UserDTO*: Details of the newly created user.

    **Raises**:
    - `AlreadyExistError`: If the login is already in use.

    **Requires admin privileges**

    **Usage**: Endpoint to add a new user via a POST request.
    """
    service: UserService
    return await service.create(user_entity)

@router.get(
    "/",
    response_model=List[UserDTO],
    summary="List all users",
    description="Retrieves a list of all users, optionally paginated. Requires admin privileges."
)
async def list_users(
        user_service: IUserService,
        limit: Optional[int] = Query(None, ge=1, le=10000, description="Maximum number of users to return"),
        offset: Optional[int] = Query(None, ge=0, description="Number of users to skip"),
):
    """
    **Description**: Retrieves a list of registered users with optional pagination.

    **Parameters**:
    - `user_service`: *IUserService* - Dependency-injected user service instance.
    - `limit`: *Optional[int]* - Maximum number of users to return (1 to 10,000).
    - `offset`: *Optional[int]* - Number of users to skip for pagination (minimum 0).

    **Returns**:
    - *List[UserDTO]*: List of user details.

    **Requires admin privileges**

    **Usage**: Endpoint to fetch all users with pagination support.
    """
    user_service: UserService
    return await user_service.get_list(limit=limit, offset=offset)

@router.post(
    "/search",
    response_model=Optional[UserDTO],
    summary="Find a user by criteria",
    description="Finds a single user matching the specified criteria (e.g., login, id). Returns the first match or null."
)
async def find_user_endpoint(user_service: IUserService, dto: FindUserDTO):
    """
    **Description**: Searches for a single user based on provided criteria.

    **Parameters**:
    - `user_service`: *IUserService* - Dependency-injected user service instance.
    - `dto`: *FindUserDTO* - Search criteria (e.g., id, login, name).

    **Returns**:
    - *Optional[UserDTO]*: User details if found, otherwise None.

    **Raises**:
    - `UserIsNotUnique`: If multiple users match the criteria.

    **Requires admin privileges**

    **Usage**: Endpoint to locate a unique user using search parameters.
    """
    user_service: UserService
    return await user_service.get_user(dto)

@router.get(
    "/{user_id}",
    response_model=UserDTO,
    summary="Get user by ID",
    description="Retrieves details for a specific user by their ID.",
    responses={404: {"description": "User not found"}}
)
async def get_user_by_id_endpoint(
    user_id: int,
    user_service: IUserService
):
    """
    **Description**: Fetches a user by their unique integer ID.

    **Parameters**:
    - `user_id`: *int* - Unique identifier of the user.
    - `user_service`: *IUserService* - Dependency-injected user service instance.

    **Returns**:
    - *UserDTO*: Details of the user.

    **Raises**:
    - `UserNotFound`: If no user exists with the given ID.

    **Requires admin privileges**

    **Usage**: Endpoint to retrieve a specific user by ID.
    """
    user_service: UserService
    return await user_service.get(user_id)

@router.put(
    "/{user_id}",
    response_model=UserDTO,
    summary="Update user details",
    description="Updates the name and/or surname for a specific user.",
    responses={404: {"description": "User not found"}}
)
async def update_user(
    pk: int,
    dto: UpdateUserDTO,
    user_service: IUserService
):
    """
    **Description**: Updates a user’s name and/or surname by their ID.

    **Parameters**:
    - `pk`: *int* - Unique identifier of the user.
    - `dto`: *UpdateUserDTO* - New details for the user (name and/or surname).
    - `user_service`: *IUserService* - Dependency-injected user service instance.

    **Returns**:
    - *UserDTO*: Updated user details.

    **Raises**:
    - `UserNotFound`: If no user exists with the given ID.

    **Requires admin privileges**

    **Usage**: Endpoint to modify an existing user via a PUT request.
    """
    user_service: UserService
    return await user_service.update(dto, pk)

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Deletes a user by their ID. Requires admin privileges.",
    responses={404: {"description": "User not found"}}
)
async def delete_user_endpoint(
    pk: int,
    user_service: IUserService
):
    """
    **Description**: Deletes a user permanently based on their ID.

    **Parameters**:
    - `pk`: *int* - Unique identifier of the user.
    - `user_service`: *IUserService* - Dependency-injected user service instance.

    **Returns**:
    - None: HTTP 204 No Content on success.

    **Raises**:
    - `UserNotFound`: If no user exists with the given ID.

    **Requires admin privileges**

    **Usage**: Endpoint to remove a user from the system.
    """
    user_service: UserService
    await user_service.delete(pk)

@router.patch(
    "/{user_id}/password",
    response_model=UserDTO,
    summary="Update user password",
    description="Updates the password for a specific user.",
    responses={404: {"description": "User not found"}}
)
async def update_password_endpoint(
    user_id: int,
    password_data: UpdatePasswordDTO,
    user_service: IUserService
):
    """
    **Description**: Updates the password for the specified user ID.

    **Parameters**:
    - `user_id`: *int* - Unique identifier of the user.
    - `password_data`: *UpdatePasswordDTO* - New password data.
    - `user_service`: *IUserService* - Dependency-injected user service instance.

    **Returns**:
    - *UserDTO*: Updated user details (excluding password).

    **Raises**:
    - `UserNotFound`: If no user exists with the given ID.

    **Requires admin privileges**

    **Usage**: Endpoint to change a user’s password via a PATCH request.
    """
    user_service: UserService
    return await user_service.update_password(password_data, user_id)