# Job_API_explorer

Análise do conteúdo da API do itjobs.pt e Webscraping do site pt.teamlyzer.com. Criação de uma CLI (Command Line Interface).

Ficheiros: projetoFinal.py (código com os comandos listados abaixo); RelatórioTP1_Job_API_Explorer (Relatório em pdf sobre comandos relativos à API ItJobs); RelatórioTP2_Teamlyzer (Relatório em pdf sobre comandos 

Tecnologias Usadas: Python (módulos typer, requests, json, re, datetime, BeautifulSoup,csv)

Funcionalidades:

-Comando "dump" que cria ou atualiza o ficheiro "empregos.json". Objetivo - evitar múltiplas requisições à API e consecutivo atingimento da threshold da API.
  Ex: python main.py dump
  
-Comando "top" que recebe como argumento um inteiro n - quantidade de propostas de emprego mais recentes que desejamos visualizar. Devolve ID do emprego, nome da oferta, empresa e data de publicação.
  Ex: python main.py top 5

-Comando "search" - lista os anúncios de emprego part-time publicados por uma determinada empresa numa localidade específica, com base nos dados do ficheiro empregos.json. Permite limitar o número de resultados devolvidos e exportar a informação (título, empresa, descrição, data de publicação, salário e localização) para CSV.
Ex: python main.py search "Lisboa" "Deloitte" 5 --csv
  
-Comando "regime" que recebe como argumento um ID de um emprego. Devolve o regime associado a esse emprego - presencial/híbrido/remoto.
  Ex: python main.py regime 506847
  
-Comando "procurar" - sem utilidade para o utilizador. Utilizado por nós como um comando intermédio para obter descrições de anúncios que tivessem as seguintes expressões: "Experiência", "Conhcecimentos", "Forte", "valoriza", "Domínio", "skills" ,"experience", "exprertise","looking for". Motivo: redução do campo de análise de expressões regulares associadas a skills, uma vez que nem todos os anúncios incluem as skills pretendidas. Objetivo: criação de uma lista concreta de skills (tecnológicas e comportamentais). O resultado desta análise é utilizado no comando seguinte.
  Ex: python main.py procurar
  
-Comando "skills" - recebe como argumentos duas datas no formato "AAAA-MM-DD" e devolve a contagem de skills que aparecem nos anúncios entre essas datas.
  Ex:python main.py skills 2025-11-10 2025-11-15

-Comando "get" - recebe como argumento um jobID e devolve informação detalhada sobre o anúncio de emprego, consultando a API do ITJobs.pt e dados complementares da empresa obtidos no Teamlyzer (rating, descrição e benefícios). Permite opcionalmente exportar os resultados para CSV.
Ex: python main.py get 506847 --csv 

-Comando "statistics" - realiza a contagem de vagas por zona e tipo/nome de posição a partir de um ficheiro JSON de anúncios de emprego. Gera um ficheiro CSV com a distribuição das vagas por região e função.
Ex: python main.py statistics

-Comando "list_skills" - recebe como argumento o nome de uma profissão e devolve as 10 competências mais frequentes associadas a essa função, com base na informação disponível no Teamlyzer. Os resultados são apresentados em JSON no terminal e podem ser opcionalmente exportados para CSV.
Ex: python main.py list_skills "Data Scientist" --csv


Autores:
Marta Rocha 
Olga Marynych
Filipe Araújo



