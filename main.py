from __future__ import print_function

import types
import datetime
import json

import requests
import boto3


CONFIG_FILE = 'config.json'


def on_event(event, context):
    config = read_config()
    rv = process_event(config, event)
    return rv


def process_event(config, event):
    rv = []

    for rule_name in iter_rule_names(event):
        rv.extend(process_rule(config, rule_name))

    return rv


def read_config(config_path=CONFIG_FILE):
    with open(config_path) as f:
        return json.load(f)


def iter_rule_names(event):
    for resource in event['resources']:
        yield resource.split('/', 1)[-1]


def process_rule(config, rule_name):
    if rule_name not in config['rules']:
        return []

    story_spec = config['rules'][rule_name]
    story_params = interpolate_story_spec(story_spec)
    handler = handler_factory(config, story_params)
    story = handler.create_story()
    return [story]


def handler_factory(config, story_params):
    service = story_params['service']
    if service == 'pivotal-tracker':
        token = fetch_token(config['ssm_aws_region'], config['ssm_pt_token_path'])
        return PivotalTracker(token, story_params)
    raise Exception('Unknown service {}'.format(service))


def fetch_token(region, ssm_path):
    ssm = boto3.client('ssm', region_name=region)
    return ssm.get_parameter(
        Name=ssm_path,
        WithDecryption=True,
    )['Parameter']['Value']


class PivotalTracker(object):
    DEFAULT_STORY_PARAMS = {
        "current_state": "unstarted"
    }

    def __init__(self, token, story_params):
        self._story_params = dict(self.DEFAULT_STORY_PARAMS, **story_params)
        self._token = token

    def create_story(self):
        response = requests.post(
            self._stories_endpoint(),
            json=self._story_params,
            headers=self._headers)
        created_story = response.json()
        updated_story = self._move_to_top_of_backlog(created_story)
        return updated_story

    def _get_current_top_of_backlog(self):
        params = {
            'with_state': 'unstarted',
            'limit': 1
        }
        response = requests.get(
            self._stories_endpoint(),
            params=params,
            headers=self._headers)
        return response.json()

    def _move_to_top_of_backlog(self, target_story):
        top_story = self._get_current_top_of_backlog()
        print((top_story))
        if len(top_story) == 0:
            return target_story

        params = {
            'group': 'scheduled',
            'before_id': top_story[0]['id'],
        }
        response = requests.put(
            self._story_endpoint(target_story['id']),
            json=params,
            headers=self._headers,
        )
        return response.json()

    def _stories_endpoint(self):
        return "https://www.pivotaltracker.com/services/v5/projects/{}/stories".format(self._project_id)

    def _story_endpoint(self, story_id):
        return "https://www.pivotaltracker.com/services/v5/projects/{}/stories/{}".format(self._project_id, story_id)

    @property
    def _project_id(self):
        return self._story_params['project_id']

    @property
    def _headers(self):
        return {
            'X-TrackerToken': self._token,
        }


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


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--rule-name', required=True)
    args = parser.parse_args()
    mock_event = {'resources': ['arn:mock/{}'.format(args.rule_name)]}
    print(on_event(mock_event, None))
