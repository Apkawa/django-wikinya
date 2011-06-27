#!/bin/bash
PROJECT_ROOT=$(pwd)
ENV_ROOT=${PROJECT_ROOT}/.env/
REQUIREMENTS=${PROJECT_ROOT}/requirements.txt
TIMESTAMP=${ENV_ROOT}.timestamp


function init_env() {
    virtualenv --python=python2 ${ENV_ROOT} ||return 1 #--no-site-packages
    source ${ENV_ROOT}/bin/activate
    pip2 install -r ${REQUIREMENTS} -E ${ENV_ROOT} ||return 1 #--upgrade
    deactivate
    touch ${TIMESTAMP}
}


echo ${REQUIREMENTS}

if [ ! -d "${ENV_ROOT}" -o ${REQUIREMENTS} -nt ${TIMESTAMP} ]; then
    init_env
fi

source ${ENV_ROOT}/bin/activate
${ENV_ROOT}/bin/python $*
deactivate
