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

docker rmi -f container-vog-fornecedor 2>/dev/null || true
docker rmi -f container-vog-almoxarifado 2>/dev/null || true
docker rmi -f container-vog-fabrica 2>/dev/null || true
docker rmi -f container-vog-linha 2>/dev/null || true
docker rmi -f container-vog-ordem 2>/dev/null || true

docker build -t container-vog-fornecedor ./Fornecedor
docker build -t container-vog-almoxarifado ./Almoxarifado
docker build -t container-vog-fabrica ./Fabrica
docker build -t container-vog-linha ./Linha
docker build -t container-vog-ordem ./OrdemProducao