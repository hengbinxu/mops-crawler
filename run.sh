#!/bin/bash

# # Ensure your project has been eggified.
# if [ ! -d "${SCRPAY_HOME}/build/" ] || [ ! -d "${SCRAPY_HOME}/project.egg-info"  ];then
#     scrapyd-deploy --build-egg=crawler_service.egg
# fi
SCRAPY_INFO_DIR=/var/scrapyd

if [ $( ls -t ${SCRAPY_INFO_DIR}/eggs | wc -l ) -eq 0 ];then
    echo "Need to deploy your scrapy to scrapyd"
    exit 1
fi

PROJECT_NAMES=($( ls -t ${SCRAPY_INFO_DIR}/eggs ))

echo ${PROJECT_NAMES[@]}

# LAST_COMMIT_HASH=$( git rev-parse HEAD )

# SCRAPYD_PID=$( scrapyd & )

# scrapyd-deploy crawler_service -p mops_crawler
