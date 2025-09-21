from ftplib import FTP, FTP_TLS, error_reply, error_perm
import ssl
import os
from io import IOBase, BytesIO
from pathlib import Path
import posixpath
from datetime import datetime
from dateutil import parser
import re
from dateutil.relativedelta import relativedelta
from itertools import chain
from typing import Optional, List, Union

class FTPClient:
    def __init__(self, host: str, user: str, password: str, secure: bool, passive: bool=True, **kwargs) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.passive = passive

        self.port = kwargs.pop("port", 21)
        self.encoding = kwargs.pop("encoding", "utf-8")
        self.timeout = kwargs.pop("timeout", None)
        self.acct = kwargs.pop("acct", "")
        self.source_address = kwargs.pop("source_address", None)
        self.ssl_version = kwargs.pop("ssl_version", ssl.PROTOCOL_TLS_CLIENT)

        if secure:
            self.context = kwargs.pop("context", None)
            self.conn = FTP_TLS(encoding=self.encoding, context=self.context) 
            self.conn.ssl_version = self.ssl_version
            self.conn.auth()
        else:
            self.conn = FTP(encoding=self.encoding)

        self.conn.connect(host=self.host, port=self.port, timeout=self.timeout, source_address=self.source_address)
        self.conn.login(user=self.user, passwd=self.password, acct=self.acct)

        if secure:
            self.conn.prot_p() # type: ignore
        
        self.conn.set_pasv(self.passive)
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.conn.quit()
        except:
            self.conn.close()

    def set_debug_level(self, level: int) -> None:
        """Sets the debug level of ftplib"""
        self.conn.set_debuglevel(level)
    
    def get_welcome(self) -> str:
        """Gets the server's welcome message"""
        return self.conn.getwelcome()
    
    def abort(self) -> str:
        """Attempts to abort a file transfer."""
        return self.conn.abort()

    def quit(self) -> None:
        """
        Requests the server to quit the connection. 
        If that fails, closes the connection without assuming anything about it
        """
        try:
            self.conn.quit()
        except:
            self.conn.close()
    
    def get_features(self) -> List[str]:
        """
        Returns a list of the FTP server's supported features
        """
        features = self.conn.sendcmd("FEAT").split("\n")
        features = [item for item in features if "211" not in item and item]
        features = [item.strip() for item in features]
        return features
    
    def get_mlst_features(self) -> List[str]:
        """"""
        features = self.get_features()
        if len([item.split(" ")[0] for item in self.get_features() if "MLST" in item]) == 0:
            raise ValueError("MLST not supported by FTP server")
        mlst_features = [item.split(";") for item in features if "MLST" in item][0]
        mlst_features = [item.split(" ") for item in mlst_features]
        mlst_features = list(chain(*mlst_features))
        mlst_features = [item.replace("*", "") for item in mlst_features if item]
        mlst_features.pop(0)
        return mlst_features

    def ls(self, remote_path=".", detailed_listing=False, mlst_listing_facts: Optional[list] = None) -> Union[List[str], List[dict]]:
        """
        Returns a list of the directories/files on the current working directory.
        
        If the `detailed_listing` argument is set to `True`, 
        then FTPClient.ls() will return a more detailed listing, hence the name.
        
        `mlst_listing_facts` is an argument that allows you to control what metadata
        you would like to have returned when `detailed_listing` is set to True.
        
        More information can be found in the docs.
        """
        
        if mlst_listing_facts is None:
            mlst_listing_facts = []


        if not detailed_listing:
            return self.conn.nlst(remote_path)

        features = [line.lower() for line in self.get_features()]
        mlsd_supported = any("mlst" in feature or "mlsd" in feature for feature in features)

        if mlsd_supported:
            possible_facts = {f.lower() for f in self.get_mlst_features()}
            for fact in mlst_listing_facts:
                if fact.lower() not in possible_facts:
                    raise ValueError(f"MLSD fact '{fact}' not supported by server")

            try:
                return [{"name": name, "facts": facts} for name, facts in self.conn.mlsd(remote_path, mlst_listing_facts)]
            except Exception:
                pass

        temp_output = []
        self.conn.dir(remote_path, temp_output.append)
        return _split_file_info(temp_output)

    def cd(self, remote_path = ".", force=False) -> Union[str, List[str]]:
        """Changes the current working directory."""
        if force:
            responses = []
            path = Path(remote_path).as_posix()
            parts = [p for p in path.split("/") if p]
            for item in parts:
                try:
                    responses.append(self.conn.cwd(item))
                except (error_reply, error_perm):
                    responses.append(self.conn.mkd(item))
                    responses.append(self.conn.cwd(item))
            
            return responses
            
        return self.conn.cwd(remote_path)

    def pwd(self) -> str:
        """Returns the current working directory."""
        return self.conn.pwd()

    def rename(self, from_name: str, to_name: str) -> str:
        """Renames file `from_name` to `to_name`"""
        return self.conn.rename(from_name, to_name)
    
    def mkdir(self, remote_path: str, force=False) -> List[str]:
        """Creates a new directory on the server and returns its path name"""
        if not force:
            return [self.conn.mkd(remote_path)]
        
        responses = []
        current_directory = self.conn.pwd()
        responses.append(self.cd(remote_path, force=True))
        responses.append(self.conn.cwd(current_directory))
        return responses
    
    def get_filesize(self, file_path: str) -> Optional[int]:
        """Gets the size of a file"""
        try:
            return self.conn.size(file_path)
        except Exception:
            return None
    
    def delete(self, remote_path: str) -> str:
        """Deletes the item from the server"""
        try:
            return self.conn.delete(remote_path)
        except (error_reply, error_perm):
            return self.conn.rmd(remote_path)
    
    def put(self, local_file_path, remote_file_path, block_size=8192) -> dict:
        """Uploads a file onto the server."""
        file_to_upload = local_file_path
        if not isinstance(local_file_path, IOBase):
            file_to_upload = open(local_file_path, "rb")

        try:    
            response = self.conn.storbinary(f"STOR {remote_file_path}", file_to_upload, block_size)
        except Exception as exc:
            return {
                "local_file": local_file_path,
                "remote_file": remote_file_path,
                "status": "ERROR",
                "additional_notes": (type(exc).__name__, str(exc))
            }

        return {
            "local_file": local_file_path,
            "remote_file": remote_file_path,
            "status": "OK",
            "additional_notes": response
        }

    def put_content(self, local_contents, remote_file_path, block_size=8192, overwrite=False):
        """Overwrites a file remotely. 
        (i.e. you don't have to get the file, edit it and then put it. This method saves bandwidth)"""
        content_to_put = BytesIO(local_contents)
        command = "STOR" if overwrite else "APPE"
        try:
            response = self.conn.storbinary(f"{command} {remote_file_path}", content_to_put, block_size)
        except Exception as exc:
            return {
                "local_contents": local_contents,
                "remote_file": remote_file_path,
                "status": "ERROR",
                "additional_notes": (type(exc).__name__, str(exc))
            }

        return {
            "local_contents": local_contents,
            "remote_file": remote_file_path,
            "status": "OK",
            "additional_notes": response
        }

    def put_tree(self, local_item_path, remote_item_path, ignore_items=None, block_size=8192) -> List[dict]:
        """Uploads a tree to the server"""
        try:
            files = os.listdir(local_item_path)
        except Exception as exc:
            return [{"local_path": local_item_path, "remote_path": remote_item_path,
                     "status": "ERROR", "additional_notes": (type(exc).__name__, str(exc))}]
        
        ignore_items = set(ignore_items) if ignore_items is not None else set()

        self.mkdir(remote_item_path, force=True)
                
        responses = []

        for name in files:
            local_path = os.path.join(local_item_path, name)
            remote_path = posixpath.join(Path(remote_item_path).as_posix(), name)
            if name in ignore_items:
                responses.append({"local_path": local_path, "remote_path": remote_path,
                                  "status": "SKIPPED", "additional_notes": "ignored"})
                continue
            try:

                if os.path.islink(local_path):
                    responses.append({"local_path": local_path, "remote_path": remote_path, 
                                      "status": "SKIPPED", "additional_notes": "symlink"})
                    
                elif os.path.isdir(local_path):
                    responses.extend(self.put_tree(local_path, remote_path, ignore_items))

                else:
                    response = self.put(local_path, remote_path, block_size)
                    responses.append({"local_path": local_path, "remote_path": remote_path,
                                      "status": "OK", "additional_notes": response})
            except Exception as exc:

                responses.append({"local_path": local_path, "remote_path": remote_path,
                                  "status": "ERROR", "additional_notes": (type(exc).__name__, str(exc))})

        return responses
    
    def get(self, remote_path, local_path=None, block_size=8192) -> dict:
        """Retrieves a file from the server"""
        local_file = local_path or os.path.basename(remote_path) 
        close_file = False
        
        if not isinstance(local_path, IOBase):
            local_file = open(local_path, "wb") # type: ignore
            close_file = True
        
        try:
            response = self.conn.retrbinary(f"RETR {remote_path}", local_file.write, blocksize=block_size)
        except Exception as exc:
            return {
                "local_path": local_path,
                "remote_path": remote_path,
                "status": "ERROR",
                "additional_notes": (type(exc).__name__, str(exc))
            }
        finally:
            if close_file:
                local_file.close()

        return {
            "local_path": local_path,
            "remote_path": remote_path,
            "status": "OK",
            "additional_notes": response
        }
    
    def get_content(self, remote_path, local_path=None, block_size=8192) -> dict:
        """Retrieves the contents of a file from the server"""
        local_file = local_path or BytesIO()
        close_file = False
        
        if not isinstance(local_path, IOBase) and not isinstance(local_path, BytesIO):
            local_file = open(local_path, "wb") # type: ignore
            close_file = True
        
        try:
            response = self.conn.retrbinary(f"RETR {remote_path}", local_file.write, blocksize=block_size)
        except Exception as exc:
            return {
                "contents": None,
                "local_path": local_path,
                "remote_path": remote_path,
                "status": "ERROR",
                "additional_notes": (type(exc).__name__, str(exc))
            }
        finally:
            if close_file:
                local_file.close()
        

        if local_path is None:
            contents = local_file.getvalue()
            return {
                "contents": contents,
                "local_path": local_path,
                "remote_path": remote_path,
                "status": "OK",
                "additional_notes": response
            }
        
        return {
            "contents": None,
            "local_path": local_path,
            "remote_path": remote_path,
            "status": "OK",
            "additional_notes": response
        }

    def _get_tree_mlst_supported(self, remote_tree, local_path, block_size=8192):
        remote_tree = Path(remote_tree).as_posix()
        os.makedirs(local_path, exist_ok=True)
        responses = []

        for entry in self.ls(remote_tree, detailed_listing=True, mlst_listing_facts=["type"]):
            name = entry["name"]  # type: ignore
            remote_path = posixpath.join(remote_tree, name)
            local_file_path = os.path.join(local_path, name)

            if entry["facts"]["type"] == "dir":  # type: ignore
                responses.extend(self._get_tree_mlst_supported(remote_path, local_file_path, block_size))
            elif entry["facts"]["type"] == "file":  # type: ignore
                responses.append(self.get(remote_path, local_file_path))
            else:
                continue

        return responses
    
    def _get_tree_mlst_unsupported(self, remote_tree, local_path, block_size=8192):
        remote_tree = Path(remote_tree).as_posix()
        os.makedirs(local_path, exist_ok=True)
        responses = []

        for entry in self.ls(remote_tree, detailed_listing=True):
            name = entry["name"] # type: ignore
            remote_path = posixpath.join(remote_tree, name)
            local_file_path = os.path.join(local_path, name)

            if entry["flags"] == 'd': # type: ignore
                responses.extend(self._get_tree_mlst_unsupported(remote_path, local_file_path, block_size))
            elif entry["flags"] == '-': # type: ignore
                responses.append(self.get(remote_path, local_file_path))

        return responses

    def get_tree(self, remote_tree, local_path, block_size=8192) -> List[dict]:
        """Retrieves an entire tree from the server."""
        features = [line.upper() for line in self.get_features()]
        mlst_supported = any("MLST" in f or "MLSD" in f for f in features)

        if mlst_supported:
            return self._get_tree_mlst_supported(remote_tree, local_path, block_size)
        return self._get_tree_mlst_unsupported(remote_tree, local_path, block_size)        

def _get_year(date: str):
    current_date = datetime.now()
    parsed_date = parser.parse(date)
    if current_date > parsed_date:
        current = current_date
    else:
        current = current_date - relativedelta(years=1)
    return current.strftime('%Y')

def _split_file_info(fileinfo):
    """
    Makes something returnable out of ftplib.FTP.dir()
    I have no idea what the code below does, thank you codebynumbers for writing this for me. 
    """
    files = []

    unix_format = re.compile(
        r'^([\-dbclps])' +                  # Directory flag [1]
        r'((?:[r-][w-][-xsStT]){3})\s+' +   # Permissions [2]
        r'(\d+)\s+' +                       # Number of items [3]
        r'([a-zA-Z0-9_-]+)\s+' +            # File owner [4]
        r'([a-zA-Z0-9_-]+)\s+' +            # File group [5]
        r'(\d+)\s+' +                       # File size in bytes [6]
        r'(\w{3}\s+\d{1,2})\s+' +           # 3-char month and 1/2-char day of the month [7]
        r'(\d{1,2}:\d{1,2}|\d{4})\s+' +     # Time or year (need to check conditions) [+= 7]
        r'(.+)$'                            # File/directory name [8]
    )

    windows_format = re.compile(
        r'(\d{2})-(\d{2})-(\d{2})\s+' +     # month/day/2-digit year (assuming after 2000)
        r'(\d{2}):(\d{2})([AP])M\s+' +      # time
        r'(\d+)\s+' +                       # file size
        r'(.+)$'                            # filename
    )

    for line in fileinfo:
        if unix_format.match(line):
            parts = unix_format.split(line)

            date = parts[7]
            time = parts[8] if ':' in parts[8] else '00:00'
            year = parts[8] if ':' not in parts[8] else _get_year(date)
            dt_obj = parser.parse("%s %s %s" % (date, year, time))

            files.append({
                'directory': parts[1],
                'flags': parts[1],
                'perms': parts[2],
                'items': parts[3],
                'owner': parts[4],
                'group': parts[5],
                'size': int(parts[6]),
                'date': date,
                'time': time,
                'year': year,
                'name': parts[9],
                'datetime': dt_obj
            })

        elif windows_format.match(line):
            parts = windows_format.split(line)

            hour = int(parts[4])
            hour += 12 if parts[6] == 'P' else 0
            hour = 0 if hour == 24 else hour
            year = int(parts[3]) + 2000
            dt_obj = datetime(year, int(parts[1]), int(parts[2]), hour, int(parts[5]), 0)

            files.append({
                'directory': None,
                'flags': None,
                'perms': None,
                'items': None,
                'owner': None,
                'group': None,
                'size': int(parts[7]),
                'date': "{}-{}-{}".format(*parts[1:4]),
                'time': "{}:{}{}".format(*parts[4:7]),
                'year': year,
                'name': parts[8],
                'datetime': dt_obj
            })

    return files

