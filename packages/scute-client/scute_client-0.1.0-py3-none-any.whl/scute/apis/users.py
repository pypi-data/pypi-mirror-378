from typing import Dict, Any, Optional, Iterator
from .base import BaseClient

class UsersAPI:
    def __init__(self, client: BaseClient):
        self.client = client

    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieves a user by their unique ID.

        :param user_id: User ID
        :return: User data dictionary
        """
        headers = {"Authorization": self.client.app_secret}
        path = f"/apps/{self.client.app_id}/users/{user_id}"
        data = self.client.request("GET", path, headers=headers)
        return data or {}

    def get_user(
        self,
        identifier: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a user using identifier (email) or user ID.

        :param identifier: User's email
        :param user_id: User's ID
        :return: User data dictionary
        :raises ValueError: If neither identifier nor user_id is provided
        """
        if not identifier and not user_id:
            raise ValueError("Either 'identifier' or 'user_id' must be provided.")

        headers = {"Authorization": self.client.app_secret}
        params = {}
        if identifier:
            params["identifier"] = identifier
        if user_id:
            params["user_id"] = user_id

        path = f"/auth/{self.client.app_id}/users"
        data = self.client.request("GET", path, headers=headers, params=params)
        return data or {}

    def list_users(
        self,
        id: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        created_before: Optional[str] = None,
        status: Optional[str] = None,  # "active" | "pending" | "inactive"
        page: Optional[int] = 1,
        limit: Optional[int] = 20
    ) -> Dict[str, Any]:
        """
        Lists users with optional filtering and pagination.

        :return: Dictionary with users list and pagination metadata
        :raises ValueError: If status is invalid
        """
        headers = {"Authorization": self.client.app_secret}
        params = {"page": page, "limit": limit}

        if id:
            params["id"] = id
        if email:
            params["email"] = email
        if phone:
            params["phone"] = phone
        if created_before:
            params["created_before"] = created_before
        if status:
            if status not in {"active", "pending", "inactive"}:
                raise ValueError("Invalid status. Must be 'active', 'pending', or 'inactive'.")
            params["status"] = status

        path = f"/apps/{self.client.app_id}/users"
        return self.client.request("GET", path, headers=headers, params=params) or {}

    def list_all_users(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        created_before: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> Iterator[Dict[str, Any]]:
        """
        Generator that yields all users by automatically paginating.

        :yield: Individual user dictionaries
        """
        page = 1
        while True:
            response = self.list_users(
                email=email,
                phone=phone,
                created_before=created_before,
                status=status,
                page=page,
                limit=limit
            )
            users = response.get("users", [])
            if not users:
                break

            for user in users:
                yield user

            page += 1

    def create_user(self, identifier: str) -> Dict[str, Any]:
        """
        Creates a user using the given identifier (email or phone).

        :param identifier: User's identifier (email or phone number)
        :return: Created user data dictionary
        :raises ValueError: If identifier is not provided
        """
        if not identifier:
            raise ValueError("The 'identifier' (email or phone) is required.")

        headers = {
            "Authorization": self.client.app_secret
        }
        path = f"/apps/{self.client.app_id}/users"
        files = {"identifier": (None, identifier)}  # multipart/form-data

        data = self.client.request("POST", path, headers=headers, files=files)
        return data or {}

    def delete_user(self, user_id: str, access_token: str) -> bool:
        """
        Deletes a user by ID.

        :param user_id: ID of the user to delete
        :param access_token: User's access token
        :return: True if deletion was successful
        :raises ValueError: If user_id or access_token is missing
        """
        if not user_id or not access_token:
            raise ValueError("Both 'user_id' and 'access_token' are required.")

        headers = {
            "Authorization": self.client.app_secret,
            "X-Authorization": access_token
        }
        path = f"/apps/{self.client.app_id}/users/{user_id}"
        response = self.client.request("DELETE", path, headers=headers)

        return response.get("status") == "ok" or response == {}
