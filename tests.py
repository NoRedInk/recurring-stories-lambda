import json

import requests

import main


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
    with open('test_event.json', 'r') as f:
        mock_event = json.load(f)

    rv = main.process_event(config, mock_event)

    mock_post.assert_called()
    mock_move_to_top.assert_called()

    assert len(rv) > 0


def test_interpolate_story_spec():
    spec = {'with date': '{date}'}
    params = main.interpolate_story_spec(spec)

    assert params['with date'] != '{date}'
