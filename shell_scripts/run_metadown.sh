source ~/.bash_profile

cd $CATALOG_SOURCE


cd metadown
python download.py $METADATA_DIR
cd ..

cd basex
python git_consistent_update.py
 
cd ..
