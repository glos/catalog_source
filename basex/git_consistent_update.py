import os
import sys
import xml.dom.minidom
from metadown.utils.etree import etree
import datetime
import time
import BaseXClient

from git import Repo
from git.exc import GitCommandError

from optparse import OptionParser

class GitConsistentUpdateException(Exception):
    pass

#  import ipdb; ipdb.set_trace()

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

        self.inserted = 0
        self.removed = 0
        self.replaced = 0
        self.purgatory = 0

    @property
    def repo_dir(self):
        return os.path.split(self._repo.git_dir)[0]    
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        commit_message = 'Metadown generated content: added - %s, replaced - %s, purgatory - %s, removed - %s' % (self.inserted, self.replaced, self.purgatory, self.removed)
        
        if len(self._messages) > 0:
            for message in self._messages:
                print "file '%s' Raised Exception '%s' during operation %s" %(message[0],message[2],message[4])
              
            commit_message +=  '\nDuring update, %s errors occurred !' % len(self._messages)  
        
        if value is not None:
            print value, type, type(traceback)
            commit_message += '\nbut error type %s stopped the update!' % type
    
        
            
        
        self._repo.index.commit(commit_message)
        
        for remote in self._repo.remotes:
            remote.pull()
        
        for remote in self._repo.remotes:
            remote.push()
            
        # clean up any files that were removed
        cmdgit = self._repo.git
        cmdgit.clean('-f','-d')
    
    
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
        else:
            self._cu.inserted += 1
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
        else:
            self._cu.replaced += 1
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
        else:
            self._cu.removed += 1
        # Fail if there is a git error
        return not isinstance(value, GitCommandError)
    
    def remove_file(self, file):
        self._file = file
        self._session.execute("DELETE "+file)
        self._index.remove([file,])
    
    
def main(base_server, base_user, base_pass, base_port=1984, db_name='', git_metadata_dir='', new_db=False, t2l=24):
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
    other_files = set(cmdgit.ls_files('--others','--full-name', directory).split())
    cached_files = set(cmdgit.ls_files('--cached','--full-name', directory).split())
    modified_files = set(cmdgit.ls_files('--modified','--full-name', directory).split())
    
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
        
            if expired(os.path.join(cu.repo_dir, fname)) > t2l:        
                with ControlledRemove(cu) as cr:
                    cr.remove_file(fname)
            else:
                cu.purgatory += 1
            
    
    if session:
        session.execute("OPTIMIZE ALL")
        print session.info()
        session.close()


def expired(fname):
    namespaces = {
    "gmx":"http://www.isotc211.org/2005/gmx",
    "gsr":"http://www.isotc211.org/2005/gsr",
    "gss":"http://www.isotc211.org/2005/gss",
    "gts":"http://www.isotc211.org/2005/gts",
    "xs":"http://www.w3.org/2001/XMLSchema",
    "gml":"http://www.opengis.net/gml/3.2",
    "xlink":"http://www.w3.org/1999/xlink",
    "xsi":"http://www.w3.org/2001/XMLSchema-instance",
    "gco":"http://www.isotc211.org/2005/gco",
    "gmd":"http://www.isotc211.org/2005/gmd",
    "gmi":"http://www.isotc211.org/2005/gmi",
    "srv":"http://www.isotc211.org/2005/srv",
    }

                
    # Always modify date stamp!
    root = etree.parse(fname)
    
    x_res = root.xpath(
    'gmd:dateStamp/gco:DateTime', 
    namespaces=namespaces
    )
    
    dt = x_res[0].text
    d  = datetime.datetime.strptime( dt[:-7], "%Y-%m-%dT%H:%M:%S" )

    delta = time.mktime(datetime.datetime.now().timetuple()) - time.mktime(d.timetuple())

    
    return delta / (3600.)


if __name__ == "__main__":

    # Keep these here so it is easy to copy for interactive execution
    base_server = os.environ.get("BASEX_SERVER", 'localhost')
    base_port = os.environ.get("BASEX_PORT", 1984)
    base_user = os.environ.get("BASEX_USER",'admin')
    base_pass = os.environ.get("BASEX_PASS",'admin')
   
    git_metadata_dir = '../../metadata'
    db_name = "glos"
    new_db = False


    parser = OptionParser()
    parser.add_option("-s", "--server", dest="base_server", help="The hostname or IP of the basex server", type="string", default=base_server)
    parser.add_option("-p", "--port", dest="base_port", help="The port number for the basex server", type="string", default=base_port)
    parser.add_option("-u", "--user", dest="base_user", help="The user naem for the basex server", type="string", default=base_user)
    parser.add_option("-w", "--password", dest="base_pass", help="The password for the basex server", type="string", default=base_pass)
    parser.add_option("-d", "--dir", dest="git_metadata_dir", help="The git directory where the metadata lives", type="string", default=git_metadata_dir)
    parser.add_option("-n", "--dbname", dest="db_name", help="The name of the basex database", type="string", default=db_name)
    parser.add_option("-c", "--create", dest="new_db", help="The name of the basex database", action='store_true')
    parser.add_option("-t", "--timetolive", dest="t2l", help="The time to live in hours after a dataset is removed", type="int", default=24)
    
    (options, args) = parser.parse_args()

    main(**options.__dict__)

