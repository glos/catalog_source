source ~/.bash_profile

workon harvest_test

cd $CATALOG_SOURCE


cd metadown
python download.py $METADATA_DIR
cd ..

cd basex
python git_consistent_update.py -d $METADATA_DIR -n test_glos
 
cd ..
