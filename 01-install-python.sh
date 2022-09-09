#!/bin/bash

if ! command -v python3 &> /dev/null; then
    echo "**** installing python3 ****"
    if command -v apk &> /dev/null; then
        apk update
        apk --no-cache add python3
    elif command -v apt-get &> /dev/null; then
        export DEBIAN_FRONTEND=noninteractive
        apt-get -qq update
        apt-get -qq install --no-install-recommends --yes python3
        rm -rf /var/lib/apt/lists/*
    fi
fi
