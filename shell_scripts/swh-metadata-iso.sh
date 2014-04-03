#!/bin/bash
#source ~/.bash_profile
workon harvest_test

cd $CATALOG_SOURCE

function swh_update() {
    cd SWH
    java -jar sensor-web-harvester-0.12-SNAPSHOT.jar -metadata $1
    java -jar sensor-web-harvester-0.12-SNAPSHOT.jar -writeiso $1
    cd ..

    cd basex
    python git_consistent_update.py -d $SWH_DATA  -n test_glos
    cd ..
}

swh_update "glos.props"


