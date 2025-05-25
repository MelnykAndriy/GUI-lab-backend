## Setup and Installation

1. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```
   python manage.py runserver
   ```

## Local testing scenarios

### 1. Register a new user
Send a POST request to `/api/users/register/`:
```sh
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "password": "password123",
    "gender": "male",
    "dob": "1990-01-01"
  }' | jq
```

### 2. Login and obtain JWT tokens
Send a POST request to `/api/users/login/`:
```sh
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "password123"
  }' | jq
```

### 3. Refresh your access token
Send a POST request to `/api/users/token/refresh/`:
```sh
curl -X POST http://localhost:8000/api/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<your_refresh_token>"
  }' | jq
```

### 4. Access protected endpoints
Include the access token in the `Authorization` header:
```
Authorization: Bearer <your_access_token>
```

#### Get current user info (returns nested profile)
```sh
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer <your_access_token>" | jq
```

#### Update current user profile
```sh
curl -X PUT http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {
      "name": "John Updated",
      "gender": "other",
      "dob": "1991-02-02"
    }
  }' | jq
```

### 5. Send a message
POST to `/api/chats/messages/`:
```sh
curl -X POST http://localhost:8000/api/chats/messages/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "receiverId": 2,
    "content": "Hello!"
  }' | jq
```

### 6. Get chat messages
GET `/api/chats/messages/<userId>/`:
```sh
curl -X GET http://localhost:8000/api/chats/messages/<userId>/ \
  -H "Authorization: Bearer <your_access_token>" | jq
```

### 7. Get recent chats
GET `/api/chats/`:
```sh
curl -X GET http://localhost:8000/api/chats/ \
  -H "Authorization: Bearer <your_access_token>" | jq
```

### 8. Upload avatar
POST to `/api/users/me/avatar` with `multipart/form-data` containing an `avatar` file field:
```sh
curl -X POST http://localhost:8000/api/users/me/avatar \
  -H "Authorization: Bearer <your_access_token>" \
  -F "avatar=@/path/to/avatar.jpg" | jq
```

### 9. Get user by email
GET `/api/users/search/<email>/`:
```sh
curl -X GET http://localhost:8000/api/users/search/<email>/ \
  -H "Authorization: Bearer <your_access_token>" | jq
```

---

You can use [httpie](https://httpie.io/), [curl](https://curl.se/), [Postman](https://www.postman.com/), or Swagger UI for testing.

## API Endpoints

Swagger/OpenAPI specification file [`swagger.yml`](./swagger.yml). You can use tools like [Swagger UI](https://swagger.io/tools/swagger-ui/) or [Redoc](https://github.com/Redocly/redoc) to visualize and interact with the API documentation.

## Creating Test Users (for Bot Auto-Reply)

To automatically create the bot users for testing, run:

```sh
python manage.py create_bot_users
```

This will create the following users (if they do not already exist):
- alice@example.com
- bob@example.com
- charlie@example.com
- dave@example.com
- eve@example.com

You can use any password you like by editing the script, but the default is `testpass` for all users.


