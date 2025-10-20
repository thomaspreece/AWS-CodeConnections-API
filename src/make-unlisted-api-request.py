import json

import boto3
import requests
import os 

from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

# Code to make an AWS API request for a undocumented operation/api
# See the following for more:
# - https://github.com/DataDog/undocumented-aws-api-hunter
# - https://github.com/frichetten/aws-api-models
# - https://frichetten.com/blog/aws-api-protocols/

boto_session = boto3.Session()
credentials = boto_session.get_credentials()

region = "eu-west-1"
service = "codeconnections"
method = "POST"
host = "codeconnections.eu-west-1.amazonaws.com"
path = "/"
url=f'https://{host}{path}'
data={"ProviderTypeFilter": 'GitHub', "MaxResults": 50}                                                                                                                                                                                    

content_type='application/x-amz-json-1.0' 
target="com.amazonaws.codeconnections.CodeConnections_20231201.ListConnections" 

request = AWSRequest(
    method,
    url,
    headers={
        "X-Amz-Target": target,
        'Content-Type': content_type
    },
    data=json.dumps(data)
)

SigV4Auth(credentials, service, region).add_auth(request)

response = requests.request(
    method, 
    url, 
    headers=dict(request.headers),
    data=json.dumps(data)
)
print(response.status_code)
print(response.text)