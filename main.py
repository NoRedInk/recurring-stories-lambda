from __future__ import print_function

import types
import datetime
import json

import requests
import boto3


CONFIG_FILE = 'config.json'
DEFAULT_STORY_PARAMS = {
    "current_state": "unstarted"
}


def on_event(event, context):
    config = read_config()
    rv = process_event(config, event)
    return rv


def process_event(config, event):
    ssm = boto3.client('ssm', region_name=config['ssm_aws_region'])
    token = ssm.get_parameter(
        Name=config['ssm_tracker_token_name'],
        WithDecryption=True,
    )['Parameter']['Value']
    rv = []

    for rule_name in iter_rule_names(event):
        rv.extend(process_rule(config, token, rule_name))

    return rv


def read_config(config_path=CONFIG_FILE):
    with open(config_path) as f:
        return json.load(f)


def iter_rule_names(event):
    for resource in event['resources']:
        yield resource.split('/')[1]


def process_rule(config, pt_token, rule_name):
    if rule_name not in config['rules']:
        return []

    story_spec = config['rules'][rule_name]

    project_id = story_spec.pop('project_id')
    story_params = interpolate_story_spec(story_spec)
    story_params.update(DEFAULT_STORY_PARAMS)

    response = requests.post(
        stories_endpoint(project_id),
        json=story_params,
        headers=headers(pt_token))
    created_story = response.json()
    updated_story = move_to_top_of_backlog(pt_token, project_id, created_story)

    return [updated_story]


def get_current_top_of_backlog(pt_token, project_id):
    params = {
        'with_state': 'unstarted',
        'limit': 1
    }
    response = requests.get(
        stories_endpoint(project_id),
        params=params,
        headers=headers(pt_token))
    return response.json()


def move_to_top_of_backlog(pt_token, project_id, story):
    top_story = get_current_top_of_backlog(pt_token, project_id)
    if len(top_story) == 0:
        return story

    story_params = {
        'group': 'scheduled',
        'before_id': top_story[0]['id'],
    }
    response = requests.put(
        story_endpoint(project_id, story['id']),
        json=story_params,
        headers=headers(pt_token),
    )
    return response.json()


def interpolate_story_spec(spec):
    context = {
        'date': datetime.date.today()
    }
    return {k: interpolate_value(v, context) for (k, v) in spec.items()}


def interpolate_value(value, context):
    if isinstance(value, types.StringTypes):
        return value.format(**context)
    else:
        return value


def headers(pt_token):
    return {
        'X-TrackerToken': pt_token,
    }


def stories_endpoint(project_id):
    return "https://www.pivotaltracker.com/services/v5/projects/{}/stories".format(project_id)


def story_endpoint(project_id, story_id):
    return "https://www.pivotaltracker.com/services/v5/projects/{}/stories/{}".format(project_id, story_id)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--rule-name', required=True)
    args = parser.parse_args()
    mock_event = {'resources': ['arn:mock/{}'.format(args.rule_name)]}
    print(on_event(mock_event, None))
