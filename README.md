Create recurring Pivotal Tracker or Targetprocess stories with AWS Lambda.

1. Copy config.json.sample to config.json and configure the following as needed:
   - `ssm_pt_token_path`: Name of SSM Parameter Store parameter to store
      your API token for Pivotal Tracker
   - `ssm_tp_token_path`: Name of SSM Parameter Store parameter to store
      your service token for Targetprocess
   - `ssm_tp_domain`: Name of SSM Parameter Store parameter to store
      your Targetprocess domain (example of a value: `md5.tpondemand.com`)
   - `ssm_aws_region`: Region of SSM Parameter Store to use
   - `rules`: Keys of this object correspond to the CloudWatch Events rules
      you set up later. The values define which project to create the story in
      and other attributes of the story.
2. Package up `main.py` and `config.json` and deploy as an AWS Lambda function.
3. Allow the Lambda function to call `ssm:GetParameter`
   by attaching the appropriate IAM role policy.
4. Put required SSM parameters:
```
# for Pivotal Tracker
aws --region=region-configured-in-config-json \
    ssm put-parameter \
    --name "/name-configured-in-config-json" \
    --value "your-tracker-api-token" \
    --type SecureString
# for Targetprocess
aws --region=region-configured-in-config-json \
    ssm put-parameter \
    --name "/name-configured-in-config-json" \
    --value "your-targetprocess-service-token" \
    --type SecureString
aws --region=region-configured-in-config-json \
    ssm put-parameter \
    --name "/name-configured-in-config-json" \
    --value "your-targetprocess-domain" \
    --type SecureString
```
5. [Set up CloudWatch Event rules](http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/RunLambdaSchedule.html)
   to trigger the Lambda function with the desired frequency.

## Running tests

```
virtualenv env
. env/bin/activate
pip-compile dev-requirements.in requirements.txt
pip install -r requirements.txt
pip install -r dev-requirements.txt
pytest tests.py
```

## Upgrading a dependency

If you have Nix, you can load a shell with the necessary dependencies like this:

```
nix-shell -p python37Packages.pip-tools
```

Once in the shell, run:

```
pip-compile --upgrade-package my-package
```
