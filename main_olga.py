import typer
import requests
import json
import re

app = typer.Typer(help="CLI para explorar empregos do itjobs.pt")

url = "https://api.itjobs.pt/job/list.json"
api_key = "5ead20f487935ddbab9b3f084acdbf63"
limite = 2

@app.command(name="top")
def top_empregos(n: int = typer.Argument(..., help="Número de empregos a listar")):
    offset = 0
    total_mostrado = 0
    resultado_final = []

    while total_mostrado < n:
        resposta = requests.get(
            url, params={"api_key": api_key, "limit": limite, "offset": offset}
        )

        if resposta.status_code == 200:
            dados = resposta.json()
            empregos = dados.get("jobs", [])

            if not empregos:
                typer.echo("Sem mais empregos disponíveis.")
                break

            for emprego in empregos:
                resultado_final.append(emprego)
                total_mostrado += 1
                if total_mostrado >= n:
                    break

            offset += limite
        else:
            typer.echo(f"Erro ao obter dados da API. Código: {resposta.status_code}")
            break

    typer.echo(json.dumps(resultado_final, indent=2))


if __name__ == "__main__":
    app()


@app.command(name="regime")

def regime_trabalho(id: int = typer.Argument(..., help="ID do emprego")):
    url1= "https://api.itjobs.pt/job/get.json"
    resposta = requests.get(url1, params={"api_key": api_key,"id":id})
    if resposta.status_code == 200:
        dados = resposta.json()
        allow_remote = dados.get("allowRemote", False)
        corpo = dados.get("corpo", "").lower()

        if allow_remote:
            typer.echo("Remoto")
        elif re.search(r"remoto|teletrabalho", corpo):
            typer.echo("Remoto (inferido pelo corpo do anúncio)")
        elif re.search(r"híbrido|hibrido", corpo):
            typer.echo("Híbrido")
        elif re.search(r"presencial|no escritório|on-site", corpo):
            typer.echo("Presencial")
        else:
            typer.echo("Outro / Não especificado")

    else:
        typer.echo(f"Erro ao obter dados da API. Código: {resposta.status_code}")


            


