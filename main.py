import rdflib

def add_compatibility(g):
    query = f"""
    PREFIX ex: <http://example.org/univ#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?cpu ?mb WHERE {{
        ?cpu ex:UsaSocket ?s .
        ?mb ex:TemSocket ?s .
    }}
    """
    results = g.query(query)
    EX = rdflib.Namespace("http://example.org/univ#")
    for cpu_c, mb_c in results:
        # Adicicionando no grafo a relacao simetrica de compatibilidade entre CPU e Placa-Mae
        g.add((cpu_c, EX.compativelCom, mb_c))
        g.add((mb_c, EX.compativelCom, cpu_c))
    return g


def get_nome(g, componente):
    # O nome de cada componente inclui a fabricante e o nome do modelo
    query = f"""
    PREFIX ex: <http://example.org/univ#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?fabricante WHERE {{
        ?fabricante ex:fabrica ex:{componente} .
    }}
    """
    results = g.query(query)
    for row in results:
        fabricante = row.fabricante.split('#')[-1]
        nome_completo = f"{fabricante.replace('_', ' ')} {componente.replace('_', ' ')}"
        # Retorna o primeiro resultado encontrado, ja que so existe um fabricante por componente
        return nome_completo


def get_components(g, preferencia_marca, preferencia_desempenho):
    marca_cpu, marca_mb, marca_indesejada = preferencia_marca
    nivel, nucleos, threads = preferencia_desempenho
    query = f"""
    PREFIX ex: <http://example.org/univ#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?cpu ?mb WHERE {{
        ?cpu a ex:CPU .
        ?mb a ex:MB .
        ?cpu ex:compativelCom ?mb .
        ?cpu ex:ehNivel ?nivel .
        ?mb ex:ehNivel ?nivel .
        OPTIONAL {{ ?cpu ex:temNucleos ?cpuNucleos . }}
        OPTIONAL {{ ?cpu ex:temThreads ?cpuThreads . }}
        
        {"?fcpu ex:fabrica ?cpu . ?fmb ex:fabrica ?mb . FILTER regex(str(?fcpu), '" + marca_cpu + "', 'i') ." if marca_cpu else ""}
        {"FILTER regex(str(?fmb), '" + marca_mb + "', 'i') ." if marca_mb else ""}
        {"FILTER regex(str(?nivel), '" + nivel + "', 'i') ." if nivel else ""}
        {f"FILTER NOT EXISTS {{ ?fcpu ex:fabrica ?cpu . FILTER regex(str(?fcpu), '{marca_indesejada}', 'i') . }} ." if marca_indesejada else ""}
        {f"FILTER NOT EXISTS {{ ?fmb ex:fabrica ?mb . FILTER regex(str(?fmb), '{marca_indesejada}', 'i') . }} ." if marca_indesejada else ""}
        {f"FILTER(?cpuNucleos >= {int(nucleos)}) ." if nucleos and nucleos.isdigit() else ""}
        {f"FILTER(?cpuThreads >= {int(threads)}) ." if threads and threads.isdigit() else ""}
    }}
    """

    results = g.query(query)
    clnd_rslts = []
    for row in results:
        cpu = row.cpu.split('#')[-1]
        mb = row.mb.split('#')[-1]
        clnd_rslts.append((cpu, mb))
    return clnd_rslts

def get_upgrades(g, cpu, mb):
    # Lista todos os componentes compativeis com a placa-mae melhores que a CPU atual em cores/threads
    s1 = f"ex:{cpu}" if cpu else "?cpu"
    s2 = f"ex:{mb}" if mb else "?mb"
    query = f"""
    PREFIX ex: <http://example.org/univ#>
    
    SELECT ?upgradeCPU ?newCores ?newThreads
    WHERE {{
        {s2} ex:TemSocket ?socketUser .
        
        {{
            SELECT ?coresUser ?threadsUser ?socketUser
            WHERE {{
                BIND(ex:{cpu} AS ?cpuAtual)
                
                ?cpuAtual ex:temNucleos ?coresUser ;
                         ex:temThreads ?threadsUser ;
                         ex:UsaSocket ?socketUser .
            }}
        }}
        
        ?upgradeCPU a ex:CPU ;
                    ex:UsaSocket ?socketUser ;
                    ex:temNucleos ?newCores ;
                    ex:temThreads ?newThreads .
        
        FILTER(?newCores > ?coresUser || ?newThreads > ?threadsUser)
        FILTER(?upgradeCPU != ex:{cpu})
    }}
    ORDER BY DESC(?newCores) DESC(?newThreads)
    """
    results = g.query(query)
    upgrades = []
    for row in results:
        upgrade_cpu = row.upgradeCPU.split('#')[-1]
        upgrades.append(upgrade_cpu)
    return upgrades
    

def check_comp(g, cpu, mb):
    # Verifica se a CPU e a Placa-Mae sao compativeis usando a relacao de compatibilidade
    s1 = f"ex:{cpu}" if cpu else "?cpu"
    s2 = f"ex:{mb}" if mb else "?mb"
    select = s1 + " ex:compativelCom " + s2 + " ."
    query = f"""
    PREFIX ex: <http://example.org/univ#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?cpu ?mb WHERE {{
        {select}
    }}
    """
    results = g.query(query)
    return len(results) > 0

def listar_componentes_compatíveis(g, componente, tipo_componente):
    s = f"ex:{componente}" if componente else "?comp"
    if tipo_componente == "CPU":
        select = s + " ex:compativelCom ?mb ."
        var_name = "mb"
    else:
        select = "?cpu ex:compativelCom " + s + " ."
        var_name = "cpu"
    query = f"""
    PREFIX ex: <http://example.org/univ#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?{var_name} WHERE {{
        {select}
    }}
    """
    results = g.query(query)
    componentes_compatíveis = []
    for row in results:
        comp = getattr(row, var_name).split('#')[-1]
        componentes_compatíveis.append(comp)
    return componentes_compatíveis


# Programa Principal
g = rdflib.Graph()
g.parse("meugrafo.ttl", format="turtle")
g = add_compatibility(g)
modo = int(input("Modo (1 para Montagem, ou 2 para Checagem, ou 3 para recomendar uma peça, ou 4 para listar possiveis upgrades, ou qualquer outro número para ajuda): "))
match modo:
    case 1:
        preferencia_marca_cpu = input("Você tem preferência por alguma marca de CPU (Intel, AMD)? (Deixe vazio se não tiver): ")
        preferencia_marca_mb = input("Você tem preferência por alguma marca de Placa-Mae (Asus, Gigabyte, MSI)? (Deixe vazio se não tiver): ")
        marcas_indesejadas = input("Você tem alguma marca que não gostaria de incluir na busca? (Deixe vazio se não tiver): ")
        preferencia_marca = (preferencia_marca_cpu, preferencia_marca_mb, marcas_indesejadas)
        
        preferencia_nivel = input("Você tem preferência por algum nível de desempenho (Entrada, Intermediário, Avançado, Premium)? (Deixe vazio se não tiver): ")
        preferencia_nucleos = input("Você tem preferência por um número mínimo de núcleos? (Deixe vazio se não tiver): ")
        preferencia_threads = input("Você tem preferência por um número mínimo de threads? (Deixe vazio se não tiver): ")
        preferencia_desempenho = (preferencia_nivel, preferencia_nucleos, preferencia_threads)
        configs = get_components(g, preferencia_marca, preferencia_desempenho)
        if not configs:
            print("Nao temos nenhuma configuracao que cumpra com suas necessidades.")
        for i, config in enumerate(configs):
            cpu = config[0]
            mb = config[1]
            print(f"PC {i + 1} - CPU: {get_nome(g, cpu)} {get_nome(g, mb)};")

    case 2:
        # Trocar espacos por underline para casar com os nomes no grafo
        cpu = input("Nome do modelo de CPU: ").replace(' ', '_')
        mb = input("Nome do modelo de Placa-Mae: ").replace(' ', '_')
        eh_compativel = check_comp(g, cpu, mb)
        print(  "Esses componentes são compativeis!" 
                if eh_compativel else \
                "Sua montagem não é compatível!"
                )
        
    case 3:
        cpu = input("Nome do modelo de CPU (deixe vazio se quiser recomendação baseada na Placa-Mãe): ").replace(' ', '_')
        mb = input("Nome do modelo de Placa-Mãe (deixe vazio se quiser recomendação baseada na CPU): ").replace(' ', '_')
        if not cpu and not mb:
            print("Por favor, informe ao menos um componente para recomendação.")
            exit()
        componente = cpu if cpu else mb
        tipo_componente = "CPU" if cpu else "MB"
        recommendations = listar_componentes_compatíveis(g, componente, tipo_componente)
        if not recommendations:
            print("Nenhum componente compativel encontrado.")
        else:
            print("Componentes compativeis:")
            for rec in recommendations:
                print(f"- {get_nome(g, rec)}")

    case 4:
        mb = input("Nome do modelo de Placa-Mãe para listar possíveis upgrades: ").replace(' ', '_')
        cpu = input("Nome do modelo de CPU atual (para basear o nivel de desempenho): ").replace(' ', '_')
        upgrades = get_upgrades(g, cpu, mb)
        if not upgrades:
            print("Nenhum componente compativel encontrado para upgrade.")
        else:
            print("Componentes compativeis para upgrade:")
            for upg in upgrades:
                print(f"- {get_nome(g, upg)}")
    
    case _:
        print("Modo 1: Montagem - Receba sugestões de configurações de CPU e Placa-Mãe baseadas em suas preferências de marca e desempenho.")
        print("Modo 2: Checagem - Verifique se uma CPU e uma Placa-Mãe são compatíveis.")
        print("Modo 3: Recomendação - Obtenha recomendações de componentes compatíveis com base em uma CPU ou Placa-Mãe específica.")
        print("Modo 4: Listar Upgrades - Liste todos os componentes compatíveis para sua placa-mãe, baseada no nivel de desempenho da CPU atual.")
