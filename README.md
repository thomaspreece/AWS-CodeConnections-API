# CodeConnections-API

This repository provides code to call the undocumented AWS API operations in the CodeConnections API. 

The code in `make-unlisted-api-request.py` shows how to make a single undocumented AWS API operation call to CodeConnections API.
The code in `test-codeconnection-api-methods.py` tests several CodeConnection operations to several different source code providers and also tests the effect different conditions on `UseConnection` IAM permission have on these operations.

This code was used in the research that is detailed in the following blog posts:
- TODO
- TODO


## Requirements

- Load `IAMRoles-CodeConnectins.yaml`, `IAMRoles-CodeStar.yaml` and `IAMRoles-CodeStarWCodeConnectionConditions.yaml` into your AWS Account
- Setup CodeConnections into your AWS Account for the different source code providers you want to test.
- Install the python dependencies listed in `requirements.txt`


## Use 

- Update `test-codeconnection-api-methods.py` to use your AWS account ID and CodeConnection ARNs.
- Update `test-codeconnection-api-methods.py` to use the owner and repos that your CodeConnections can access.
- Run `python3 ./test-codeconnection-api-methods.py`

Then view results in `results.csv`
