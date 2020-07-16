# -*- coding: utf-8 -*-

import json

# codigo para criar arquivo de opcoes options.json
# Gera um template para que o bot apresente estas opcoes para o usuario

# Gerador de Opcoes para Bot 1.0
print (f"Gerador de opcoes para bot 2.0\n")

# Se nao for valor inteiro, sai
try:
    z=int(input ("Quantas opcoes deseja criar? "))
except:
    quit()
if z<=0:
    quit()

# variaveis
o=0
op=list()

# Laço para perguntar questões e montar a config
while o<z:
    print (f'\nOpcao {o+1}\n')
    cod=input ("Codigo da opcao: ")
    title=input ("Titulo da opcao: ")
    tag=input ("Palavras chave da opcao (separadas por espacos): ")
    desc=input ("Descricao da opcao: ")
    ad=input ("É comando de administrador? responda sim ou nao: ")
    if "sim" in ad:
        admin=True
    else:
        admin=False

    t=input ("tem parametros? responda sim ou nao: ")

    if "sim" in t:
        params=input ("Coloque os nomes dos parametros separados por virgulas: ")
        var= { "tag": tag, "title":title, "option":int(cod), "desc":desc, "admin":admin, "req":True, "params":params }
    
    if not "sim" in t:
        var= { "tag": tag, "title":title, "option":int(cod), "desc":desc, "admin":admin, "req":False }
    
    op.append(var)
    o+=1

# Gera config
config={"opcoes":op}
arquivo="options_new.json"

# Salva
print ("Gravando...")
try:
    # Salva com LF (Unix like para funcionar no Windows e no Unix (variavel newline))
    # Salva com encoding UTF-8 para funcionar caracteres especiais no Unix
    with open(arquivo, 'w', encoding="utf-8", newline='\n') as file:
        json.dump(config, file, indent=4, sort_keys=True, ensure_ascii=False)

    print ("ok")
except:
    print ("Erro de gravacao")