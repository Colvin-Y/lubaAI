#!/bin/bash

# 替换为实际参数
API_KEY="AIzaSyDovLKo3djdRbs963vqKdbj-geRWyzMTrg"
API_KEY="AIzaSyCoi4MfFodBoRBj3OEDMcrZVRN-RPbA3oU"
EMAIL="test@example.com"
PASSWORD="password123"

# 发送注册请求
curl -X POST \
  "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=${API_KEY}" \
  -H "content-type: application/json; charset=UTF-8" \
  -H "Referer: localhost" \
  -d "{\"email\":\"${EMAIL}\", \"password\":\"${PASSWORD}\", \"returnSecureToken\":true}"
  
# 使用说明：
# 1. 保存为 test_signup.sh
# 2. 添加执行权限：chmod +x test_signup.sh
# 3. 运行：./test_signup.sh