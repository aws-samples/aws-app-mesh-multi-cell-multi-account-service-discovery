# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import socket
import os
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    print("inside method home  of Domain-1-Service-A-Cell-2.internal-Domain1.com This is cell 1")
   
    response1 = requests.get("http://Domain1-ServiceB-Cell1.internal-Domain1.com:5001/")

    return "<html><head><title>Domain-1-Service-A-Cell2</title></head><body bgcolor=#A52A2A><p><h1 style=color:#FAEBD7>You have hit Domain-1-Service-A-Cell-2 from node %s</h1> <p><h3 style=color:#B8860B>The below content is fetched from Service B</h3><p><br><br><br><br><p><h1 style=color:red>%s</h1><p><br><br></body></html>" % ( socket.gethostname() , response1.content)
   

    #return "<html><head><title>Domain-1-Service-A-Cell-2</title></head><body bgcolor=#A52A2A><p><h1 style=color:#FAEBD7>You have hit Domain-1-Service-A-Cell-2 from node %s</h1> </p></body></html>" % ( socket.gethostname() )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)