# Job_API_explorer
Análise do conteúdo da API do itjobs.pt. Criação de uma CLI (Command Line Interface).

Tecnologias Usadas: Python (módulos typer, requests, json, re e datetime)

Funcionalidades:

-Comando "dump" que cria ou atualiza o ficheiro "empregos.json". Objetivo - evitar múltiplas requisições à API e consecutivo atingimento da threshold da API.
  Ex: python main.py dump
  
-Comando "top" que recebe como argumento um inteiro n - quantidade de propostas de emprego mais recentes que desejamos visualizar. Devolve ID do emprego, nome da oferta, empresa e data de publicação.
  Ex: python main.py top 5
  
-Comando "regime" que recebe como argumento um ID de um emprego. Devolve o regime associado a esse emprego - presencial/híbrido/remoto.
  Ex: python main.py regime 506847
  
-Comando "procurar" - sem utilidade para o utilizador. Utilizado por nós como um comando intermédio para obter descrições de anúncios que tivessem as seguintes expressões: "Experiência", "Conhcecimentos", "Forte", "valoriza", "Domínio", "skills" ,"experience", "exprertise","looking for". Motivo: redução do campo de análise de expressões regulares associadas a skills, uma vez que nem todos os anúncios incluem as skills pretendidas. Objetivo: criação de uma lista concreta de skills (tecnológicas e comportamentais). O resultado desta análise é utilizado no comando seguinte.
  Ex: python main.py procurar
  
-Comando "skills" - recebe como argumentos duas datas no formato "AAAA-MM-DD" e devolve a contagem de skills que aparecem nos anúncios entre essas datas.
  Ex:python main.py skills 2025-11-10 2025-11-15


Autores:
Marta Rocha 
Olga Marynych
Filipe Araújo



