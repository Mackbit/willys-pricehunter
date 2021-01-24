#!/bin/bash
docker build -t willys ./
docker stop willys > /dev/null 2>&1
docker rm willys > /dev/null 2>&1
echo "Container id: "
docker run -d --restart unless-stopped --env-file .env_local --name willys -p 666:80 willys
docker container logs willys -f