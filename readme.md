# to get into container
docker exec -it c89536b0312d bash
# or
docker exec -it flask-hello_flask_1 bash

curl -i -X POST -H "Content-Type: application/json" -d '{"key":"val"}' http://localhost:5000/iris_post