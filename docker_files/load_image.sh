#!/bin/bash

# 指定包含镜像的目录
image_dir="images"

# 检查目录是否存在
if [ ! -d "$image_dir" ]; then
    echo "Directory $image_dir does not exist."
    exit 1
fi

# 在指定目录中查找所有.tar文件并加载它们
for image_file in "$image_dir"/*.tar; do
    # 检查是否有文件匹配
    if [ -f "$image_file" ]; then
        echo "Loading image from $image_file"
        docker load -i "$image_file"
    else
        echo "No .tar files found in $image_dir."
        break
    fi
done

echo "All images in $image_dir have been loaded."
