import typer
import requests
import json
import re
from datetime import datetime
import csv

app = typer.Typer()

# -------------------------------------------------------------------------------
# Subcomando statistics
statistics_app = typer.Typer()
app.add_typer(statistics_app, name="statistics")

@statistics_app.command(name="zone")
def statistics_zone(csv_file: str = typer.Option("statistics_zone.csv", "--csv", "-c", help="Nome do ficheiro CSV de saída")):
    """
    Contagem de vagas por região (zona) e tipo/nome da posição.
    Gera ficheiro CSV com colunas: Zona, Tipo de Trabalho, Nº de vagas
    """
    try:
        with open("empregos.json", "r", encoding="utf-8") as f:
            conteudo = json.load(f)
    except FileNotFoundError:
        typer.echo("Ficheiro 'empregos.json' não encontrado. Faz primeiro o dump da API.")
        raise typer.Exit(code=1)

    trabalhos = conteudo.get("results", [])
    contador = {}

    for t in trabalhos:
        locations = t.get("locations", [])
        zonas = [loc.get("name", "Desconhecida") for loc in locations] or ["Desconhecida"]
        tipo = t.get("title", "Não especificado")
        for zona in zonas:
            key = (zona, tipo)
            contador[key] = contador.get(key, 0) + 1

    lista_csv = [{"Zona": z, "Tipo de Trabalho": t, "Nº de vagas": n} for (z, t), n in contador.items()]
    lista_csv.sort(key=lambda x: (x["Zona"], x["Tipo de Trabalho"]))

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Zona", "Tipo de Trabalho", "Nº de vagas"])
        writer.writeheader()
        writer.writerows(lista_csv)

    typer.echo(f"Ficheiro de exportação '{csv_file}' criado com sucesso!")

# -------------------------------------------------------------------------------
# Configurações da API
url = "https://api.itjobs.pt/job/list.json"
user_agent = {'User-agent': 'Mozilla/5.0'}
api_key = "5ead20f487935ddbab9b3f084acdbf63"

# -------------------------------------------------------------------------------
@app.command(name="dump")
def dump():
    """Cria/atualiza o ficheiro empregos.json"""
    all_results = []
    page = 1

    try:
        while True:
            resposta = requests.get(url, headers=user_agent, params={
                "api_key": api_key,
                "page": page,
                "limit": 100
            })
            if resposta.status_code != 200:
                typer.echo(f"Erro na requisição (página {page}): {resposta.status_code} - {resposta.reason}")
                raise typer.Exit(code=1)

            dados = resposta.json()
            results = dados.get("results", [])
            if not results:
                break

            all_results.extend(results)
            page += 1

        final_data = {"total": len(all_results), "results": all_results}
        with open("empregos.json", "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)

        typer.echo("Arquivo 'empregos.json' criado/atualizado com sucesso!")

    except Exception as e:
        typer.echo(f"Erro inesperado: {str(e)}")
        raise typer.Exit(code=1)

# -------------------------------------------------------------------------------
@app.command(name="top")
def top(
    n: int = typer.Argument(..., help="Número de empregos a listar"),
    csv_file: str = typer.Option(None, "--csv", "-c", help="Nome do ficheiro CSV para exportar")
):
    """Lista os N trabalhos mais recentes e opcionalmente exporta para CSV"""
    try:
        with open("empregos.json", "r", encoding="utf-8") as f:
            conteudo = json.load(f)
    except FileNotFoundError:
        typer.echo("Ficheiro 'empregos.json' não encontrado. Faz primeiro o dump da API.")
        raise typer.Exit(code=1)

    trabalhos = conteudo.get("results", [])
    recentes = trabalhos[:n]

    lista_csv = []
    lista_terminal = []
    for t in recentes:
        empresa = t.get("company", {}).get("name", "Empresa desconhecida")
        titulo = t.get("title", "Sem título")
        data_publicacao = t.get("publishedAt", "")
        descricao = t.get("body", "")
        salario = t.get("salary", "")
        localizacao = t.get("location", "")
        id = t.get("id", "")

        item = {
            "ID da oferta": id,
            "Oferta de emprego": titulo,
            "Empresa": empresa,
            "Data da publicação": data_publicacao,
            "Descrição": descricao,
            "Salário": salario,
            "Localização": localizacao
        }
        lista_csv.append(item)
        lista_terminal.append({"ID da oferta": id, "Oferta de emprego": titulo, "Empresa": empresa, "Data da publicação": data_publicacao})

    print(json.dumps(lista_terminal, indent=4, ensure_ascii=False))

    if csv_file:
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Oferta de emprego", "Empresa", "Descrição", "Data da publicação", "Salário", "Localização"])
            writer.writeheader()
            for item in lista_csv:
                writer.writerow({k: item[k] for k in writer.fieldnames})
        typer.echo(f"CSV exportado com sucesso para '{csv_file}'")

# -------------------------------------------------------------------------------
@app.command(name="regime")
def regime_trabalho(id: int = typer.Argument(..., help="ID do emprego")):
    url1 = "https://api.itjobs.pt/job/get.json"
    resposta = requests.get(url1, headers=user_agent, params={"api_key": api_key, "id": id})

    if resposta.status_code == 200:
        vaga_emprego = resposta.json()
        descricao_vaga = vaga_emprego.get("body", "")

        hibrido = re.search(r"([Hh][íi]brido|[Hh]ybrid)", descricao_vaga)
        presencial = re.search(r"([Pp]resencial|[Oo]n-?site)", descricao_vaga)

        if vaga_emprego.get("allowRemote"):
            typer.echo("Remoto")
        elif hibrido:
            typer.echo("Híbrido")
        elif presencial:
            typer.echo("Presencial")
        else:
            typer.echo("Não identificado")
    else:
        print(f"Erro na requisição: {resposta.status_code} - {resposta.reason}")

# -------------------------------------------------------------------------------
def remove_html_tags(text):
    if not text:
        return ""
    text = re.sub(r'</p>', '  ', text)
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

@app.command(name="search")
def search(local: str, empresa: str, n: int, csv_out: bool = typer.Option(False, "--csv", help="Exportar para CSV")):
    try:
        with open("empregos.json", "r", encoding="utf-8") as f:
            conteudo = json.load(f)
    except FileNotFoundError:
        typer.echo("Ficheiro 'empregos.json' não encontrado. Faz primeiro o dump da API.")
        raise typer.Exit(code=1)

    trabalhos = conteudo.get("results", [])
    filtered = []

    for job in trabalhos:
        locations = job.get("locations", [])
        found_location = any(local.lower() in loc.get("name", "").lower() for loc in locations)
        if not found_location:
            continue

        company_name = job.get("company", {}).get("name", "")
        if empresa.lower() not in company_name.lower():
            continue

        types = job.get("types", [])
        part_time = any("part-time" in t.get("name", "").lower() for t in types)
        title = job.get("title", "").lower()
        body = job.get("body", "").lower()
        part_time_pattern = r"part[-\s]?time"
        if not part_time and (re.search(part_time_pattern, title) or re.search(part_time_pattern, body)):
            part_time = True

        if part_time:
            filtered.append(job)

    filtered = filtered[:n]

    if not filtered:
        typer.echo("Nenhum resultado encontrado.")
        raise typer.Exit()

    output_data = []
    for job in filtered:
        locations_list = [loc.get("name", "") for loc in job.get("locations", [])]
        locations_str = ", ".join(locations_list) if locations_list else ""

        output_data.append({
            "titulo": job.get("title", ""),
            "empresa": job.get("company", {}).get("name", ""),
            "descrição": remove_html_tags(job.get("body", "")),
            "data de publicação": job.get("publishedAt", ""),
            "salário": job.get("wage", ""),
            "localização": locations_str
        })

    if csv_out:
        with open("search_results.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=output_data[0].keys())
            writer.writeheader()
            writer.writerows(output_data)
        typer.echo("Resultados exportados para 'search_results.csv'")
    else:
        print(json.dumps(output_data, indent=4, ensure_ascii=False))

# -------------------------------------------------------------------------------
if __name__ == "__main__":
    app()
