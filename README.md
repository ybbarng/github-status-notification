# Github Status Notification

Notify the new messages in [Github Status](https://status.github.com/messages) to slack


## Notification
Notify to slack when the following:
* a new trouble message: a new minor or major messsage
* a new good message followed a trouble message


## Dependencies
* Python 3.7
* [arrow](https://github.com/crsmithdev/arrow)
* [requests](http://docs.python-requests.org/en/master/)
* [Scrapy](https://scrapy.org/)


## How to Use
1. Clone this project
```sh
git clone https://github.com/ybbarng/github-status-notification.git
```
2. Install dependencies
```sh
pip install -r requirements.txt
```

3. Modify the [run.sh](run.sh) to set the variables

ex)
```sh
...
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/ABC/DEF/GHI
export PATH_TO_GSN=/Users/me/github-status-notification/
export PATH_TO_GSN_SCRAPY=/Users/me/.virtualenvs/github-status-notification/bin/
...
```

4. add crontab
```
$ crontab -e
*/10 * * * * /PATH/TO/github-status-notification/run.sh >> /tmp/github-status-notification.log 2>&1
```
