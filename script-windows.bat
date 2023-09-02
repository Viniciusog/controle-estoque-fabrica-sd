docker rm -f container-vog-fornecedor 2>NUL || true
docker rm -f container-vog-almoxarifado 2>NUL || true
docker rm -f container-vog-fabrica 2>NUL || true
docker rm -f container-vog-linha 2>NUL || true
docker rm -f container-vog-ordem 2>NUL || true

docker build -t container-vog-fornecedor ./Fornecedor
docker build -t container-vog-almoxarifado ./Almoxarifado
docker build -t container-vog-fabrica ./Fabrica
docker build -t container-vog-linha ./Linha
docker build -t container-vog-ordem ./OrdemProducao