#! /bin/bash

export SLACK_WEBHOOK_URL=
export PATH_TO_GSN=/PATH/TO/github-status-notification/
export PATH_TO_GSN_SCRAPY=/PATH/TO/VENV/bin/

cd $PATH_TO_GSN/
echo '['$(date)'] Github Status Notification is started'
$PATH_TO_GSN_SCRAPY/scrapy crawl github-status --loglevel WARNING
