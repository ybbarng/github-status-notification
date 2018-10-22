#! /bin/bash

export PATH_TO_GSN=/PATH/TO/github-status-notification/
export PATH_TO_GSN_SCRAPY=/PATH/TO/VENV/bin/

cd $PATH_TO_GSN/
$PATH_TO_GSN_SCRAPY/scrapy crawl github-status
