import os
import sys
import xml.dom.minidom

import BaseXClient

from git import Repo

class GitConsistentUpdateException(Exception):
    pass

def readXml(filename):
    doc = xml.dom.minidom.parse(filename)
    content = doc.toxml()    
    return content


class ControlledUpdate:
    """
    Use a with context manager to make sure that only changes which are successful in 
    basex are staged to git.
    """
    def __init__(self, repo, session)
    
        self._repo = repo
        self._session = session

    @attribute
    def repo_dir():
        return os.path.split(self._repo.git_dir)[0]


    def __enter__(self):
        """
        On enter into the context statement - determine which files will be updated,
        add or removed. 
        """
        pass

        
    def __exit(self, type, value, traceback):
        pass
    

    # Don't really need separate methods
    def remove_unmodified_file(file):
        pass
    
    def update_modified_file(file):
        fpath = os.path.join(self.repo_dir, file)
        session.replace(dbpath, readXml(fpath))

    def add_other_file(file):
    




def main(repository=None, directory=None, include_files=None):
    """
    repository is a path to the glos_catalog repository
    directory is a path relative to root of the repository
    
    """

    try:
        base_server = os.environ["BASEX_SERVER"]
        base_port = os.environ.get("BASEX_PORT", 1984)
        base_user = os.environ["BASEX_USER"]
        base_pass = os.environ["BASEX_PASS"]
    except KeyError:
        raise GitConsistentUpdateException("Please set environmental variables 'BASEX_SERVER', 'BASEX_PORT', 'BASEX_USER' & 'BASEX_PASS'"))

    # create session
    session = BaseXClient.Session(base_server, base_port, base_user, base_pass)
    session.execute("OPEN glos")
    print(session.info())

    print "Updating XML from DIR: '", directory, "'"

    #### get the files to update ####
    # get the command line caller:
    cmdgit = repo.git
    
    other_files = set(cmdgit.ls_files('--others','--full-name', directory).split('\n'))
    cached_files = set(cmdgit.ls_files('--cached','--full-name', directory).split('\n'))
    modified_files = set(cmdgit.ls_files('--modified','--full-name', directory).split('\n'))
    
    unmodified_files = cached_files.difference(modified_files)
    ####

   
    with ControlledUpdate() as cu:
    
        for fname in other_files:
            with ControlledInsert() as ci:            
                ci.insert(fname)
   
       for fname in modified_files:
            with ControlledReplace() as cr:            
                cr.replace(fname)
   
       for fname in unmodified_files:
            with ControlledDelete() as cr:            
                cr.replace(fname)
   

    # Only process files that contain the string 'include_files'
    if include_files is not None:
        if include_files not in dbpath:
            continue

    print "Updating %s..." % dbpath
    session.replace(dbpath, readXml(fpath))
    
    except Exception as e:
        print(repr(e))
    
    finally:
        # close session
        session.execute("CREATE INDEX FULLTEXT")
        if session:
            session.close()

directory = None
if sys.argv[1] is not None:
    directory = sys.argv[1]
    
files = None    
if sys.argv[2] is not None and sys.argv[2].lower() != "all":
    files = sys.argv[2]

main(directory=directory, include_files=files)

