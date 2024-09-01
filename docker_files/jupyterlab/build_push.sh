#!/bin/bash

# 定义变量
DOCKER_USERNAME="allanwlz"        # 替换为你的Docker Hub用户名
IMAGE_NAME="ezqt-jupyter"         # 替换为你想要的镜像名称
VERSION="latest"                  # 替换为你的镜像版本标签，例如 "latest" 或 "v1.0"

# echo "Please login to Docker Hub:"
docker login --username "$DOCKER_USERNAME"

# 构建Docker镜像
docker build -t ${IMAGE_NAME}:${VERSION} .

# 为Docker镜像打标签，以便推送到Docker Hub
docker tag ${IMAGE_NAME}:${VERSION} ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}

# 推送Docker镜像到Docker Hub
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}

# 打印完成消息
echo "Image ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION} pushed to Docker Hub successfully."
