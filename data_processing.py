import os
import csv
import json


def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        result = json.load(f)
    return result


def save_csv(rows, header, path):
    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(rows)


def get_or_create_node_id(name, field):
    global nodes
    node_id = nodes[field].get(name)
    if node_id is None:
        num_id = len(nodes[field].keys()) + 1
        node_id = f'{field[0].upper()}{num_id}'
        nodes[field][name] = node_id

    return node_id


def create_nodes(field):
    global nodes
    global nodes_list

    for label in nodes[field]:
        nodes_list.append([nodes[field][label], label, field])


if __name__ == "__main__":
    main_dir = 'data'  # path to directory
    nodes = {
        "human": {},
        "state": {},
        "education": {},
        "party": {}
    }
    edges = []
    for filename in os.listdir(main_dir):
        filepath = os.path.join(main_dir, filename)
        data = read_json(filepath)
        if data['state'] not in ['CA', 'CO', 'FL', 'IL', 'MO', 'NY', 'TX', 'MI']:
            continue

        # party = get_or_create_node_id(data['party'].lower(), 'party')
        party = data['party'].lower()
        if party == 'republican':
            state = get_or_create_node_id(data['state'], 'state')
            human = get_or_create_node_id(data['name'], 'human')

            edges.append([f'{party}-{state}', party, state, 1, 'party-state'])
            edges.append([f'{state}-{human}', state, human, 1, 'state-human'])

            if data.get('VoteSmart') and data['VoteSmart'].get('Education'):
                education_weight = 1 / len(data['VoteSmart']['Education'])
                for item in data['VoteSmart']['Education']:
                    if not item.get('institution'):
                        continue
                    education = get_or_create_node_id(item['institution'], 'education')
                    edges.append([f'{human}-{education}', human, education, education_weight, 'human-education'])

    save_csv(edges, ['Id', 'Source', 'Target', 'Weight', 'Description'], 'graphs/republican/Edges.csv')

    nodes_list = []
    # create_nodes('party')
    create_nodes('state')
    create_nodes('education')
    create_nodes('human')

    save_csv(nodes_list, ['Id', 'Label', 'Description'], 'graphs/republican/Nodes.csv')
