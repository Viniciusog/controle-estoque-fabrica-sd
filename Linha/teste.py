import ast
myStr = "Linha/1/20"
print(myStr.split('/')[2])

outra_str = "[1, 2, 3, 5, 8]"
minha_str = "{'a':1, 'b':2}"
meu_dicionario = ast.literal_eval(minha_str)
print(meu_dicionario['b'])

meu_array = ast.literal_eval(outra_str)
print(meu_array[3])


ok = [1,2, 3, 4, 5]
msg = f"Fabrica/Linha/{1}/{str(ok)}"
print(msg)