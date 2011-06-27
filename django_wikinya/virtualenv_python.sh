#!/bin/bash
PROJECT_ROOT=$(pwd)
ENV_ROOT=${PROJECT_ROOT}/.env/
REQUIREMENTS=${PROJECT_ROOT}/requirements.txt

function init_env() {
    virtualenv --python=python2 ${ENV_ROOT} --no-site-packages
    source ${ENV_ROOT}/bin/activate
    pip2 install -r ${REQUIREMENTS} -E ${ENV_ROOT} --upgrade
    deactivate
    touch ${ENV_ROOT}.timestamp
}


echo ${REQUIREMENTS}

if [ ! -d "${ENV_ROOT}" ]; then
    init_env
else
    last_update_env=$(stat ${ENV_ROOT}/.timestamp -c "%Y")
    last_update_requirements=$(stat ${REQUIREMENTS} -c "%Y")
    echo $last_update_env $last_update_requirements
    if [ "${last_update_env}" -lt "${last_update_requirements}" ]; then
        init_env
    fi
fi

source ${ENV_ROOT}/bin/activate
${ENV_ROOT}/bin/python $*
deactivate
