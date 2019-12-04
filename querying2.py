import csv
from collections import defaultdict
import pandas as pd
import json
import sqlite3
import networkx as nx
# from tabulate import tabulate

DBPath = r"reg360_action_mapping.db"


def getClusterData(directive_filter, var):
    # df = pd.read_csv('static\cluster_output_after_labels2.csv', encoding='Latin-1')
    df = pd.read_excel('static\cluster_output_after_labels2.xlsx', encoding='Latin-1')
    if(directive_filter != 'All'):
        filtered_row_indexes = df['directive'] == directive_filter
        df = df[filtered_row_indexes]
    data = df.loc[:, ['group', 'topic', 'cluster','sentence']]
    if(var == 'none'):
        data['radius'] = 4
        data1 = data
    else:
        group_list=['group', 'topic', 'cluster','sentence']
        group_list.remove(var)
        # print(group_list)
        data1 = data.groupby(group_list)[var].agg('count').to_frame('radius').reset_index()
        # data1 = data.groupby(['group', 'topic', 'cluster', 'sentence']).topic.agg('count').to_frame('radius').reset_index()
    # print(data1.to_json(orient='records'))
    return data1.to_json(orient='records'), data1.group.nunique(), len(data1)


def ctree():
    # One of the python gems. Making possible to have dynamic tree structure.
    return defaultdict(ctree)


def build_leaf(name, leaf):
    # Recursive function to build desired custom tree structure
    res = {"name": name}
    # add children node if the leaf actually has any children
    if len(leaf.keys()) > 0:
        res["children"] = [build_leaf(k, v) for k, v in leaf.items()]
    return res


def makeJson(fileName):
    """ The main thread composed from two parts.
    First it's parsing the csv file and builds a tree hierarchy from it.
    Second it's recursively iterating over the tree and building custom
    json-like structure (via dict).
    And the last part is just printing the result.
    """
    tree = ctree()
    # NOTE: you need to have test.csv file as neighbor to this file
    with open(fileName) as csvfile:
        reader = csv.reader(csvfile)
        for rid, row in enumerate(reader):
            # skipping first header row. remove this logic if your csv is
            # headerless
            if rid == 0:
                continue
            # usage of python magic to construct dynamic tree structure and
            # basically grouping csv values under their parents
            leaf = tree[row[0]]
            for cid in range(1, len(row)):
                leaf = leaf[row[cid]]
    # building a custom tree structure
    res = []
    for name, leaf in tree.items():
        res.append(build_leaf(name, leaf))
    # printing results into the terminal

    data= {"name":"Regulation", "children":res }
    data = json.dumps(data)
    # print(data)
    return data


def makeJson2(fileName, col_list):
    """ The main thread composed from two parts.
    First it's parsing the csv file and builds a tree hierarchy from it.
    Second it's recursively iterating over the tree and building custom
    json-like structure (via dict).
    And the last part is just printing the result.
    """
    tree = ctree()
    df = pd.read_excel('static\cluster_output_after_labels2.xlsx', encoding='Latin-1')
    reader = df.loc[:, col_list]

    for rid, row in enumerate(reader):
        # skipping first header row. remove this logic if your csv is
        # headerless
        if rid == 0:
            continue
        # usage of python magic to construct dynamic tree structure and
        # basically grouping csv values under their parents
        leaf = tree[row[0]]
        for cid in range(1, len(row)):
            leaf = leaf[row[cid]]
    # building a custom tree structure
    res = []
    for name, leaf in tree.items():
        res.append(build_leaf(name, leaf))
    # printing results into the terminal

    data= {"name":"Regulation", "children":res }
    data = json.dumps(data)
    # print(data)
    return data


def get_action_data(text):
    data = pd.read_excel('static\INPUT_ACTION_ITEMS.xlsx', encoding='Latin-1')
    filtered_row_indexes = data['subject'] == text
    df = data[filtered_row_indexes].reset_index().loc[:, ['subject', 'relation', 'object']].drop_duplicates()
    flare = df_to_tree(df)
    return [flare]


def make_holistic_table():
    # df = pd.read_csv('static\cluster_output_after_labels2.csv', encoding='Latin-1')
    df = pd.read_excel('static\cluster_output_after_labels2.xlsx', encoding='Latin-1')

    filtered_row_indexes = df['directive'] == 'MIFID2'
    data1 = df[filtered_row_indexes]
    data1_1 = pd.DataFrame(data1)
    filtered_row_indexes = df['directive'] == 'GDPR'
    data2 = df[filtered_row_indexes]
    data2_2 = pd.DataFrame(data2)

    data1_1_1 = data1_1.groupby(['group', 'topic']).directive.agg('count').to_frame('MIFID2').reset_index()
    data2_2_2 = data2_2.groupby(['group', 'topic']).directive.agg('count').to_frame('GDPR').reset_index()

    result = pd.merge(data1_1_1, data2_2_2, how='outer', on=['group', 'topic'])

    pd_table = result.loc[:, ['group', 'topic', 'MIFID2', 'GDPR']].fillna(0)

    html_table = '<table><thead>'
    for col in pd_table.columns:
        if(col != 'group'):
            html_table += '<th>'+str(col)+'</th>'
    html_table += '</thead><tbody>'
    group_stack = []
    for index, row in pd_table.iterrows():
        if(row['group'] not in group_stack):
            group_stack.append(row['group'])
            if(index != 0):
                html_table += '</tbody>'
            html_table += '<tbody class="labels"><tr><td colspan="3"><label for="' + row['group'] + '">' + row[
                'group'] + '</label><input type="checkbox" name="' + row['group'] + '" id="' + row[
                              'group'] + '" data-toggle="toggle"></td></tr></tbody><tbody class=""><tr><td>'+row['topic']+'</td><td name="MIFID2~'+row['topic']+'">'+str(int(row['MIFID2']))+'</td><td name="GDPR~'+row['topic']+'">'+str(int(row['GDPR']))+'</td></tr>'
        else:
            html_table += '<tr><td>'+row['topic']+'</td><td name="MIFID2~'+row['topic']+'">'+str(int(row['MIFID2']))+'</td><td name="GDPR~'+row['topic']+'">'+str(int(row['GDPR']))+'</td></tr>'
    html_table += '</tbody></tbody></table>'

    # html_table = pd_table.to_html()

    return html_table


def getSentence(directive,topic):
    # df = pd.read_csv('static\cluster_output_after_labels2.csv', encoding='Latin-1')
    df = pd.read_excel('static\cluster_output_after_labels2.xlsx', encoding='Latin-1')
    filtered_row_indexes_1 = df['directive'] == directive
    filtered_row_indexes_2 = df['topic'] == topic
    data = df[filtered_row_indexes_1 & filtered_row_indexes_2]
    pd_table = data.loc[:, ['sentence']]
    # html_table = pd_table.to_html(border=0)
    return pd_table.to_json(orient='records')


def df_to_tree(df):
    flare = dict()
    d = {"name": "flare", "children": []}
    for index, row in df.iterrows():
        parent = row[0]
        child = row[1]
        child_size = row[2]
        # print(row)
        # Make a list of keys
        key_list = []
        for item in d['children']:
            key_list.append(item['name'])
        # if 'parent' is NOT a key in flare.JSON, append it
        if not parent in key_list:
            d['children'].append({"name": parent, "children": [{"children": [{'name': child_size, 'children':[]}], "name": child}]})
        # if parent IS a key in flare.json, add a new child to it
        else:
            d['children'][key_list.index(parent)]['children'].append({"children": [{'name': child_size, 'children':[]}], "name": child})
    flare = d
    return flare


def make_comparable_action_trees(text):
    df1 = pd.read_excel('static\FB_action_items_feb_2006.xlsx', encoding='Latin-1')
    filtered_row_indexes1 = df1['subject'] == text
    data1 = df1[filtered_row_indexes1].reset_index().loc[:, ['subject', 'relation', 'object']].drop_duplicates()
    list_rel1 = data1['relation'].tolist()

    df2 = pd.read_excel('static\FB_action_items_oct_2006.xlsx', encoding='Latin-1')
    filtered_row_indexes2 = df2['subject'] == text
    data2 = df2[filtered_row_indexes2].reset_index().loc[:, ['subject', 'relation', 'object']].drop_duplicates()

    tree1 = df_to_tree(data1)
    tree2 = df_to_tree(data2)

    return tree1, tree2, list_rel1


def maketable_risk(rows):
    ready_table='<tr>'
    for row in rows:
        ready_table += '<TR>'
        for column in row:
            if 'span' not in str(column):
                 ready_table+='<TD class="pt-3-half" contenteditable="true">'+str(column)+'</TD>'
            else:
                ready_table += '<TD>' + str(column) + '</TD>'
        ready_table += '</TR>'
    return(ready_table)


def getCustomActions():
    sql = "select * from ACTION_CONNECTION"
    con = sqlite3.connect(DBPath)
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    ready_rows = maketable_risk(rows)
    # print(ready_rows)
    return ready_rows


def save_data(new_data):
    last_col='''<span class="table-remove"><button type="button" class="btn btn-rounded btn-sm my-0">Remove</button></span>'''
    con = sqlite3.connect(DBPath)
    cur = con.cursor()

    query = 'delete from ACTION_CONNECTION'
    cur.execute(query)
    con.commit()

    for row in new_data:
        query = '''insert into ACTION_CONNECTION values ('%s', '%s', '%s', '%s', '%s', '%s')'''%(str(row[0]),str(row[1]),str(row[2]),str(row[3]),str(row[4]),last_col)
        # print(query)
        cur.execute(query)
        con.commit()


def getActionClusterJsonData(subject_type_filter, subject_filter, cluster_filter, process_filter, special_filter):

    print(subject_type_filter,subject_filter,cluster_filter,process_filter,special_filter)
    G = nx.DiGraph()
    # df = pd.read_excel(r'static\action_graph_FINAL.xlsx')
    df = pd.read_excel(r'static\LIBOR_term_graph.xlsx')

    if(subject_type_filter != 'All'):
        df=df[(df['subject_node_type'].isin(subject_type_filter) | df['object_node_type'].isin(subject_type_filter))]

    if(subject_filter != 'All'):
        df = df[(df['subject'].isin(subject_filter)) | (df['object'].isin(subject_filter))]

    if (process_filter != 'All'):
        df = df[df['process'].isin(process_filter)]

    if((special_filter != 'All') & (cluster_filter != 'All')):
        # df = df[(df['subject_node_type'].isin(special_filter) | df['object_node_type'].isin(special_filter) | df['cluster_label'].isin(cluster_filter))]
        df = df[(df['relationship_node_type'].isin(special_filter)) | df['relationship_node_type'].isin(cluster_filter)]

    elif (special_filter != 'All'):
        # df = df[(df['subject_node_type'].isin(special_filter) | df['object_node_type'].isin(special_filter))]
        df = df[df['relationship_node_type'].isin(special_filter)]

    elif (cluster_filter != 'All'):
        # df = df[df['cluster_label'].isin(cluster_filter)]
        df = df[df['relationship_node_type'].isin(cluster_filter)]

    # node_subject_df = df.reset_index().loc[:, ['subject', 'cluster_id', 'subject_node_type']]
    # node_object_df = df.reset_index().loc[:, ['object', 'cluster_id','object_node_type']]
    # node_subject_df.columns=['entity', 'cluster','node_type']
    # node_object_df.columns=['entity', 'cluster','node_type']

    node_subject_df = df.reset_index().loc[:, ['subject']]
    node_object_df = df.reset_index().loc[:, ['object']]
    node_subject_df.columns=['entity']
    node_object_df.columns=['entity']

    nodes_list=pd.concat([node_subject_df, node_object_df], axis= 0).drop_duplicates('entity').fillna('NA').values.tolist()
    # print(nodes_list)
    # edge_df = df.reset_index().loc[:, ['subject', 'object', 'relation', 'cluster_id', 'sentence', 'process', 'subprocess', 'score', 'cluster_label', 'topics', 'lob', 'sublob', 'Responsibility', 'email', 'phone', 'directive']].drop_duplicates().fillna('NA')
    edge_df = df.reset_index().loc[:, ['subject', 'object', 'relation']].drop_duplicates().fillna('NA')


    edges_list = edge_df.values.tolist()
    print(edges_list)
    # import numpy
    # Import id, name, and group into node of Networkx:
    for i in nodes_list:
        # G.add_node(i[0], id=i[0], group=i[1], type=i[2])
        G.add_node(i[0], id=i[0])

    # Import source, target, and value into edges of Networkx:
    for i in edges_list:
       # G.add_edge(i[0], i[1], value=i[2], cluster=i[3], sentence=i[4], process=i[5], subprocess=i[6], score=i[7], cluster_label=i[8], topics=i[9], lob=i[10], sub_lob=i[11], responsible=i[12], email=i[13], phone=i[14], directive=i[15])
       G.add_edge(i[0], i[1], value=i[2])


    from networkx.readwrite import json_graph
    j = json_graph.node_link_data(G)

    print(j)
    return(j)


if __name__ == "__main__":
    getActionClusterJsonData()