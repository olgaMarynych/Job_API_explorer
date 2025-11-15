import typer
import requests
import json
import re
from datetime import datetime

app = typer.Typer()

url = "https://api.itjobs.pt/job/list.json"
user_agent = {'User-agent': 'Mozilla/5.0'}
api_key = "5ead20f487935ddbab9b3f084acdbf63"

#------------------------------------------------------------------------------------------------------------------------------------
@app.command(name="dump")  #cria/atualiza o ficheiro "empregos.json, para evitar requisições consecutivas à API e respetivo bloqueio"
def dump():
    resposta = requests.get(url, headers=user_agent, params={"api_key": api_key})
    if resposta.status_code == 200:
        dados = resposta.json()
        with open("empregos.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        typer.echo("Arquivo 'empregos.json' criado/atualizado com sucesso!")
    else:
        typer.echo(f"Erro na requisição: {resposta.status_code} - {resposta.reason}")
        raise typer.Exit(code=1)


#-----------------------------------------------------------------------------------------------------------------------------------
@app.command(name="top")  #n empregos mais recentes publicados no site
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
        data_publicacao = t.get("publishedAt", "")
        id=t.get("id","")
        lista_titulos.append({"ID da oferta": id, "Oferta de emprego": titulo, "Empresa": empresa, "Data da publicação": data_publicacao})

    print(json.dumps(lista_titulos, indent=4, ensure_ascii=False))

#------------------------------------------------------------------------------------------------------------------------------------

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
    

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.command(name="procurar")  #comando intermédio para procurar descrições de anúncios com possível indicação de skills (nem todos os anúncios têm); 
#serve como um filtro intermédio
#a partir do resultado, criou-se uma lista de skills usada no comando seguinte (de contagem)
def procurar_palavras():
    try:
        with open("empregos.json", "r", encoding="utf-8") as f:
            conteudo = json.load(f)
    except FileNotFoundError:
        typer.echo("Ficheiro 'empregos.json' não encontrado. Faz primeiro o dump da API.")
        raise typer.Exit(code=1)

    trabalhos = conteudo.get("results", [])
    padrao = re.compile(r"(experiência|conhecimentos|forte|valoriza|domínio|skills|experience|expertise|looking\s+for)", re.IGNORECASE)

    encontrados = []

    for t in trabalhos:
        corpo = t.get("body", "")
        if padrao.search(corpo):
            encontrados.append(corpo)
    if encontrados:
        print(json.dumps(encontrados, indent=4, ensure_ascii=False))
    else:
        typer.echo("Nenhuma vaga com as palavras procuradas.")

        
#-----------------------------------------------------------------------------------------------------------------------------------------------------

@app.command(name="skills")
def contar_skills(data_inicial: str, data_final: str):
    """Conta skills entre duas datas"""
    try:
        dt_ini = datetime.strptime(data_inicial, "%Y-%m-%d")
        dt_fim = datetime.strptime(data_final, "%Y-%m-%d")
    except ValueError:
        typer.echo("Datas inválidas. Usa o formato YYYY-MM-DD.")
        raise typer.Exit(code=1)

    try:
        with open("empregos.json", "r", encoding="utf-8") as f:
            conteudo = json.load(f)
    except FileNotFoundError:
        typer.echo("Ficheiro 'empregos.json' não encontrado. Primeiro faz 'dump'.")
        raise typer.Exit(code=1)

    trabalhos = conteudo.get("results", [])
    contador = {}

    #lista deduzida a partir do resultado do comando anterior. Skills técnicas e comportamentais
    lista_skills = ["Linux","Red Hat","CentOS","Ubuntu","Virtualização","Proxmox","Storage Networking","NAS","SAN","iSCSI","DNS","Mail","DHCP","LDAP",
                    "Active Directory","SSL", "Scripting","Bash","Python","Apache","Nginx","Troubleshooting","Containers","Docker","Docker Swarm","Kubernetes",
                    "Veeam Backup","Zabbix","Ethernet","Routing","NAT","IPSec VPN", "VLAN","Java","JavaScript","CI/CD","RESTful APIs","Microservices","Git",
                    "SQL","MySQL","PostgreSQL","NoSQL","Redis","Django","Node.js", "iOS","Android","React Native","Mac OS","Ansible","Capistrano","Photoshop",
                    "Figma","VBA","MS Access","SQL Server","PHP","PowerBI","Firewalls Checkpoint", "Cisco","IPv4","IPv6","IPSec","MPLS","VXLAN","TCP/IP",
                    "Switching","Networking","Industry 4.0","MES software","Product Marketing","Frameworks","Workflows","Go-to-Market (GTM)","Connect IoT", 
                    "Data Platform", "Messaging frameworks","Storytelling","Product positioning","Messaging architectures","GTM playbooks",
                    "Competitive battlecards","Pitch decks","Objection handling guides", "ROI tools","Training","Workshops","Pitch libraries","Demo flows", 
                    "Proof-of-value materials","Dashboards","Content usage tracking","Message adoption","Enablement impact","Campaigns", "SaaS",
                    "Cloud infrastructure (AWS, Azure, GCP)","Infrastructure as Code (Terraform, Pulumi)","Backend development","TypeScript","GraphQL",
                    "REST APIs","Data engineering", "Databricks","Snowflake","ETL pipelines","Data modeling","Frontend engineering","DevOps","Monitoring",
                    "Security best practices","ECS","EKS","GKE","AKS","Serverless platforms", "AI/ML infrastructure","Data visualization","Tableau",
                    "Embedded systems","C","C++","Real time systems","Software architecture","Design patterns","Multithreading","Multiprocess applications", 
                    "Bash scripting","Communication technologies","Layer 2 and Layer 3 network applications","Cybersecurity concepts","Electronics",
                    "Laboratory instrumentation", "Version control systems","SVN","Microsoft Dynamics 365 (CRM)","Power Platform","CRM","Integration of systems",
                    "Automation of business processes","Sales","Contact Center", "Service Workspace","Management of access and data security","Agile methodologies",
                    "Technical planning tools","Spring Boot","Software development","Java backend development", "Angular","HTML","CSS","Bootstrap","APIs REST","Jira","Xray",
                    "Azure DevOps","Liderança","Gestão","Mentoring","Comunicação","Planeamento","Desenho","Análise","Inovação", "Colaboração","Trabalho em equipa",
                    "Flexibilidade","Proatividade","Dedicação","Integridade","Transparência","Confiança","Honestidade","Responsabilidade","Criatividade", "Problem-solving",
                    "Analytical mind","Communication skills","Collaboration","Leadership","Analytical skills","Problem solving","Creativity","Strategic thinking","Adaptability", 
                    "Fast learning","Ambition","Commitment","Focus on innovation","Dynamism","Autonomy","Teamwork","Organization","Attention to detail","Passion for learning",
                    "Bias for action", "Intellectual curiosity","Navigating ambiguity", "Planning"]

    # nota: \b representa "boundary", ou seja, o programa procura a palavra por inteiro (sem palavras parecidas); escape(s) - tratamento literal de cada caractere de s.
    lista_regex = {s: re.compile(r"\b" + re.escape(s) + r"\b", re.IGNORECASE) for s in lista_skills}

    for t in trabalhos:
        data_pub_str = t.get("publishedAt")
        if not data_pub_str:
            continue
        try:
            data_pub = datetime.strptime(data_pub_str.split(" ")[0], "%Y-%m-%d")
        except ValueError:
            continue

        if not (dt_ini <= data_pub <= dt_fim):
            continue

        corpo = t.get("body", "")
        for skill, rgx in lista_regex.items():
            if rgx.search(corpo):
                contador[skill] = contador.get(skill, 0) + 1

    if contador:
        print(json.dumps(contador, indent=4, ensure_ascii=False))
    else:
        typer.echo("Nenhuma skill encontrada no intervalo de datas indicado.")

if __name__ == "__main__":
    app()

