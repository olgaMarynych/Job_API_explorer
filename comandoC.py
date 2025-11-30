from bs4 import BeautifulSoup
import requests
import json
import typer
import csv

app = typer.Typer()

@app.command(name="list_skills")
def list_skills(
    prof: str = typer.Argument(help="Profissão a analisar"),
    export_csv: bool = typer.Option(False, "--csv", help="Exportar resultados para ficheiro CSV")):

    user_agent = {'User-agent': 'Mozilla/5.0'}
    url = "https://pt.teamlyzer.com/companies/jobs?profession_role=" + prof + "&order=most_relevant"

    dados_profissao = requests.get(url, headers=user_agent)
    soup_profissao = BeautifulSoup(dados_profissao.text, 'lxml')

    contagem = {}

    skills = soup_profissao.find_all("div", {"class": "voffset2"})
    for s in skills:
        skill_element = s.find("a")
        if skill_element and skill_element.text:
            skill = skill_element.text
            if skill in contagem:
                contagem[skill] += 1
            else:
                contagem[skill] = 1

    contagem_ordenada = sorted(contagem.items(), key=lambda item: item[1], reverse=True)
    
    skills_formatadas = []
    for skill, count in contagem_ordenada[:10]:
        skills_formatadas.append({
            "skill": skill,
            "count": count
        })
    
    json_10 = json.dumps(skills_formatadas, indent=2, ensure_ascii=False)
    typer.echo(json_10)

    if export_csv:
        try:
            with open("top10_skills.csv", 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['profession', 'skill', 'count'])
                writer.writeheader()
                
                for skill_data in skills_formatadas:
                    writer.writerow({
                        'profession': prof,
                        'skill': skill_data['skill'],
                        'count': skill_data['count']
                    })
                
            typer.echo("✅ Dados exportados para 'top10_skills.csv'")
        except Exception as e:
            typer.echo(f"❌ Erro ao exportar para CSV: {e}", err=True)
if __name__ == "__main__":
    app()





