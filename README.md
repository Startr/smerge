# 

# Archived Project 

For new development go to https://github.com/Startr/codezy/

Codezy is a merge tool for school environments and Snap!. It is based on a lot of open source projects including cytoscape.js or Django. It is intended to be simple, beautiful, fast, and easy to use in school environments. A live demo can be found at [Codezy.org](https://Codezy.org)

# Install

You will need pip and Python 3 for installing Codezy on your server.
We recommend using a virtualenv and npm for local deployment. Activate your virtualenv and use

## With docker

To deploy Codezy via docker you may use our BuildnRun.sh script:

```bash
BuildnRun.sh
```

This will automaticly run 

```bash
# OpenCo Build 'n' Run Script
#!/bin/bash
# Version 1.0.1

# This simple script builds and runs this directory 's Dockerfile Image
PROJECTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    PROJECT=${PROJECTPATH##*/}
FULL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
# Lowecase the branch
FULL_BRANCH=`echo $FULL_BRANCH|awk '{print tolower($0)}'`
     BRANCH=${FULL_BRANCH##*/}
        TAG=$(git describe --always --tag)

echo PROJECTPATH=$PROJECTPATH
echo     PROJECT=$PROJECT
echo FULL_BRANCH=$FULL_BRANCH
echo      BRANCH=$BRANCH

echo docker build -t openco/$PROJECT-$BRANCH:$TAG .
echo docker tag -f openco/$PROJECT-$BRANCH:$TAG
echo   openco/$PROJECT-$BRANCH:latest
docker build -t openco/$PROJECT-$BRANCH:$TAG . \
  && \
docker tag openco/$PROJECT-$BRANCH:$TAG \
 openco/$PROJECT-$BRANCH:latest \
  && \
  ./Run.sh
```

## Without docker

```
pip install -r requirements.txt
npm install
```

and then the command

```
make run
```

In case, you have unapplied migrations, first run:

```
make migrate
```

We recommend to test the system using a redis docker. Redis is used for handling all websocket related actions:

```
docker run -p 6379:6379 --name some-redis -d redis
```

TODO Move redis into our Codezy Docker image


# Contributing

Thank you for considering contributing to Codezy! It's as easy as creating a pull request.

# License



RIAC Cloud is licenced under the AGPLv3 and builds on SMERGE.

SMERGE is licenced under the MIT license. 
Licence for third-party libraries may differ and those licences apply in those cases.

# etc.

To import initial data use:
manage.py loaddata snapmerge/fixtures/initial_data.json
