import re
import itertools
from collections import Counter
import csv
import requests
from bs4 import BeautifulSoup
import os

group_3d = ['Ti', 'Co', 'Fe', 'Co', 'Cu', 'Mn', 'Ni']
group_5d = ['Hf', 'Ta', 'W', 'Re', 'Os', 'Ir']
last_elements = ['B', 'Br']
original_elements = ['Ti', 'Co', 'Fe', 'Cu', 'Mn',
                     'Ni', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'B']


def parse_formula(formula):
    pattern = r'([A-Z][a-z]*)(\d*)'
    matches = re.findall(pattern, formula)
    elements_counts = [(element, int(count) if count else 1)
                       for element, count in matches]
    return elements_counts


def tuple_to_formula(formula_tuple, original_order):
    combined_counts = Counter()

    for element_tuple in formula_tuple:
        element_count = Counter(element_tuple)
        combined_counts.update(element_count)

    formula = []
    for element in original_order:
        if element in combined_counts:
            count = combined_counts[element]
            if count > 1:
                formula.append(f"{element}{count}")
            else:
                formula.append(element)

    return ''.join(formula)


def get_combinations(element, count, is_first):
    if element in ['B', 'Br']:
        return [(element,) * count]

    if is_first:
        combinations = []
        for comb in itertools.combinations_with_replacement(group_3d + group_5d, count - 1):
            for group_3d_elem in group_3d:
                combinations.append((group_3d_elem,) + comb)
    else:
        combinations = list(itertools.combinations_with_replacement(
            group_3d + group_5d, count))

    return combinations


def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            contents = file.read()
            return contents
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def read_file_exclude_first_line(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()[1:]
    return [line.strip() for line in lines]


poscar_start = '''Titanium cobalt boride (3/5/2)
1.0
        8.4890003204         0.0000000000         0.0000000000
        0.0000000000         8.4890003204         0.0000000000
        0.0000000000         0.0000000000         3.0380001068
'''

poscar_end = '''
Cartesian
     0.000000000         0.000000000         0.000000000
     4.244500160         4.244500160         0.000000000
     2.775902987         7.020403385         0.000000000
     5.713097095         1.468596816         0.000000000
     1.468596816         2.775902987         0.000000000
     7.020403385         5.713097095         0.000000000
     0.000000000         4.244500160         1.519000053
     4.244500160         0.000000000         1.519000053
     1.884558082         0.577252030         1.519000053
     6.604442120         7.911747932         1.519000053
     7.911747932         1.884558082         1.519000053
     0.577252030         6.604442120         1.519000053
     2.359941959         4.821752548         1.519000053
     6.129058361         3.667248011         1.519000053
     4.821752548         6.129058361         1.519000053
     3.667248011         2.359941959         1.519000053
     0.976235032         5.220735073         0.000000000
     7.512765408         3.268265009         0.000000000
     3.268265009         0.976235032         0.000000000
     5.220735073         7.512765408         0.000000000'''


def generate_cif_from_poscar(poscar):
    session = requests.Session()

    query_url = 'https://uspex-team.org/online_utilities/poscar2cif/'

    payload = {
        'input_poscar': poscar,
        'tolerance': 0.02
    }

    response = session.post(query_url, data=payload)

    if response.status_code != 200:
        return f"Query failed with status code {response.status_code}"

    return response.text


def createCombinations(formula):
    res = parse_formula(formula)
    file_name = formula + '_structured_formula_combinations.csv'
    combinations_per_element = []
    for idx, (element, count) in enumerate(res):
        is_first_element = (idx == 0)
        element_combinations = get_combinations(
            element, count, is_first_element)
        combinations_per_element.append(element_combinations)
    all_formula_combinations = list(
        itertools.product(*combinations_per_element))
    structured_formula_combinations = [
        tuple_to_formula(formula_combo, original_elements)
        for formula_combo in all_formula_combinations]
    unique_formulas = set()
    for formula in structured_formula_combinations:
        unique_formulas.add(formula)
    os.makedirs('./output', exist_ok=True)
    with open('./output/'+file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Formula'])
        for formula in unique_formulas:
            writer.writerow([formula])
    msg = f"Saved {len(unique_formulas)} unique formulas to " + file_name + " in output folder!"
    print(msg)
    return msg, file_name

def createPOSCARs(original_poscar_file, combinations_file):
    combinations = read_file_exclude_first_line("./output/"+ combinations_file)
    for formula in combinations:
        parsed_formula = parse_formula(formula)
        element_line = ""
        count_line = ""

        for i in range(len(parsed_formula)):
            element_line += ("   " + parsed_formula[i][0])
            count_line += ("   " + str(parsed_formula[i][1]*2))
        new_poscar = poscar_start + element_line + '\n' + count_line + poscar_end
        file_path = './output/' + formula + " POSCAR"
        with open(file_path, 'w') as file:
            file.write(new_poscar)
    msg = f"Saved {len(combinations)} POSCARs to output folder!"
    print(msg)
    return msg

def generateCIFs(formula, poscar):
    res = generate_cif_from_poscar(poscar)
    res_soup = BeautifulSoup(res, 'html.parser')
    textarea = res_soup.find('textarea', {'name': 'f_cif'})
    if textarea:
        textarea_text = textarea.get_text()
        textarea_text = textarea_text.replace(
            "_cell_length_b       3.03800", "_cell_length_b       8.48900")
        textarea_text = textarea_text.replace(
            "_cell_length_c       8.48900", "_cell_length_c       3.03800")
        textarea_text = textarea_text.replace("x,y,z", "z,x,y")
        textarea_text = textarea_text.replace("-x,y,-z", "-z,-x,y")
        textarea_text = textarea_text.replace("-x,-y,-z", "-z,-x,-y")
        textarea_text = textarea_text.replace("x,-y,z", "z,x,-y")
        print(textarea_text)
        print("Textarea found and parsed!")
        file_path = './output/' + formula + '.cif'

        with open(file_path, 'w') as file:
            file.write(textarea_text)

        print(f"Textarea content has been saved to {file_path}")
    else:
        print("Textarea not found!")


# Process:
# Step 1: Create all formulas
# Step 2: Create all poscars
# Step 3: Generate CIFs files from poscars
# Step 4: Featurize with jarvis using cif files

# Outputs:
# CSV File with all correct records from ICSD, CIFs and Jarvis Features
