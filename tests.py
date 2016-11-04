import main

import requests
import credstash


MOCK_EVENT = {
    "account": "123456789012",
    "region": "us-east-1",
    "detail": {},
    "detail-type": "Scheduled Event",
    "source": "aws.events",
    "time": "1970-01-01T00:00:00Z",
    "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
    "resources": [
        "arn:aws:events:us-east-1:123456789012:rule/my-schedule"
    ]
}

def test_process_event(mocker):
    mocker.patch.object(credstash, 'getSecret')
    mocker.patch.object(requests, 'post')
    config = main.read_config('config.json.sample')

    rv = main.process_event(config, MOCK_EVENT)

    assert len(rv) > 0


def test_interpolate_story_spec():
    spec = {'with date': '{date}'}
    params = main.interpolate_story_spec(spec)

    assert params['with date'] != '{date}'
