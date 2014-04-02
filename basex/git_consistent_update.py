import os
import sys
import xml.dom.minidom

import BaseXClient

from git import Repo
from git.exc import GitCommandError

class GitConsistentUpdateException(Exception):
    pass

def readXml(filename):
    doc = xml.dom.minidom.parse(filename)
    content = doc.toxml()    
    return content

    
class ControlledUpdate(object):
    """
    Use a with context manager to make sure that only changes which are successful in 
    basex are staged to git.
    """
    def __init__(self, repo, session):    
        self._repo = repo
        self._session = session
        self._messages = []

    @property
    def repo_dir(self):
        return os.path.split(self._repo.git_dir)[0]
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        commit_message = 'Metadown generated content add'
        
        if value is not None:
            print value, type, type(traceback)
            commit_message += '\nbut error type %s stopped the update!' % type
    
        if len(self._messages) > 0:
            for message in self._messages:
                print "file '%s' Raised Exception '%s' during operation %s" %(message[0],message[2],message[4])
                
            commit_message +=  'During update, %s errors occurred !' % len(self._messages)
        
        self._repo.index.commit(commit_message)
        
        for remote in self._repo.remotes:
            remote.push()
    
    def add_message(self,*args):
        self._messages.append(args)
        
class ContextBase(object):
    """
    Use a with context manager to make sure that only changes which are successful in 
    basex are staged to git.
    """
    def __init__(self, controlled_update):    
        self._cu = controlled_update
        self._index = controlled_update._repo.index
        self._repo = controlled_update._repo
        self._session = controlled_update._session
        self._file = None

    @property
    def repo_dir(self):
        return os.path.split(self._repo.git_dir)[0]

    
class ControlledInsert(ContextBase):
    """
    Unfortunately, the basexclient methods do not have a return value
    They do throw an error (IOError) if the operation fails
    Add will work even if the file exists in basex
    """
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        if type is not None:
            self._cu.add_message(self._file, type, value, traceback,self.__class__.__name__)
        # Fail if there is a git error
        return not isinstance(value, GitCommandError)
        
    def insert_file(self, file):
        self._file = file
        fpath = os.path.join(self.repo_dir, file)
        self._session.add(file, readXml(fpath))
        self._index.add([file,])
        
class ControlledReplace(ContextBase):
    """
    Replace will work even if the file does not exist in basex
    """
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        if type is not None:
            self._cu.add_message(self._file, type, value, traceback,self.__class__.__name__)
        # Fail if there is a git error
        return not isinstance(value, GitCommandError)
        
    def replace_file(self, file):
        self._file = file
        fpath = os.path.join(self.repo_dir, file)
        self._session.replace(file, readXml(fpath))
        self._index.add([file,])
        
class ControlledRemove(ContextBase):
    """
    Delete will work even if the file is not in basex
    """
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        if type is not None:
            self._cu.add_message(self._file, type, value, traceback,self.__class__.__name__)
        # Fail if there is a git error
        return not isinstance(value, GitCommandError)
    
    def remove_file(self, file):
        self._file = file
        self._session.execute("DELETE "+file)
        self._index.remove([file,])
    
    
def main(base_server, base_user, base_pass, base_port=1984, db_name='', git_metadata_dir='', new_db=False):
    """
    repository is a path to the glos_catalog repository
    directory is a path relative to root of the repository
    """
    
    # create session
    session = BaseXClient.Session(base_server, base_port, base_user, base_pass)
    
    if db_name == '':
        raise GitConsistentUpdateException('Invalid db_name not specified!')
    
    if new_db:
        session.create(db_name,'')
        session.execute("CREATE INDEX FULLTEXT")
        session.execute("CREATE INDEX TEXT")
        session.execute("CREATE INDEX ATTRIBUTE")
    else:
        session.execute("OPEN " + db_name)

    print(session.info())

    #### Get the REPO object ####
    # Reinitialize every time - it is idempotent
    repo = Repo.init(git_metadata_dir)
    
    # get the command line caller:
    cmdgit = repo.git
    
    # keep historical option to specify a single directory to update
    directory = None
    other_files = set(cmdgit.ls_files('--others','--full-name', directory).split('\n'))
    cached_files = set(cmdgit.ls_files('--cached','--full-name', directory).split('\n'))
    modified_files = set(cmdgit.ls_files('--modified','--full-name', directory).split('\n'))
    
    unmodified_files = cached_files.difference(modified_files)
    ####
    
    
    with ControlledUpdate(repo, session) as cu:
    
        for fname in other_files:
            with ControlledInsert(cu) as ci:
                ci.insert_file(fname)
    
        for fname in modified_files:
            with ControlledReplace(cu) as cr:
                cr.replace_file(fname)
    
        for fname in unmodified_files:
            with ControlledRemove(cu) as cr:
                cr.remove_file(fname)
    
    if session:
        session.execute("OPTIMIZE ALL")
        print session.info()
        session.close()


if __name__ == "__main__":


    base_server = os.environ.get("BASEX_SERVER", 'localhost')
    base_port = os.environ.get("BASEX_PORT", 1984)
    base_user = os.environ.get("BASEX_USER",'admin')
    base_pass = os.environ.get("BASEX_PASS",'admin')
   
    git_metadata_dir = '/Users/dstuebe/code/glos/metadata'
    db_name = "foobar"
    new_db = False
    
    
    main(base_server, base_user, base_pass, base_port, db_name, git_metadata_dir, new_db)

