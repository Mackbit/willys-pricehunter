#!/bin/bash
docker build -t willys ./
docker stop willys > /dev/null 2>&1
docker rm willys > /dev/null 2>&1
echo "Container id: "
docker run -d --restart unless-stopped -v /home/ubuntu/database:/var/run/database --env-file .env --name willys -p 666:80 willys