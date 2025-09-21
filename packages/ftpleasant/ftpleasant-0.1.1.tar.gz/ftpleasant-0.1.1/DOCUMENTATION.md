# `ftpleasant` : Documentation

---

> This module supports Python versions 3.7+, but this documentation uses 3.10+ type annotations for legibility

---

## Table of Contents

- [Initialising an FTPClient object](#topic_1)
- [`set_debug_level()`](#topic_2)
- [`get_welcome()`](#topic_3)
- [`abort()`](#topic_4)
- [`quit()](#topic_5)
- [`get_features()`](#topic_6)
- [`get_mlst_features()`](#topic_7)
- [`ls()`](#topic_8)
- [`cd()`](#topic_9)
- [`pwd()`](#topic_10)
- [`rename()`](#topic_11)
- [`mkdir()`](#topic_12)
- [`get_filesize()`](#topic_13)
- [`delete()`](#topic_14)
- [Item upload/download functions](#topic_15)
    - [`put()`](#topic_15_subtopic_1)
    - [`put_content()`](#topic_15_subtopic_2)
    - [`put_tree()`](#topic_15_subtopic_3)
    - [`get()`](#topic_15_subtopic_4)
    - [`get_content()`](#topic_15_subtopic_5)
    - [`get_tree()`](#topic_15_subtopic_6)

## Initialising an FTPClient object <a name="topic_1"></a>

```python
from ftpleasant import FTPClient
conn = FTPClient()
...
conn.quit()
```

OR:

```python
from ftpleasant import FTPClient
with FTPClient() as conn:
    ...
```

There are four required fields you must specify when initialising an FTPClient object:
| Field    | Type   | Description                                                    | 
|----------|--------|----------------------------------------------------------------|
| host     | str    | The host address of the FTP server                             |
| user     | str    | Username to login to the FTP server                            | 
| password | str    | Password to login to the FTP server                            | 
| secure   | bool   | Whether the current FTPClient should be encrypted with SSL/TLS |

Specify them as shown below:
```python
FTPClient(host="127.0.0.1", user="", password="", secure=False)
```

(^^^ Obviously replacing the above fields with what is required by your FTP server)

There are 6 more optional fields:
| Field            | Type              | Description                                                    | 
|------------------|-------------------|----------------------------------------------------------------|
| port             | int                                     | The port of the FTP server                                     | 
| encoding         | str                                     | The encoding for directories and filenames (default: 'utf-8')  | 
| timeout          | int                                     | How long operations should wait (in seconds) before timing out | 
| source_address   | tuple[str, int]                         | A tuple containing the host and port for the socket to bind to as its source address before connecting |
| acct             | str                                     | Account information to be used for the `ACCT` FTP command. Few systems actually implement this.             |
| ssl_version      | ssl version provided by the ssl library | The SSL version to use (defaults to PROTOCOL_TLS_CLIENT). This is ignored when `secure` is set to False |

Headings below are functions that are within the FTPClient context (initialised either via `with` or by assigning the object to a variable)

## `set_debug_level(level: int) -> None` <a name="topic_2"></a>

Sets the debugging level of the underlying FTP/FTP_TLS object. The debug levels are:
* `0` (default): No debug output.
* `1`: Produce a moderate amount of debug output, generally a single line per request.
* `2` or higher: Produce the maximum amount of debugging output, logging each line sent and received on the control connection.

## `get_welcome() -> str` <a name="topic_3"></a>

Gets the server's welcome message.

## `abort() -> str` <a name="topic_4"></a>

Attempts to abort an ongoing file transfer. This does not always work but it's worth a try.

## `quit() -> str` <a name="topic_5"></a>

Sends a `QUIT` command to the FTP server to politely close the connection. If this fails, this closes the connection anyway.

## `get_features() -> list[str]` <a name="topic_6"></a>

Returns a list containing what the FTP server is capable of. 

## `get_mlst_features() -> list[str]` <a name="topic_7"></a>

If `MLST` is supported on the FTP server, it returns the "facts" that it can returns when the command is returned. "Facts" are essentially metadata attributes of a file. Possible listing facts are shown as below. Most servers only support the first three or four facts shown below.

| Fact       | Description                                                         | 
|------------|---------------------------------------------------------------------|
| type       | The type of entry (e.g. file, dir, `cdir` - current directory .etc) |
| size       | File size in bytes                                                  | 
| modify     | Last modification time of the entry, format (YYYYMMDDHHMM SS)       | 
| perm       | Permission/capabilities (what operations are permitted on the entry)|
| create     | Creation time of the entry (same format as `modify`)                |
| lang       | Language of the filename                                            |
| media-type | MIME type (if applicable)                                           |
| charset    | Character set of the filename                                       |

Further operating system specific keywords could be specified by using the IANA operating system name as a prefix (examples only):

| Fact       | Description                                                         | 
|------------|---------------------------------------------------------------------|
| unix.mode  | UNIX-style mode                                                     |
| unix.owner | Owner names/IDs                                                     |
| unix.group | Group names/IDs                                                     |
| os/2.ea    | OS/2 extended attributes                                            |
| macos.rf   | MacOS resource forks                                                |

This function raises a ValueError if the `MLST` command is not supported by the FTP server

## `ls(remote_path=".", detailed_listing=False, mlst_listing_facts: list | None) -> list[str] | list[dict]` <a name="topic_8"></a>

Returns the list of items present in the current working directory.

| Field              | Description                                                                                       | 
|--------------------|---------------------------------------------------------------------------------------------------|
| remote_path        | The directory to list items from (default: the current working directory)                         |
| detailed_listing   | Whether a more comprehensive listing should be returned (including item metadata, default: false) |
| mlst_listing_facts | What metadata attributes should be returned (ignored if `detailed_listing` is set to false or the server does not support `MLST`) |

## `cd(remote_path=".", force=False) -> str | list[str]` <a name="topic_9"></a>

Changes the current working directory

| Field              | Description                                                                              | 
|--------------------|------------------------------------------------------------------------------------------|
| remote_path        | Where to change to current working directory to (default: the present working directory) |
| force              | Creates the directories specified in `remote_path` if they do not exist                  |

## `pwd() -> str` <a name="topic_10"></a>

Returns the present working directory.

## `rename(from_name: str, to_name: str) -> str` <a name="topic_11"></a>

Renames an item from `from_name` to `to_name`

## `mkdir(remote_path: str, force=False) -> list[str]` <a name="topic_12"></a>

Create a directory specified through `remote_path`. `force` specifies whether parent directories should be created if they do not exist (`False` by default). 

## `get_filesize(file_path: str) -> int | None` <a name="topic_13"></a>

Gets the size of a file specified through `file_path`. Returns `None` is the item specified is not a file or does not exist

## `delete(remote_path: str) -> str` <a name="topic_14"></a>

Deletes an item off the remote server.

# Item upload/download functions <a name="topic_15"></a>

These functions have a return syntax different to the functions above. This is to help you differentiate between files and directories, especially for the `put_tree` and `get_tree` functions.

### `put`/`get` return syntax:

```python
{
    "local_path": "path/to/local/file",
    "remote_path": "path/to/remote/file",
    "status": [TRANSFER_STATUS],
    "additional_notes": [ADDITIONAL_NOTES]
}
```

The status (which replaces `[TRANSFER_STATUS]`) can be one of two things:
* OK: The file transfer completed successfully
* ERROR: Something went wrong during the file transfer.

The "additional_notes" (which replace `[ADDITIONAL_NOTES]`) either
* Return the response from the remote server if the status is `OK`
* Returns the type and details of the error if the status is `ERROR`


### `put_content`/`get_content` return syntax:

```python
{
    "contents": [CONTENTS]
    "local_path": "path/to/local/file",
    "remote_path": "path/to/remote/file",
    "status": [TRANSFER_STATUS],
    "additional_notes": [ADDITIONAL_NOTES]
}
```

This return syntax is exactly the same as the above, except that `contents` holds the contents of the remote file if the local_path is `None`. Otherwise, `contents` is `None`.

### `put_tree`/`get_tree` return syntax: 

```python
{
    "local_path": "path/to/local/file",
    "remote_path": "path/to/remote/file",
    "status": [TRANSFER_STATUS],
    "additional_notes": [ADDITIONAL_NOTES]
}
```

This return syntax is exactly the same as the `put`/`get` return syntax, except that `put_tree` has an additional status - `SKIPPED`. This can have two possible additional notes: `symlink` (as `put_tree` ignores symlinks to prevent uploading items outside of the specified tree) and `ignored` (as the item is specified in the `ignore_items` field)

## `put(local_file_path: IOBase | str, remote_file_path: str, block_size=8192) -> dict` <a name="topic_15_subtopic_1"></a>

Uploads a local file (`local_file_path`) on to a remote file path (`remote_file_path`) in sets of `block_size`. The local file can be an open file or a string containing the path to a local file.

"Blocks" are chunks of data that are read from or written to the remote server at any one time. The block size should be kept low for small files, and high for large files

| Field              | Description                                          | 
|--------------------|------------------------------------------------------|
| local_file_path    | The local file to be placed on to the remote server. |
| remote_file_path   | Where the local file should be upload to.            |
| block_size         | How large the blocksize should be (default 8KB).     |

## `put_content(local_contents: bytes | str, remote_file_path: str, block_size=8192, overwrite=False) -> dict` <a name="topic_15_subtopic_2"></a>

Appends `local_contents` to a remote file (`remote_file_path`). If `overwrite` is set to `True`, the `local_contents` will overwrite the remote file.

| Field              | Description                                          | 
|--------------------|------------------------------------------------------|
| local_contents     | The contents to be placed on to the remote file.     |
| remote_file_path   | Where the local contents should be placed.           |
| block_size         | How large the blocksize should be (default 8KB).     |
| overwrite          | Whether the local contents should overwrite the remote file. By default, the function appends to the remote file. |

## `put_tree(local_item_path: IOBase | str, remote_item_path: str, ignore_items: list | None = None, block_size=8192) -> list[dict]` <a name="topic_15_subtopic_3"></a>

Uploads a tree on to the remote server. The local item can be an open file or a string containing the path to a local item.

| Field              | Description                                               | 
|--------------------|-----------------------------------------------------------|
| local_item_path    | The local file to be placed on to the remote server.      |
| remote_item_path   | Where the local file should be upload to.                 |
| ignore_items       | Specifies what items in the local tree should be ignored. |
| block_size         | How large the blocksize should be (default 8KB).          |

## `get(remote_path: str, local_path: IOBase | str | None = None, block_size=8192) -> dict` <a name="topic_15_subtopic_4"></a>

Downloads a file from the remote server

| Field              | Description                                          | 
|--------------------|------------------------------------------------------|
| remote_path        | The local file to be placed on to the remote server. |
| local_path         | Where the local file should be upload to.            |
| block_size         | How large the blocksize should be (default 8KB).     |

## `get_content(remote_path: str, local_path: IOBase | str | None = None, block_size=8192) -> dict` <a name="topic_15_subtopic_5"></a>

Downloads the contents of a file from the remote server. By default, the contents will be returned. However, these can be written to an open file or a local file specified as path (as a string).

| Field              | Description                                                                              | 
|--------------------|------------------------------------------------------------------------------------------|
| remote_path        | The local file to be placed on to the remote server.                                     |
| local_path         | Where the contents should be written to. By default, this is returned from the function. |
| block_size         | How large the blocksize should be (default 8KB).                                         |

## `get_tree(remote_tree: str, local_path: str, block_size=8192)` <a name="topic_15_subtopic_6"></a>

Downloads a tree (nested files and directories) from the remote server.

| Field              | Description                                         | 
|--------------------|-----------------------------------------------------|
| remote_tree        | The tree to be fetched from the remote server.      |
| local_path         | Where the downloaded tree should be placed locally. |
| block_size         | How large the blocksize should be (default 8KB).    |