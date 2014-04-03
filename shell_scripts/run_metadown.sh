source ~/.bash_profile
workon harvest_test

cd $CATALOG_SOURCE

cd metadown
python download.py $METADOWN_DATA
cd ..

cd basex
python git_consistent_update.py -d $METADOWN_DATA -n test_glos
cd ..
