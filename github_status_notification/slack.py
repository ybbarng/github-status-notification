import json
import os

import requests


webhook_url = os.getenv('SLACK_WEBHOOK_URL')


def write(timestamp, status, message):
    if not webhook_url:
        raise ValueError('Invalid slack webook_url: {}'.format(webhook_url))
    colors = {
        'good': 'good',
        'minor': 'warning',
        'major': 'danger',
    }
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'attachments': [
            {
                'author_name': 'GitHub Status',
                'author_link': 'https://status.github.com/messages',
                'pretext': 'A new github status message is arrived',
                'fallback': 'GitHub Status - {}: {}'.format(status, message),
                'title': 'New Status Message',
                'fields': [
                    {
                        'title': 'When',
                        'value': timestamp,
                        'short': True,
                    },
                    {
                        'title': 'Status',
                        'value': status.capitalize(),
                        'short': True,
                    },
                    {
                        'title': 'Message',
                        'value': message,
                        'short': False,
                    },
                ],
                'color': colors[status],
            },
        ]
    }
    response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise ValueError('Request to slack returned an error: ({}, {})'.format(response.status_code, response.text))

if __name__ == '__main__':
    write('12:45', 'good', 'All systems reporting at 100%')
