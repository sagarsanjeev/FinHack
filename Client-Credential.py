from flask import Flask, session, render_template, url_for, redirect, request, jsonify
import requests
import os
import json
import pandas as pd
import helpers

app = Flask(__name__)

# Global variables
client_id = os.getenv("CLIENT_ID")
access_key = os.getenv("CLIENT_SECRET")
token_endpoint = os.getenv("TOKEN_URL")
base_url = os.getenv("BASE_URL")
strong = os.getenv("STRONG")=='True'

# Main page
@app.route('/')
def auth():
    return render_template('index.html', strong=strong)

# Log in
@app.route("/login", methods=["GET","POST"])
def login():
    
    data = {'grant_type':'client_credentials'}
    if(strong):
        data['client_assertion_type'] = 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer'
        data['client_assertion'] = helpers.jwToken()
    else:
        data['client_id'] = client_id
        data['client_secret'] = access_key    
   
    headers = {'Content-Type':'application/x-www-form-urlencoded'}    
    r = requests.post(token_endpoint, headers=headers, data=data)
    response =  r.json()
    
    if (r.status_code is 200):         
        token = response['access_token']
        # Put token in the session
        session['session_token'] = token    
    
    return render_template('auth.html', token=token, strong=strong)

# Display the results
@app.route('/results')
def results():
    try:
        headers={"Authorization": "Bearer " + session['session_token']}
        result = requests.get(base_url + '/liquidity/clientinformation/v1/clients?limit=1000&offset=10', headers=headers)
        with open('static/testDataApi.json', 'w') as f:
            f.write(result.text)
        return render_template('action.html', error="Success", strong=strong)
    except:
        return render_template('error.html', error="Unauthorized!", strong=strong)

# Logout
@app.route('/logout')
def logout():  
    session['session_token']=''
    return render_template('logout.html', error="You successfully removed the access token.", strong=strong)

@app.route('/panama')
def home():
    return render_template('action.html')

@app.route('/getAPIData')
def getAPIData():
    with open('static/testDataApi.json') as json_file:
        data = json.load(json_file)
    result = []
    for client in data['data']['clients']:
        result.append(client['name'])
    return jsonify(result={"data": result})

@app.route('/getPanamaData')
def getPanamaData():
    filterText = request.args.get('filter_text', 0, type=str)
    filePath = 'static/' + filterText + '.json'
    with open(filePath) as f:
        res = json.load(f)
    return jsonify(result={"data": res})

@app.route('/getNodeDetails')
def getNodeDetails():
    nodeId = request.args.get('filter_text', 0, type=str)
    df_a = pd.read_csv('static/csv_panama_papers.2017-11-17/panama_papers.nodes.address.csv',
                       usecols=['n.address', 'n.node_id'])
    df_b = pd.read_csv('static/csv_panama_papers.2017-11-17/panama_papers.nodes.entity.csv',
                       usecols=['n.name', 'n.node_id'])
    df_c = pd.read_csv('static/csv_panama_papers.2017-11-17/panama_papers.nodes.intermediary.csv',
                       usecols=['n.name', 'n.node_id'])
    df_d = pd.read_csv('static/csv_panama_papers.2017-11-17/panama_papers.nodes.officer.csv',
                       usecols=['n.name', 'n.node_id'])
    df_a.columns = ['n.node_id', 'n.name']
    df = pd.concat([df_a, df_b, df_c, df_d])

    lkp = df.set_index('n.node_id')['n.name'].to_dict()
    nodeName = lkp[int(nodeId)]
    return jsonify(result={"data": 'Node Name: ' + nodeName})


# Main script
if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True,host='0.0.0.0' ,port=80)
