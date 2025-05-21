#!/bin/zsh

# Colors for pretty output
green='\033[0;32m'
red='\033[0;31m'
yellow='\033[1;33m'
reset='\033[0m'

print_result() {
  if [[ $1 -eq 0 ]]; then
    echo "${green}✔ $2${reset}"
  else
    echo "${red}✖ $2${reset}"
  fi
}

# Helper to split curl response into body and code using a delimiter
delimiter='---CURL-DELIM---'

# 1. Register a new user
echo "${yellow}Registering a new user...${reset}"
register_response=$(curl -s -w "${delimiter}%{http_code}" -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john.doe@example.com", "password": "password123", "gender": "male", "dob": "1990-01-01"}')
register_body="${register_response%%${delimiter}*}"
register_code="${register_response##*${delimiter}}"

# Accept 200, 201, or 400 with 'already exists' as success
if [[ $register_code == 200 || $register_code == 201 ]]; then
  print_result 0 "User registration ($register_code)"
elif [[ $register_code == 400 && $(echo "$register_body" | grep -qi 'already exists'; echo $?) -eq 0 ]]; then
  print_result 0 "User already exists ($register_code)"
else
  print_result 1 "User registration ($register_code)"
fi

# 2. Login and obtain JWT tokens
echo "${yellow}Logging in...${reset}"
login_response=$(curl -s -w "${delimiter}%{http_code}" -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "john.doe@example.com", "password": "password123"}')
login_body="${login_response%%${delimiter}*}"
login_code="${login_response##*${delimiter}}"

# Only extract tokens from login
access=$(echo "$login_body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))" 2>/dev/null)
refresh=$(echo "$login_body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('refresh', ''))" 2>/dev/null)
if [[ -z "$access" || -z "$refresh" ]]; then
  print_result 1 "Login ($login_code) - Token extraction failed"
else
  print_result $([[ $login_code == 200 ]] && echo 0 || echo 1) "Login ($login_code)"
fi

# 3. Refresh your access token
echo "${yellow}Refreshing access token...${reset}"
refresh_response=$(curl -s -w "${delimiter}%{http_code}" -X POST http://localhost:8000/api/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "'$refresh'"}')
refresh_body="${refresh_response%%${delimiter}*}"
refresh_code="${refresh_response##*${delimiter}}"
new_access=$(echo "$refresh_body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))" 2>/dev/null)
print_result $([[ $refresh_code == 200 ]] && echo 0 || echo 1) "Token refresh ($refresh_code)"

# 4. Get current user info
echo "${yellow}Getting current user info...${reset}"
me_response=$(curl -s -w "${delimiter}%{http_code}" -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer $new_access")
me_body="${me_response%%${delimiter}*}"
me_code="${me_response##*${delimiter}}"
print_result $([[ $me_code == 200 ]] && echo 0 || echo 1) "Get current user ($me_code)"

# 5. Send a message (to self for test)
echo "${yellow}Sending a message...${reset}"
msg_response=$(curl -s -w "${delimiter}%{http_code}" -X POST http://localhost:8000/api/chats/messages/ \
  -H "Authorization: Bearer $new_access" \
  -H "Content-Type: application/json" \
  -d '{"receiverId": 2, "content": "Hello!"}')
msg_body="${msg_response%%${delimiter}*}"
msg_code="${msg_response##*${delimiter}}"
print_result $([[ $msg_code == 200 || $msg_code == 201 ]] && echo 0 || echo 1) "Send message ($msg_code)"

# 6. Get chat messages
echo "${yellow}Getting chat messages...${reset}"
chat_response=$(curl -s -w "${delimiter}%{http_code}" -X GET http://localhost:8000/api/chats/messages/2/ \
  -H "Authorization: Bearer $new_access")
chat_body="${chat_response%%${delimiter}*}"
chat_code="${chat_response##*${delimiter}}"
print_result $([[ $chat_code == 200 ]] && echo 0 || echo 1) "Get chat messages ($chat_code)"

# 7. Get recent chats
echo "${yellow}Getting recent chats...${reset}"
recent_response=$(curl -s -w "${delimiter}%{http_code}" -X GET http://localhost:8000/api/chats/ \
  -H "Authorization: Bearer $new_access")
recent_body="${recent_response%%${delimiter}*}"
recent_code="${recent_response##*${delimiter}}"
print_result $([[ $recent_code == 200 ]] && echo 0 || echo 1) "Get recent chats ($recent_code)"

# 8. Search user by email
echo "${yellow}Searching user by email...${reset}"
search_response=$(curl -s -w "${delimiter}%{http_code}" -X GET http://localhost:8000/api/users/search/john.doe@example.com/ \
  -H "Authorization: Bearer $new_access")
search_body="${search_response%%${delimiter}*}"
search_code="${search_response##*${delimiter}}"
print_result $([[ $search_code == 200 ]] && echo 0 || echo 1) "Search user by email ($search_code)"

echo "${green}All smoke tests completed.${reset}"
