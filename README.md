# CodeConnections-API

This repository provides code to call the undocumented AWS API operations in the CodeConnections API. 

The code in `make-unlisted-api-request.py` shows how to make a single undocumented AWS API operation call to CodeConnections API.
The code in `test-codeconnection-api-methods.py` tests several CodeConnection operations to several different source code providers and also tests the effect different conditions on `UseConnection` IAM permission have on these operations.

This code was used in the research that is detailed in the following blog posts:
- TODO
- TODO


## Requirements

- Load `Iac/IAMRoles-CodeConnectins.yaml`, `Iac/IAMRoles-CodeStar.yaml` and `Iac/IAMRoles-CodeStarWCodeConnectionConditions.yaml` into your AWS Account
- Setup CodeConnections into your AWS Account for the different source code providers you want to test.
- Install the python dependencies listed in `requirements.txt`


## Use 

- Update `src/test-codeconnection-api-methods.py` to use your AWS account ID and CodeConnection ARNs.
- Update `src/test-codeconnection-api-methods.py` to use the owner and repos that your CodeConnections can access.
- Run `python3 ./src/test-codeconnection-api-methods.py`
- View results in `results.csv`
- To do some basic analysis, run `python3 ./src/test--codeconnection-api-methods-analyse.py`



