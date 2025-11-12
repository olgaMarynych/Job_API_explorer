import typer
import requests
import json
import re

app = typer.Typer(help="CLI para explorar empregos do itjobs.pt")

url = "https://api.itjobs.pt/job/list.json"
user_agent = {'User-agent': 'Mozilla/5.0'}
api_key = "5ead20f487935ddbab9b3f084acdbf63"
limite = 2

resposta = requests.get(url, headers=user_agent, params={"api_key": api_key})

if resposta.status_code == 200:
    dados = resposta.json()
    with open("empregos.json", "w", encoding="utf-8") as f:
        json.dump(dados, f)
    print("Arquivo 'empregos.json' criado com sucesso!")
else:
    print(f"Erro na requisição: {resposta.status_code} - {resposta.reason}")
    dados = {}


#------------------------------------------------------------------------------------------------------
@app.command(name="top")  # n empregos mais recentes publicados no site
def top(n: int):
    try:
        with open("empregos.json", "r", encoding="utf-8") as f:
            conteudo = json.load(f)
    except FileNotFoundError:
        typer.echo("Ficheiro 'empregos.json' não encontrado. Faz primeiro o dump da API.")
        raise typer.Exit(code=1)

    trabalhos = conteudo.get("results", [])
    recentes = trabalhos[:n]

    lista_titulos = []
    for t in recentes:
        empresa = t.get("company", {}).get("name", "Empresa desconhecida")
        titulo = t.get("title", "Sem título")
        lista_titulos.append({"Oferta de emprego": titulo, "Empresa": empresa})

    print(json.dumps(lista_titulos, indent=4, ensure_ascii=False))



@app.command(name="regime")
def regime_trabalho(id: int = typer.Argument(..., help="ID do emprego")):
    url1= "https://api.itjobs.pt/job/get.json"
    resposta = requests.get(url1, headers=user_agent, params={"api_key": api_key,"id":id})
    if resposta.status_code == 200:
        vaga_emprego = resposta.json()
        with open("empregos.json", "w", encoding="utf-8") as f:
            json.dump(vaga_emprego, f)
            print("Arquivo 'vaga_emprego.json' criado com sucesso!")
    else:
        print(f"Erro na requisição: {resposta.status_code} - {resposta.reason}")
        
    if vaga_emprego.get("allowRemote"):
        typer.echo("Remoto")
    else:
        typer.echo("Presencial")

if __name__ == "__main__":
    app()