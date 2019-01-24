import json

import requests

import main


def test_process_event_pivotal_tracker(mocker):
    mock_client = mocker.patch.object(main.boto3, 'client').return_value
    mock_client.get_parameter.return_value = {
        'Parameter': {
            'Value': 'some secret'
        }
    }
    # called in create_story
    mock_post = mocker.patch.object(requests, 'post')
    # called in _get_current_top_of_backlog
    mock_get = mocker.patch.object(requests, 'get')
    mock_get.return_value.json.return_value = [{'id': 1}]
    # called in _move_to_top_of_backlog
    mock_put = mocker.patch.object(requests, 'put')

    config = main.read_config('config.json.sample')
    with open('test_event_one.json', 'r') as f:
        mock_event = json.load(f)

    rv = main.process_event(config, mock_event)

    mock_post.assert_called()
    mock_get.assert_called()
    mock_put.assert_called()

    assert len(rv) > 0


def test_process_event_targetprocess(mocker):
    mock_client = mocker.patch.object(main.boto3, 'client').return_value
    mock_client.get_parameter.return_value = {
        'Parameter': {
            'Value': 'some secret'
        }
    }
    # called in create_story
    mock_post = mocker.patch.object(requests, 'post')

    config = main.read_config('config.json.sample')
    with open('test_event_two.json', 'r') as f:
        mock_event = json.load(f)

    rv = main.process_event(config, mock_event)

    mock_post.assert_called()

    assert len(rv) > 0


def test_interpolate_story_spec():
    spec = {'with date': '{date}'}
    params = main.interpolate_story_spec(spec)

    assert params['with date'] != '{date}'
