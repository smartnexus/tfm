#!/bin/bash

LIST=`ls -d images/* | cut -f1-2 -d'/' | uniq`
if [ -z "$LIST" ]; then
    echo "No images found in the 'images' directory."
    exit 1
fi
for image in $LIST; do
    echo "Building image: $image"
    pushd $image
    source image_info.sh
    IMAGE_NAME=${image#"images/"}
    if [ -z "$PLATFORMS" ]; then
      docker build -t $IMAGE_NAME:$IMAGE_TAG --build-arg version=$IMAGE_TAG .
    else
      docker buildx build -t $IMAGE_NAME:$IMAGE_TAG --build-arg version=$IMAGE_TAG --platform ${PLATFORMS} .
    fi
    popd
done