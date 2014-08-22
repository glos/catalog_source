Catalog Source
============
Source code and configuration files for the GLOS Catalog

Uses environmental variables:

    BASEX_SERVER    (no default)
    BASEX_PORT      (1984)
    BASEX_USER      (no default)
    BASEX_PASS      (no default)
    METADOWN_DATA   (~/metadown_r2/metadown_r2_data
    CATALOG_SOURCE  (~/metadown_r2/catalog_source
    GLOS_DB         (glos)

Uses virtual envs:
    harvest         (swh harvest)
    harvest_test    (metadown r2)

Use basex client
./basexclient -n 64.9.200.113 -p 1984 -P glos -U user
  
  
===Indexes

Up-to-date: true
Text Index: ON
Attribute Index: ON
Full-Text Index: ON
