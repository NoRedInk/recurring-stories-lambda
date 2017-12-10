import main

import requests


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
    mock_client = mocker.patch.object(main.boto3, 'client').return_value
    mock_client.get_parameter.return_value = {
        'Parameter': {
            'Value': 'some secret'
        }
    }
    mock_post = mocker.patch.object(requests, 'post')
    mock_move_to_top = mocker.patch.object(main, 'move_to_top_of_backlog')
    config = main.read_config('config.json.sample')

    rv = main.process_event(config, MOCK_EVENT)

    mock_post.assert_called()
    mock_move_to_top.assert_called()

    assert len(rv) > 0


def test_interpolate_story_spec():
    spec = {'with date': '{date}'}
    params = main.interpolate_story_spec(spec)

    assert params['with date'] != '{date}'
