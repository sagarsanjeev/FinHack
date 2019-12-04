import querying2
import json
import pandas as pd
from flask import Flask, jsonify, render_template, request
app = Flask(__name__, static_url_path='/panama')


@app.route('/panama')
def home():
    return render_template('action.html')

@app.route('/getPanamaData')
def getPanamaData():
    filterText = request.args.get('filter_text', 0, type=str)
    filePath = 'static/' + filterText + '.json'
    print(filePath)
    with open(filePath) as f:
        res = json.load(f)
    return jsonify(result={"data": res})

@app.route('/getNodeDetails')
def getNodeDetails():
    nodeId = request.args.get('filter_text', 0, type=str)

    df_a = pd.read_csv('C:\PRASH\Acc\panama\csv_panama_papers.2017-11-17\panama_papers.nodes.address.csv',
                       usecols=['n.address', 'n.node_id'])
    df_b = pd.read_csv('C:\PRASH\Acc\panama\csv_panama_papers.2017-11-17\panama_papers.nodes.entity.csv',
                       usecols=['n.name', 'n.node_id'])
    df_c = pd.read_csv('C:\PRASH\Acc\panama\csv_panama_papers.2017-11-17\panama_papers.nodes.intermediary.csv',
                       usecols=['n.name', 'n.node_id'])
    df_d = pd.read_csv('C:\PRASH\Acc\panama\csv_panama_papers.2017-11-17\panama_papers.nodes.officer.csv',
                       usecols=['n.name', 'n.node_id'])

    # print(df_a)
    df_a.columns = ['n.node_id', 'n.name']
    df = pd.concat([df_a, df_b, df_c, df_d])

    lkp = df.set_index('n.node_id')['n.name'].to_dict()
    nodeName = lkp[int(nodeId)]
    return jsonify(result={"data": 'Node Name: ' + nodeName})


if __name__ == '__main__':
    app.run(port=6052)