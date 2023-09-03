#!/bin/bash

# Defina as imagens desejadas (separadas por espaço)
IMAGES=("container-vog-fornecedor" "container-vog-almoxarifado" "container-vog-fabrica" "container-vog-linha" "container-vog-ordem")

# Loop através das imagens
for IMAGE in "${IMAGES[@]}"; do
    # Encontre e pare todos os containers relacionados à imagem
    CONTAINERS=$(docker ps -a --format "{{.ID}} {{.Image}}" | grep "$IMAGE" | awk '{print $1}')
    for CONTAINER in $CONTAINERS; do
        echo "Parando e removendo container $CONTAINER relacionado à imagem $IMAGE"
        docker stop "$CONTAINER" && docker rm "$CONTAINER"
    done
done
