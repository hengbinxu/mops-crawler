#!/bin/bash

# set -ex

EGG_FILE_NAME="crawler_service.egg"
SCRAPY_HOME=/Users/wayne/python_scripts/mops-crawler
# SCRAPY_INFO_DIR=${SCRAPY_HOME}
SCRAPY_INFO_DIR=/var/scrapyd

# # Ensure your project has been eggified.
# if [ ! -d "${SCRAPY_HOME}/build" ] || [ ! -d "${SCRAPY_HOME}/project.egg-info"  ];then
#     scrapyd-deploy --build-egg=${EGG_FILE_NAME}
# fi

extract_from_config(){
    local PROJECT_NAME=${1}
    
    echo "${PROJECT_NAME}"
    while IFS= read -r line;
    do
        # echo "${line}"
        if grep -q "\[deploy\:" <<< "${line}"; then
            echo "${line}"
        fi
    done < ${SCRAPY_HOME}/scrapy.cfg
}

NAME="mops_crawler"
extract_from_config ${NAME}


# 
# $( cat scrapy.cfg | grep -oE "version\s=\s[[:alnum:]]*" | awk -F '=' '{print $NF}' | sed "s/ //g" )

# if [ $( ls -t ${SCRAPY_INFO_DIR}/eggs | wc -l ) -eq 0 ];then
#     echo "Need to deploy your scrapy to scrapyd"
#     exit 1
# fi

# PROJECT_NAMES=($( ls -t ${SCRAPY_INFO_DIR}/eggs ))

# echo ${PROJECT_NAMES[@]}

# LAST_COMMIT_HASH=$( git rev-parse HEAD )

# SCRAPYD_PID=$( scrapyd & )

# scrapyd-deploy crawler_service -p mops_crawler