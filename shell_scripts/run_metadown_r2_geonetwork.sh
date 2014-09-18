source ~/.bash_profile
workon harvest_test

cd $CATALOG_SOURCE

cd metadown
python download.py -g $METADOWN_DATA
cd ..

cd basex
python git_consistent_update.py -d $METADOWN_DATA -n $GLOS_DB
cd ..
