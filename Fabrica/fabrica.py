class Produto:
    def __init__(self, identificador, quantidade_partes):
        self.identificador = identificador
        self.quantidade_partes = quantidade_partes
        
    def get_quantidade_partes(self):
        return self.quantidade_partes
        
    def get_identificador(self):
        return self.identificador
    
    def set_quantidade_partes(self, qtd_partes):
        self.quantidade_partes = qtd_partes

    def imprimir(self):
        print("-----Produto-----")
        print("Identificador: " 
              + str(self.get_identificador()) + ", Qtd Partes: " 
              + str(self.get_quantidade_partes()) + "\n")

produto = Produto(1, 20)
produto.imprimir()

produto.set_quantidade_partes(30)
produto.imprimir()

produto.set_quantidade_partes(40)
produto.imprimir()
