# aws-federated-python-awscli-skeleton
|name:| aws-federated-python-awscli-skeleton|
|------|--------------|
|ver:| 1.00|
|author:| Paul Dunlop + AI|
|purpose:|Primary use case for this script is making python use the aws cli for API calls, not the boto3 library... 
||why? why not! this is one way to skin a cat eh.|

# pre-reqs:
**NOTE:** Requires external tool called aws-federated-headless-login which is a go app using rod for headless browser automation found here https://github.com/stormlrd/aws-federated-headless-login. this repo comes with a precompiled version in it.

you must have installed:
- awscli
- python

set up your ~/.aws/config file with profiles with federated access. e.g:

```
[profile primary]
sso_start_url = https://d-87372cbd0b.awsapps.com/start/
sso_region = ap-southeast-2
sso_account_id = 522831239526
sso_role_name = D-Administrator
region = ap-southeast-2
output = json
```

# usage:
ensure you have set up your aws cli config properly. i have another script that can help scrape identity center profiles found here: https://github.com/stormlrd/aws-sso-cli-config-creator

copy the template & the aws-federated-headless-login executable somewhere else and rename the python script something else..

python3 ./newnameofyourscript.py to run the script