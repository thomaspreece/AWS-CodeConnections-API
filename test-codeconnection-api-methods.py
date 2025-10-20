import json

import boto3
import requests
import os 

from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

import datetime
import csv 
import time

# Target, Data & ContentType are all defined from the AWS models. See the below URL:
# https://github.com/boto/botocore/blob/develop/botocore/data/codeconnections/2023-12-01/service-2.json
def make_codeconnection_request(
        boto_credentials, 
        target, 
        data ,
        usecodestar=False, 
        content_type='application/x-amz-json-1.0', 
        region="eu-west-1", 
        host=None,
        path=None
    ):
    if usecodestar:
        service = "codestar-connections"
        target_prefix = "com.amazonaws.codestar.connections.CodeStar_connections_20191201."
    else:
        service = "codeconnections"
        target_prefix = "com.amazonaws.codeconnections.CodeConnections_20231201."

    method = "POST"
    if host == None:
        if usecodestar: 
            host = f"codestar-connections.{region}.amazonaws.com"
        else:
            host = f"codeconnections.{region}.amazonaws.com"
    if path == None:
        path = "/"
    
    url=f'https://{host}{path}'                                                                                                                                                                     

    request = AWSRequest(
        method,
        url,
        headers={
            "X-Amz-Target": target_prefix + target,
            'Content-Type': content_type
        },
        data=json.dumps(data)
    )

    SigV4Auth(boto_credentials, service, region).add_auth(request)

    response = requests.request(
        method, 
        url, 
        headers=dict(request.headers),
        data=json.dumps(data)
    )

    return {
        "request": {
            "headers": dict(request.headers),
            "data": data,
        },
        "response": response
    }

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_codeconnection_request(reqres):
    target = reqres["request"]["headers"]["X-Amz-Target"]
    data = reqres["request"]["data"]
    response = reqres["response"]

    print(f'== {target.split(".")[-1]} == ')
    print(f'{bcolors.FAIL}{target.split(".")[-1]}: {response.status_code}{bcolors.ENDC}')
    print(f"Response: {json.dumps(response.text)}")

# Start Session
main_boto_session = boto3.Session(profile_name="default")
main_sts_client = boto3.client("sts")

roles = [
    "arn:aws:iam::851725397705:role/CodeConnectionUseConnectionNoConditions",
    "arn:aws:iam::851725397705:role/CodeConnectionUseConnectionActionConditionAll",
    "arn:aws:iam::851725397705:role/CodeConnectionUseConnectionActionConditionOne",
    "arn:aws:iam::851725397705:role/CodeConnectionUseConnectionFullRepositoryIdConditionAll",
    "arn:aws:iam::851725397705:role/CodeConnectionUseConnectionFullRepositoryIdConditionOne",
    "arn:aws:iam::851725397705:role/CodeConnectionUseConnectionPermissionsConditionAll",
    "arn:aws:iam::851725397705:role/CodeConnectionUseConnectionPermissionsConditionOne",
    
    "arn:aws:iam::851725397705:role/CodeStarConnectionCCCNoConditions",
    "arn:aws:iam::851725397705:role/CodeStarConnectionCCCActionConditionAll",
    "arn:aws:iam::851725397705:role/CodeStarConnectionCCCActionConditionOne",
    "arn:aws:iam::851725397705:role/CodeStarConnectionCCCFullRepositoryIdConditionAll",
    "arn:aws:iam::851725397705:role/CodeStarConnectionCCCFullRepositoryIdConditionOne",
    "arn:aws:iam::851725397705:role/CodeStarConnectionCCCPermissionsConditionAll",
    "arn:aws:iam::851725397705:role/CodeStarConnectionCCCPermissionsConditionOne",

    "arn:aws:iam::851725397705:role/CodeStarConnectionNoConditions",
    "arn:aws:iam::851725397705:role/CodeStarConnectionActionConditionAll",
    "arn:aws:iam::851725397705:role/CodeStarConnectionActionConditionOne",
    "arn:aws:iam::851725397705:role/CodeStarConnectionFullRepositoryIdConditionAll",
    "arn:aws:iam::851725397705:role/CodeStarConnectionFullRepositoryIdConditionOne",
    "arn:aws:iam::851725397705:role/CodeStarConnectionPermissionsConditionAll",
    "arn:aws:iam::851725397705:role/CodeStarConnectionPermissionsConditionOne"
]

connection_details = [
    {
        "name": "GitHub",
        "connection_arn": "arn:aws:codeconnections:eu-north-1:851725397705:connection/b269d902-b454-4c8c-954c-1e1b16e65c48"
    },
    {
        "name": "GitLab",
        "connection_arn": "arn:aws:codeconnections:eu-north-1:851725397705:connection/8ce09f63-0064-4db9-8e73-45c13ba3c5a4"
    },
    {
        "name": "Bitbucket",
        "connection_arn": "arn:aws:codeconnections:eu-north-1:851725397705:connection/a2d116c1-7ec6-48bd-b48d-7f474964a5cc"
    }
]

results_csv = open('results.csv', mode='w')
results_writer = csv.writer(results_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

results_writer.writerow([
    "connection_name",
    "role_arn_short",
    "role_arn",
    "operation_short",
    "operation",
    "status",
    "response_text"
])

for connection_detail in connection_details:
    owner = "thomaspreece-test-org"
    repo1 = "repo-1"
    repo2 = "repo-2"
    connection_arn = connection_detail["connection_arn"]
    connection_name = connection_detail["name"]

    for role_arn in roles:
        response = main_sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="codeconnection-testing-session"
        )
        credentials = response["Credentials"]
        assumed_session = boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"]
        )
        boto_credentials = assumed_session.get_credentials()

        # Confirm users identity to ensure we are using the correct IAM role during tests
        caller_identity = assumed_session.client('sts').get_caller_identity()    
        
        print("===============================================================")
        print("===============================================================")
        print(f'ARN: {caller_identity["Arn"]}')
        print(f'{bcolors.FAIL}CONNECTION: {connection_name} & ROLE: {role_arn.split("/")[-1]}{bcolors.ENDC}')
        print("===============================================================")
        print("===============================================================")


        request_array = [
            [
                "ListOwners",
                {
                    "ConnectionArn":connection_arn,
                    "MaxResults":100
                }   
            ],
            [
                "ListRepositories",
                {
                    "ConnectionArn":connection_arn,
                    "Parameters":{
                        "OwnerId":owner
                    },
                    "MaxResults":100
                }   
            ],
            [
                "GetRepository",
                {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "FullRepositoryId": f"{owner}/{repo1}"
                    }
                },
                "GetRepository-repo1"       
            ],
            [
                "GetRepository",
                {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "FullRepositoryId": f"{owner}/{repo2}"
                    }
                },
                "GetRepository-repo2"           
            ],
            [
                "DeleteRepository",
                {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "FullRepositoryId": f"{owner}/{repo2}"
                    }
                }           
            ],
            [
                "CreateRepository",
                {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "OwnerId": owner,
                        "RepositoryName": repo2,
                        "Private": True,
                        "EnableIssues": True,
                        "Description": "It's a repo created by CodeConnections!"
                    }
                }          
            ],            
            [
                "CreatePullRequest",
                {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "FullRepositoryId": f"{owner}/{repo1}",
                        "Title": f'new Pull Request Title {datetime.datetime.now().strftime("%I %M%p on %B %d, %Y")}',
                        "SourceBranchName": "not-main",
                        "DestinationBranchName": "main"
                    }
                }           
            ],
            [
                "ListPullRequests",
                {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "FullRepositoryId": f"{owner}/{repo1}",
                        "Status": "OPEN"
                    }
                }           
            ],
            [
                "GetPullRequest",
                {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "FullRepositoryId": f"{owner}/{repo1}",
                        "PullRequestId": "1"
                    }
                }           
            ],
            [
                "UpdatePullRequest",
                {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "FullRepositoryId": f"{owner}/{repo1}",
                        "Title": f'update Pull Request {datetime.datetime.now().strftime("%I%M%p on %B %d, %Y")}',
                        "Body": "Hello Again",
                        "PullRequestId": "1",
                        "Status": "CLOSED"
                    }
                }           
            ],
            [
                "CreatePullRequestComment",
                {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "FullRepositoryId": f"{owner}/{repo1}",
                        "Body": f'Hello from a comment - {datetime.datetime.now().strftime("%I%M%p on %B %d, %Y")}',
                        "PullRequestId": "1"
                    }
                }          
            ],
            [
                "ListPullRequestComments",
                {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "FullRepositoryId": f"{owner}/{repo1}",
                        "PullRequestId": "1"
                    }
                }           
            ],
            [
                "ListPullRequestCommits",
                {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "FullRepositoryId": f"{owner}/{repo1}",
                        "PullRequestId": "1"
                    }
                }           
            ],
            [
                "ListWebhooks",
                {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "FullRepositoryId": f"{owner}/{repo1}"
                    }
                }
            ],
            [
                "CreateWebhook",
                {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "FullRepositoryId": f"{owner}/{repo1}",
                        "Url": "https://thomaspreece.com/testing",
                        "Scopes": ["push"]
                    }
                }           
            ],
            [
                "GetConnectionToken",
                {
                    "ConnectionArn":connection_arn,
                }           
            ]
        ]


        # Reset Repos
        reqres = make_codeconnection_request(
            main_boto_session.get_credentials(), 
            "CreateRepository", 
            {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "OwnerId": owner,
                        "RepositoryName": repo2,
                        "Private": True,
                        "EnableIssues": True,
                        "Description": "It's a repo created by CodeConnections!"
                    }
            }, 
            False
        )

        print("====== CodeConnection Requests ======")
        for request in request_array:
            target = request[0]
            params = request[1]
            name = None 
            if len(request) > 2:
                name = request[2]
            reqres = make_codeconnection_request(boto_credentials, target, params, False)
            if target == "CreatePullRequest" and reqres["response"].status_code == 200:
                pr_id = reqres["response"].json()["PullRequest"]["PullRequestId"]
                # Reset PRs
                make_codeconnection_request(
                    boto_credentials, 
                    "UpdatePullRequest",
                    {
                        "ConnectionArn":connection_arn,
                        "Parameters": {
                            "FullRepositoryId": f"{owner}/{repo1}",
                            "PullRequestId": pr_id,
                            "Status": "CLOSED"
                        }
                    },
                    False                             
                )
            print_codeconnection_request(reqres)
            if name == None:
                name = reqres["request"]["headers"]["X-Amz-Target"].split(".")[-1]
            results_writer.writerow([
                connection_name,
                role_arn.split("/")[-1],
                role_arn,
                "CodeConnection." + name,
                reqres["request"]["headers"]["X-Amz-Target"],
                reqres["response"].status_code,
                json.dumps(reqres["response"].text)
            ])
            # time.sleep(0.5)
       
        # Reset Repos
        reqres = make_codeconnection_request(
            main_boto_session.get_credentials(), 
            "CreateRepository", 
            {
                    "ConnectionArn":connection_arn,
                    "Parameters": {
                        "OwnerId": owner,
                        "RepositoryName": repo2,
                        "Private": True,
                        "EnableIssues": True,
                        "Description": "It's a repo created by CodeConnections!"
                    }
            }, 
            False
        )

        print("====== CodeStar Requests ======")
        for request in request_array:
            target = request[0]
            params = request[1]
            name = None 
            if len(request) > 2:
                name = request[2]
            reqres = make_codeconnection_request(boto_credentials, target, params, True)
            if target == "CreatePullRequest" and reqres["response"].status_code == 200:
                pr_id = reqres["response"].json()["PullRequest"]["PullRequestId"]
                # Reset PRs
                make_codeconnection_request(
                    boto_credentials, 
                    "UpdatePullRequest",
                    {
                        "ConnectionArn":connection_arn,
                        "Parameters": {
                            "FullRepositoryId": f"{owner}/{repo1}",
                            "PullRequestId": pr_id,
                            "Status": "CLOSED"
                        }
                    },
                    True                             
                )
            print_codeconnection_request(reqres)
            if name == None:
                name = reqres["request"]["headers"]["X-Amz-Target"].split(".")[-1]                        
            results_writer.writerow([
                connection_name,
                role_arn.split("/")[-1],
                role_arn,
                "CodeStar." + name,
                reqres["request"]["headers"]["X-Amz-Target"],
                reqres["response"].status_code,
                json.dumps(reqres["response"].text)
            ])
            # time.sleep(0.5)
 
results_csv.close()