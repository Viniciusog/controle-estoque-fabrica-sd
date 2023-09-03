# controle-estoque-fabrica-sd
Projeto para controlar o estoque de uma fábrica, gerenciando os produtos feitos e as partes necessárias para a fabricação

## Entidades:
- Fornecedor
- Almoxarifado
- Fábrica
- Linha
- Ordem de Produção

## Como funciona:
Uma empresa possui 2 unidades fabris: fábrica 1 com 5 linhas de produção e fábrica 2 com 8 linhas de produção. A empresa fabrica 1 produto em 5 versões diferentes (Pv1, Pv2, Pv3, Pv4, Pv5).

Cada produto possui uma configuração composta por uma somatória de partes: kit base composto por 43 partes e kit variação composto por uma somatória de partes que variam de 20 a 33 partes dependendo da versão. O total de partes diferentes usadas na fabricação = 100.

Projeto: Desenvolver solução de monitoramento de nível de estoque de partes em cada linha de produção. A fabrica 1 produz os 5 produtos todos os dias com ordens de produção com tamanho de lote de 48 produtos por linha (Fabricação Empurrada). A fabrica 2 fabrica os 5 produtos, porém o tamanho do lote e o produto fabricado variam dia a dia dependendo dos pedidos do mercado (Fabricação Puxada).

A solução deve simular pedidos de produtos dia a dia (aleatório) e calcular quantos produtos devem ser fabricados em função do estoque de cada produto acabado. Deve portanto monitorar nível de estoque de produtos (1 a 5), consumos (via pedido), lote de fabricação para o dia (lista de partes enviado para almoxarifado), abastecimento de partes nas linhas e monitoramento de estoques de partes em cada linha para cada parte. 

Cada linha consome parte de forma aleatória conforme os produtos são fabricados ao longo do dia até o fechamento da ordem de produção (tamanha do lote). O estoque de partes deve apontar nível de estoque VERDE, AMARELO, VERMELHO (kanban) - quando o nível se aproxima do nível vermelho é necessário disparar ordem de reabastecimento para o Almoxarifado.

monitorar nível de estoque de partes no almoxarifado usando mesma estratégia de Kanban - quando nível se aproximar do vermelho, deve-se emitir ordem de comprar para fornecedores.

Usar: Docker containeres para cada entidade (Depósito de produtos acabados, Fabricas, linhas, almoxarifado, fornecedores) Criar Buffer estoque onde Consumo faz CheckOut (decrementa) e Abastecimento faz CheckIn (incrementa). Todo buffer de materiais e produtos deve ser mostrado em tela com seu valor atual e COR. Toda mensagem de pedidos de reabastecimento e ordem de produção deve usar MQTT entre entidades.

Sugestão: desenhar solução para 1 fornecedor, 1 almoxarifado, 1 fábrica com1 linha e 1 produto com 53 partes e depois escalar para cenário do projeto

## Funcionamento do controle de estoque:
- Suporte para 3 tipos de STATUS do estoque: VERMELHO, AMARELO, VERDE. <br>
- Fornecedor envia 150 partes para almoxarifado quando requisitado.
- Almoxarifado envia 50 partes para fábrica quando requisitado.
- Níveis de estoque do almoxarifado: VERMELHO: estoque <= 50, AMARELO: estoque <= 100, VERDE: estoque > 100
- Fábrica envia 6 partes para linha quando requisitada
- Níveis de estoque da fábrica: VERMELHO: estoque <= 30, AMARELO: estoque <= 40, VERDE: estoque > 40
- Níveis de estoque da linha: VERMELHO: estoque <= 3, AMARELO: estoque <= 5, VERDE: estoque > 100

## Como executar?

O projeto está utilizando docker para possibilitar a criação dos containers das entidades (fábrica, fornecedor, almoxarifado, etc).

1. Para criar os containers, se estiver no windows execute o arquivo ```script-windows.bat```. Se estiver no linux, execute o arquivo ```script-linux.sh```
2. Para rodar os containers siga o passo abaixo (Precisa obrigatóriamente ser executado na ordem especificada): <br>
  **Rode cada um dos containers em um terminal diferente para que seja possível ver as informações corretamente.** <br><br>
  **OBS: Antes de executar os comandos abaixo, se existirem containers da nossa aplicação que ainda estão rodando, pare a execução deles para não gerar interferência nos resultados. (Você pode executar os scripts de remoção ```script-remover-windows.bat``` ou ```script-remover-linux.sh``` para fazer isso)**   
  2.1. ```docker run -it  container-vog-fornecedor``` => Ao executar, vai aparecer a mensagem de conexão do MQTT <br>
  2.2. ```docker run -it container-vog-almoxarifado``` => Ao executar, vai aparecer a mensagem de conexão do MQTT <br>
  2.3. ```docker run -it container-vog-fabrica``` => Ao executar, vai aparecer mensagem de conexão e quantidade de cada peça no estoque. <br>
  2.4. ```docker run -it container-vog-linha``` => Ao executar, vai ser preciso informar no terminal o número dessa linha: Digite 1 para que a linha fique com esse número. <br>
  2.5. ```docker run -it container-vog-ordem``` => Ao executar, vai ser preciso informar o número da fábrica, o número da linha e a quantidade de produtos para serem fabricados. <br>

   Quando inserir as informações da ordem de produção e apertar enter, vai começar a fabricar os produtos e as informações vão ser mostradas respectivamente em cada um dos terminais onde os containers foram executados. <br>
   
   Assim, para realizar mais ordens de produção, basta indicar o número da fábrica, número da linha e quantidade de produtos novamente.
