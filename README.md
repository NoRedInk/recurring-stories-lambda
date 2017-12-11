Create recurring Pivotal Tracker stories with AWS Lambda.

1. Copy config.json.sample to config.json and configure the following as needed:
   - `ssm_tracker_token_name`: Name of SSM Parameter Store parameter to store
      your API token for Pivotal Tracker
   - `ssm_aws_region`: Region of SSM Parameter Store to use
   - `rules`: Keys of this object correspond to the CloudWatch Events rules
      you set up later. The values define which project to create the story in
      and other attributes of the story.
2. Package up `main.py` and `config.json` and deploy as an AWS Lambda function.
3. Store your Pivotal Tracker API token in SSM Parameter Store:
```
aws --region=region-configured-in-config-json \
    ssm put-parameter \
    --name "/name-configured-in-config-json" \
    --value "your-tracker-api-token" \
    --type SecureString
```
4. [Set up CloudWatch Event rules](http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/RunLambdaSchedule.html)
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
