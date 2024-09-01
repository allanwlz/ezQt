#!/bin/bash

# 创建存储镜像的目录
mkdir -p images

# 读取docker-compose.yml文件中的所有镜像
images=`grep 'image:' docker-compose.yml | awk '{ print \$2 }'`

# 保存每个镜像为tar文件
for image in $images; do
    # 移除可能存在的引号
    clean_image=$(echo $image | tr -d '"')
    # 使用冒号 (:) 分割镜像名称和标签
    IFS=':' read -ra IMAGE_PARTS <<< "$clean_image"
    # 如果镜像不包含标签，则默认为latest
    if [ -z "${IMAGE_PARTS[1]}" ]; then
        IMAGE_PARTS[1]="latest"
    fi
    # 创建一个符合文件命名规范的镜像文件名
    image_filename="${IMAGE_PARTS[0]}_${IMAGE_PARTS[1]}.tar"
    # 替换所有斜线 (/) 为下划线 (_)
    image_filename=${image_filename//\//_}
    # 保存镜像
    echo "Saving $clean_image to $image_filename"
    docker save "$clean_image" -o "images/$image_filename"
done

echo "All images have been saved to the images folder."
