# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import socket
import os
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    print("inside method home  of Domain-1-Service-B-Cell-1.internal-Domain1.com This is cell 1")
    response1 = requests.get("http://Domain2-ServiceX-Cell1.internal-Domain2.com:5001/")

    #return "<html><head><title>Domain-1-Service-A</title></head><body bgcolor=gray><p><h1 style=color:blue>You have hit Domain-1-Service-A from node %s</h1> <p><h3 style=color:blue>The below content is fetched from Service B</h3><p><br><br><br><br><p><h1 style=color:red>%s</h1><p><br><br></body></html>" % ( socket.gethostname() , response1.content)
    return "<html><head><title>Domain-1-Service-B-Cell-1</title></head><body bgcolor=#00FFFF><p><h1 style=color:#008B8B>You have hit Domain-1-Service-B-Cell-1 from node %s</h1> </p><p><h3 style=color:#B8860B>The below content is fetched from Service X in Domain 2</h3><p><br><br><br><br><p><h1 style=color:red>%s</h1><p><br><br></body></html>" % ( socket.gethostname() , response1.content)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=os.getenv('FLASK_DEBUG',False))