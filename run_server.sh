#!/bin/bash

# Exit immediately if a command fails -e
# Don't ignore non-existent variables -u
set -eu

# Define image and container information
DOCKERFILE_PATH="$( pwd )/Dockerfile"
REPOSITORY="scrapy-env"
TAG="1.0"
LOCAL_PORT=6800
CONTAINER_NAME="${REPOSITORY}"
CONTAINER_PORT=6800

SYNC_DIR=$( pwd )
CONTAINER_WORKDIR=/usr/local/mops-crawler

SYNC_EGGS_DIR=/var/scrapyd
SYNC_LOGS_DIR=/var/scrapyd


CONTAINER_EGGS_DIR=/var/scrapyd
CONTAINER_LOGS_DIR=/var/scrapyd

CHECK_DIRS=( "${SYNC_EGGS_DIR}" "${SYNC_LOGS_DIR}" )
for dir in "${CHECK_DIRS[@]}";
do
    if [ ! -d ${dir} ];then
        mkdir -p ${dir}
    fi
done

# Check image whether it exists or not
BUILD_OR_NOT=$( docker images --filter=reference="${REPOSITORY}:${TAG}"\
         --format '{{.ID}}' | wc -l )

if [ ${BUILD_OR_NOT} -eq 0 ];then
    echo "Build image with repository: ${REPOSITORY}, tag: ${TAG}...."
    docker build --file ${DOCKERFILE_PATH} --tag ${REPOSITORY}:${TAG} --no-cache .
fi

# Check container whether it eixsts or not
CONTAINER_EXISTS_OR_NOT=$(
    docker ps -a --filter "name=${CONTAINER_NAME}"\
        --format "{{.Names}}" | wc -l
)

if [ ${CONTAINER_EXISTS_OR_NOT} -eq 0 ];then
    echo "Build container with ${REPOSITORY}:${TAG} image....."
    docker run --name ${CONTAINER_NAME}\
            -p ${LOCAL_PORT}:${CONTAINER_PORT}\
            -v "${SYNC_DIR}/mops_crawler":"${CONTAINER_WORKDIR}/mops_crawler"\
            -v "${SYNC_DIR}/company_info":"${CONTAINER_WORKDIR}/company_info"\
            -v "${SYNC_EGGS_DIR}/eggs":"${CONTAINER_EGGS_DIR}/eggs"\
            -v "${SYNC_LOGS_DIR}/logs":"${CONTAINER_LOGS_DIR}/logs"\
            -it -d ${REPOSITORY}:${TAG}
fi

restart_container() {
    local STATUS=${1}
    local EXECUTED_COMMAND

    case ${STATUS} in 
        "exited")
            EXECUTED_COMMAND="start"
        ;;
        "paused")
            EXECUTED_COMMAND="unpause"
        ;;
    esac
    CHECKED_RESULT=$( 
        docker ps -a --filter name=${CONTAINER_NAME}\
            --filter status=${STATUS}\
            --format "{{.ID}}" | wc -l
    )

    if [ ${CHECKED_RESULT} -eq 1 ];then
        echo "Container is ${STATUS}, ${EXECUTED_COMMAND} it now....."
        docker container ${EXECUTED_COMMAND} ${CONTAINER_NAME}
    elif [ ${CHECKED_RESULT} -eq 1 ] && [ -z ${EXECUTED_COMMAND} ];then
        echo "Container: ${CONTAINER_NAME} is ${STATUS}...."
    fi
}

echo "Check container status....."
CHECKED_STATUS=( "exited" "paused" )
for status in "${CHECKED_STATUS[@]}";
do
    restart_container ${status}
done

echo "Finish run container => ${CONTAINER_NAME}"

# Reference:
#  - Docker images cli: https://docs.docker.com/engine/reference/commandline/images/
#  - Using Linux set command: https://www.networkworld.com/article/3631415/using-the-linux-set-command.html