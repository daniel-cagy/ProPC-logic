
import rdflib


def is_valid(system: dict[str, str]) -> tuple[bool, str | None]:
    cpu = system["CPU"]
    mb = system["Motherboard"]
    psu = system["PSU"]
    if not is_compatible(cpu, mb):
        return False, "Your CPU and Motherboard are not compatible."
    system_tdp = TDP(cpu) + TDP(mb)
    if power(psu) < system_tdp * 1.1:
        return False, "Your power suplier is insufficient."
    return True, None


def is_compatible(cpu: str, mb: str) -> bool:
    return (cpu, "compatibleWith", mb) in g


def TDP(component: str) -> int:
    return g.value(subject=component, predicate="hasTDP").toPython()


def power(psu: str) -> int:
    return g.value(subject=psu, predicate="hasPower").toPython()


def get_choice(*choices) -> str:
    for i, option in enumerate(choices):
        print(f"{i + 1}. {option}")
    choice_i = int(input("Choice: ")) - 1
    return choices[choice_i]


def get_available_cpu_families(manufacturer: str) -> list[str]:
    q = g.query(f"""
                PREFIX ex: <http://example.org/univ#>
                SELECT DISTINCT ?cpu_family WHERE {{
                    ex:{manufacturer} ex:manufacturesFamily ?cpu_family .
                }}
                """,
    )
    return [row["cpu_family"].split('#')[-1] for row in q]


def get_available_cpus(cpu_family: str) -> list[str]:
    q = g.query(f"""
                PREFIX ex: <http://example.org/univ#>
                SELECT DISTINCT ?cpu WHERE {{
                    ?cpu ex:belongsToFamily ex:{cpu_family} .
                }}
                """,
    )
    return [row["cpu"].split('#')[-1] for row in q]


def get_available_components(manufacturer: str) -> list[str]:
    q = g.query(f"""
                PREFIX ex: <http://example.org/univ#>
                SELECT DISTINCT ?comp WHERE {{
                    ex:{manufacturer} ex:manufactures ?comp .
                }}
                """,
    )
    return [row["comp"].split('#')[-1] for row in q]



g = rdflib.Graph()
g.parse("ProPC-ontology.ttl")

if __name__ == "__main__":
    print("--- CPU ---")
    print("Pick your CPU manufacturer:")
    manufacturer = get_choice("Intel", "AMD")
    print(f"Manufacturer chosen: {manufacturer}")
    cpu_families_option = get_available_cpu_families(manufacturer)
    print("Pick the family of your CPU:")
    cpu_family = get_choice(*cpu_families_option)
    print(f"CPU Family chosen: {cpu_family}")
    cpus = get_available_cpus(cpu_family)
    print("Pick your CPU:")
    cpu = get_choice(*cpus)
    print(f"CPU chosen: {cpu}")

    print("--- Motherboard ---")
    print("Pick your Motherboard manufacturer:")
    mb_manufacturer = get_choice("Asus", "Gigabyte", "MSI")
    print(f"Manufacturer chosen: {mb_manufacturer}")
    motherboards = get_available_components(mb_manufacturer)
    print("Pick your Motherboard:")
    motherboard = get_choice(*motherboards)
    print(f"Motherboard chosen: {motherboard}")

    print("--- PSU ---")
    print("Pick your PSU manufacturer:")
    psu_manufacturer = get_choice("CoolerMaster", "Corsair", "SeaSonic")
    print(f"Manufacturer chosen: {psu_manufacturer}")
    psus = get_available_components(psu_manufacturer)
    print("Pick your PSU:")
    psu = get_choice(*psus)
    print(f"PSU chosen: {psu}")

    system = {
        "CPU": cpu,
        "Motherboard": motherboard,
        "PSU": psu,
    }
    validation = is_valid(system)
    if validation[0]:
        print("Your system is valid!")
    else:
        print("Your system isn't valid!")
        print(validation[1])

