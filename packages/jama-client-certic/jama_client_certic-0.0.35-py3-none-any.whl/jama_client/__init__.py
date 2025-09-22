"""
# Jama client library

## Installation

Use pip to install:

    pip install jama-client-CERTIC

## Quick start

    from jama_client import Client
    client = Client("https://acme.tld/rpc/", "secretapikeyhere")
    file_id = client.upload("/path/to/some/file.jpg")
    collection_id = client.add_collection("title of the collection")
    client.add_file_to_collection(file_id, collection_id)


"""

import os
import math
import hashlib
from requests import post
from typing import Any, List, Dict
import base64

DEFAULT_UPLOAD_CHUNK_SIZE = 1024 * 1024


def _file_hash256(file_path: str) -> str:
    hsh = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chnk in iter(lambda: f.read(8192), b""):
            hsh.update(chnk)
    return hsh.hexdigest()


def _get_nb_of_chunks(
    file_path: str, chunk_size: int = DEFAULT_UPLOAD_CHUNK_SIZE
) -> int:
    size = os.path.getsize(file_path)
    return math.ceil(size / chunk_size)


def _get_file_slice(
    file_path: str, from_byte: int, max_size: int = DEFAULT_UPLOAD_CHUNK_SIZE
) -> bytes:
    with open(file_path, "rb") as f:
        f.seek(from_byte)
        return f.read(max_size)


class IncompleteUpload(RuntimeError):
    pass


class AlreadyUploaded(RuntimeError):
    pass


class ServiceError(RuntimeError):
    def __init__(self, message):
        super(ServiceError, self).__init__()
        self.message = message


class _Method(object):
    def __init__(self, send, name):
        self.__send = send
        self.__name = name

    def __getattr__(self, name):
        return _Method(self.__send, "{}.{}".format(self.__name, name))

    def __call__(self, *args):
        return self.__send(self.__name, args)


class _Chunker:
    def __init__(self, file_path: str, chunk_size: int = DEFAULT_UPLOAD_CHUNK_SIZE):
        self._file_path = file_path
        self._chunk_size = chunk_size
        self.nb_of_chunks = _get_nb_of_chunks(self._file_path, self._chunk_size)
        self.file_hash = _file_hash256(self._file_path)

    def get_chunk(self, number_of_chunk) -> bytes:
        if number_of_chunk > self.nb_of_chunks or number_of_chunk < 0:
            raise ValueError("Chunk number out of range")
        return _get_file_slice(
            self._file_path, self._chunk_size * number_of_chunk, self._chunk_size
        )

    @property
    def chunks(self):
        for i in range(self.nb_of_chunks):
            yield self.get_chunk(i)


class _ChunksUploader:
    def __init__(
        self,
        file_path: str,
        endpoint: str,
        api_key: str,
        project_id: int,
        chunk_size: int = DEFAULT_UPLOAD_CHUNK_SIZE,
        file_name: str = None,
        origin_dir_name: str = None,
    ):
        self.foreign_reference = None
        self._file_path = file_path
        self._file_name = file_name
        self._origin_dir_name = origin_dir_name
        self._api_key = api_key
        self._endpoint = endpoint
        self._project_id = project_id
        self._chunker = _Chunker(file_path, chunk_size)
        self.chunks_statuses = {}
        for i in range(self.number_of_chunks):
            self.chunks_statuses[i] = {
                "chunk_number": i,
                "tries": 0,
                "done": False,
                "message": "",
            }

    @property
    def number_of_chunks(self) -> int:
        return self._chunker.nb_of_chunks

    @property
    def is_complete(self) -> bool:
        for k in self.chunks_statuses:
            if not self.chunks_statuses[k]["done"]:
                return False
        return True

    def upload_all(self):
        if self.foreign_reference is None:
            for i in range(self.number_of_chunks):
                if not self.chunks_statuses[i]["done"]:
                    self.upload(i)

    def upload(self, chunk_number: int):
        self.chunks_statuses[chunk_number]["tries"] = (
            self.chunks_statuses[chunk_number]["tries"] + 1
        )
        try:
            headers = {
                "X-Project": str(self._project_id),
                "X-Api-Key": self._api_key,
                "X-file-chunk": "{}/{}".format(chunk_number, self.number_of_chunks),
                "X-file-hash": self._chunker.file_hash,
                "X-file-name": base64.b64encode(
                    (self._file_name or os.path.basename(self._file_path)).encode(
                        "utf-8"
                    )
                ),
            }
            if self._origin_dir_name:
                headers["X-origin-dir"] = self._origin_dir_name
            response = post(
                url=self._endpoint,
                data=self._chunker.get_chunk(chunk_number),
                headers=headers,
            )
            if response.status_code == 202:
                self.chunks_statuses[chunk_number]["done"] = True
            elif response.status_code == 200:
                for i in range(self.number_of_chunks):
                    self.chunks_statuses[i]["done"] = True
                self.foreign_reference = int(response.text)
            else:
                self.chunks_statuses[chunk_number][
                    "message"
                ] = "failed with status {} {}".format(
                    response.status_code, response.text
                )
        except Exception as e:
            self.chunks_statuses[chunk_number]["message"] = getattr(
                e, "message", repr(e)
            )


class Client:
    def __init__(self, endpoint: str, api_key: str):
        self._endpoint = endpoint
        self._api_key = api_key
        self.requests_count = 0
        self.upload_status = {}

    def __getattr__(self, name):
        return _Method(self._call, name)

    def _call(self, method: str, params: List = None) -> Any:
        self.requests_count = self.requests_count + 1
        payload = {"method": method, "params": params or [], "id": self.requests_count}
        try:
            response = post(
                url=self._endpoint, json=payload, headers={"X-Api-Key": self._api_key}
            )
        except Exception:
            raise ServiceError("Could not contact service")
        if response.status_code == 200:
            message = response.json()
            if message["error"] is None:
                return message["result"]
            else:
                raise ServiceError(message["error"])
        else:
            raise ServiceError(
                "Response ended with status code {}".format(response.status_code)
            )

    def upload(
        self,
        file_path: str,
        project_id: int,
        chunk_size: int = DEFAULT_UPLOAD_CHUNK_SIZE,
        file_name: str = None,
        origin_dir_name: str = None,
    ) -> int:
        """
        This methods uploads a file in multiple chunks, allowing
        resumable uploads.

        ```file_path``` is the local path to the file.

        ```chunk_size``` is the number of bytes uploaded with each chunk of the file.

        ```file_name``` overides the name of the file, should you want a different name in Jama than
        the local name.

        ```origin_dir_name``` is a directory path (```dirA/dirB/dirC```). This path triggers
        the creation of the corresponding collections and sub-collections in Jama.
        """
        upload_infos = self.upload_infos(
            _file_hash256(file_path), project_id=project_id
        )
        if upload_infos.get("status") == "available":
            return upload_infos.get("id")
            # raise AlreadyUploaded()

        chunked_upload = _ChunksUploader(
            file_path,
            self._endpoint + "upload/partial/",
            self._api_key,
            project_id,
            chunk_size,
            file_name,
            origin_dir_name,
        )

        # Resume upload across sessions
        # Set chunk status to "done" if already available
        # on the server
        if upload_infos.get("status") == "incomplete":
            for available_chunk in upload_infos.get("available_chunks", []):
                _, chunk_number = os.path.splitext(available_chunk)[0].split("-")
                chunk_number = int(chunk_number.lstrip("0") or "0")
                chunked_upload.chunks_statuses[chunk_number]["done"] = True

        chunked_upload.upload_all()
        if not chunked_upload.is_complete:
            self.upload_status[file_path] = chunked_upload.chunks_statuses
            # If incomplete, raise exception so the
            # client can decide to retry or not.
            raise IncompleteUpload()
        return chunked_upload.foreign_reference

    def activate_rpc_access(self, user_name: str, api_key: str) -> bool:
        """
            Add access to the RPC API for the given user name with the given API key.
        A new user will be created if none is available with given user name.

        Requires superuser.
        """
        return self._call("activate_rpc_access", [user_name, api_key])

    def add_collection(self, title: str, parent_id: int) -> Dict:
        """
            Create a new collection based on 'title' and parent_id

        Returns either the serialized new collection of null if parent does
        not exist.

        Example output:

        ```
        {
            "id": 3,
            "title": "paintings",
            "resources_count": 0,
            "children_count": 0,
            "descendants_count": 0,
            "descendants_resources_count": 0,
            "parent": null,
            "project_id": 1,
            "children": null,
            "metas": [],
            "public_access": false,
            "tags": [],
        }
        ```
        """
        return self._call("add_collection", [title, parent_id])

    def add_collection_from_path(self, path: str, project_id: int) -> List[Dict]:
        """
            Will take a path such as '/photos/arts/paintings/'
        and build the corresponding hierarchy of collections. The hierarchy
        is returned as a list of serialized collections.

        Beware: Because the collections are serialized before their children,
        all the children/descendants counts are set to 0.

        Example output:

        ```
        [
            {
                "id": 1,
                "title": "photos",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": null,
                "project_id": 1,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
            {
                "id": 2,
                "title": "arts",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": 1,
                "project_id": 1,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
            {
                "id": 3,
                "title": "paintings",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": 2,
                "project_id": 1,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
        ]
        ```
        """
        return self._call("add_collection_from_path", [path, project_id])

    def add_meta_to_collection(
        self, collection_id: int, meta_id: int, meta_value: str, recursive: bool = False
    ) -> int:
        """
            Add a meta value to a collection given their ids.

        If recursive is True, the meta will be added to all descendants,
        collections and resources alike.
        """
        return self._call(
            "add_meta_to_collection", [collection_id, meta_id, meta_value, recursive]
        )

    def add_meta_to_resource(
        self, resource_id: int, meta_id: int, meta_value: str
    ) -> int:
        """
        Add a meta value to a resource given their ids.
        """
        return self._call("add_meta_to_resource", [resource_id, meta_id, meta_value])

    def add_meta_to_selection(
        self, from_collection_id: int, selection: dict, meta_id: int, meta_value: str
    ) -> bool:
        """
            Use such a dict for selection:
        ```
        {
            "include": {
                "resources_ids": [3493, 159]
                "collections_ids:" [20, 31]
            },
            "exclude": {
                "resources_ids": [12, 10, 15]
                "collections_ids:" [4, 254, 17]
            }
        }
        ```
        """
        return self._call(
            "add_meta_to_selection",
            [from_collection_id, selection, meta_id, meta_value],
        )

    def add_metadata(self, title: str, metas_set_id: int) -> int:
        """
            Add a new metadata to metadata set.

        Set optional 'metadata_type_id'. Defaults to string type.
        """
        return self._call("add_metadata", [title, metas_set_id])

    def add_metadataset(self, title: str, project_id: int) -> int:
        """
        Create new metadata set from title.
        """
        return self._call("add_metadataset", [title, project_id])

    def add_resource_to_collection(self, resource_id: int, collection_id: int) -> bool:
        """
        Add a resource to a collection given ids.
        """
        return self._call("add_resource_to_collection", [resource_id, collection_id])

    def add_tag_to_collection(self, tag_uid: str, collection_id: int) -> bool:
        """
        Add tag to a collection based on tag uid and collection id.
        """
        return self._call("add_tag_to_collection", [tag_uid, collection_id])

    def add_tag_to_resource(self, tag_uid: str, resource_id: int) -> bool:
        """
        Add tag to a resource based on tag uid and resource id.
        """
        return self._call("add_tag_to_resource", [tag_uid, resource_id])

    def advanced_search(
        self,
        search_terms: List[Dict],
        project_id: int,
        include_metas: bool = False,
        collection_id: int = None,
        limit_from: int = 0,
        limit_to: int = 2000,
        order_by: str = "title",
        fetch_resources: bool = True,
        fetch_collections: bool = True,
        public_access: bool = None,
    ) -> Dict[str, List]:
        """
            Performs a complex search using terms such as 'contains', 'is', 'does_not_contain'.

        Multiple conditions can be added.

        Example input:

        ```
        [
            {"property": "title", "term": "contains", "value": "cherbourg"},
            {"meta": 123, "term": "is", "value": "35mm"},
            {"exclude_meta": 145},
            {"tags": ["PAINTINGS", "PHOTOS"]}
            {"exclude_tags": ["DRAWINGS"]}
        ]
        ```

        Example output:

        ```
        {
            "collections": [],
            "resources": [
                {
                "id": 1,
                "title": "Cherbourg by night",
                "original_name": "cherbourg_by_night.jpg",
                "type": "image/jpeg",
                "hash": "0dd93a59aeaccfb6d35b1ff5a49bde1196aa90dfef02892f9aa2ef4087d8738e",
                "metas": null,
                "urls": [],
                "tags": [],
                }
            ]
        }
        ```
        """
        return self._call(
            "advanced_search",
            [
                search_terms,
                project_id,
                include_metas,
                collection_id,
                limit_from,
                limit_to,
                order_by,
                fetch_resources,
                fetch_collections,
                public_access,
            ],
        )

    def advanced_search_terms(self) -> List[str]:
        """
            Return terms conditions to be used in advanced search.

        Example output:

        ```
        [
            "is",
            "contains",
            "does_not_contain"
        ]
        ```
        """
        return self._call("advanced_search_terms", [])

    def ancestors_from_collection(
        self, collection_id: int, include_self: bool = False
    ) -> List[dict]:
        """
            Get ancestors from collection id as a list of serialized collections.

        If 'include_self' is true, will add the current collection at the begining.

        Example output:

        ```
        [
            {
                "id": 1,
                "title": "photos",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": null,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
            {
                "id": 2,
                "title": "arts",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": 1,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
            {
                "id": 3,
                "title": "paintings",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": 2,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
        ]
        ```
        """
        return self._call("ancestors_from_collection", [collection_id, include_self])

    def ancestors_from_resource(self, resource_id: int) -> List[List[dict]]:
        """
            Get ancestors from resource id as a list of serialized collections.

        Example output:

        ```
        [
            {
                "id": 1,
                "title": "photos",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": null,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
            {
                "id": 2,
                "title": "arts",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": 1,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
            {
                "id": 3,
                "title": "paintings",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": 2,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
        ]
        ```
        """
        return self._call("ancestors_from_resource", [resource_id])

    def auto_find_rotate_angle(self, resource_id: int) -> float:
        """
        Tries to determine skew angle of image with text.
        """
        return self._call("auto_find_rotate_angle", [resource_id])

    def change_collection_meta_value(self, meta_value_id: int, meta_value: str) -> bool:
        """
        Change the value of a meta for a collection.
        """
        return self._call("change_collection_meta_value", [meta_value_id, meta_value])

    def change_resource_meta_value(self, meta_value_id: int, meta_value: str) -> bool:
        """
        Change the value of a meta for a resource
        """
        return self._call("change_resource_meta_value", [meta_value_id, meta_value])

    def collection(self, collection_id: int) -> Dict:
        """
            Get a particular collection given its id.

        Example output:

        ```
        {
            "id": 2,
            "title": "art works",
            "resources_count": 23,
            "children_count": 5,
            "parent": 1,
            "children": None,
            "metas": [],
            "public_access": False,
            "tags": [],
        }
        ```
        """
        return self._call("collection", [collection_id])

    def collection_stats(self, collection_id: int) -> dict:
        """
            Get infos from given collection:

        - number of descendants
        - number of descendant resources
        - number of resources
        - number of children collections
        """
        return self._call("collection_stats", [collection_id])

    def collections(
        self,
        parent_id: int,
        recursive: bool = False,
        limit_from: int = 0,
        limit_to: int = 2000,
        flat_list: bool = False,
        only_published: bool = False,
        order_by: str = "title",
        only_deleted_items: bool = False,
    ) -> List[Dict]:
        """
            Return the user's collections under the parent collection
        specified by 'parent_id'. If 'recursive' is true, will
        return all the descendants recursively in the 'children' key.
        If recursive is false, 'children' is null.

        Special case:

        If flat_list is True, collections are returned as a flat list and parent_id is effectively IGNORED.

        Example output:

        ```
        [
            {
                "id": 2,
                "title": "art works",
                "resources_count": 23,
                "children_count": 5,
                "descendants_count": 12,
                "descendants_resources_count": 58,
                "parent": 1,
                "children": None,
                "metas": [],
                "public_access": False,
                "tags": [],
            }
        ]
        ```
        """
        return self._call(
            "collections",
            [
                parent_id,
                recursive,
                limit_from,
                limit_to,
                flat_list,
                only_published,
                order_by,
                only_deleted_items,
            ],
        )

    def create_annotation(self, resource_id: int, data: dict) -> dict:
        """
            Adds an annotation, returning the serialized annotation:

        ```
        {
            "id": annotation.id,
            "owner": annotation.owner.username,
            "data": annotation.data,
            "created_at": annotation.created_at.isoformat(),
            "updated_at": annotation.updated_at.isoformat(),
            "resource_id": annotation.resource_id,
        }
        ```
        """
        return self._call("create_annotation", [resource_id, data])

    def create_project(self, project_label: str, project_description: str) -> dict:
        """
            Create a new project.

        Requires superuser.
        """
        return self._call("create_project", [project_label, project_description])

    def deactivate_rpc_access(self, user_name: str, api_key: str) -> bool:
        """
            Deactivate access to the RPC API for the given user name and API key.
        Only the access (API key) is removed, not the user.

        Requires superuser.
        """
        return self._call("deactivate_rpc_access", [user_name, api_key])

    def delete_annotation(self, annotation_id: int) -> bool:
        """
        Deletes an annotation
        """
        return self._call("delete_annotation", [annotation_id])

    def delete_collection(self, collection_id: int, recursive: bool = False) -> Dict:
        """
            Delete collection given its id.

        Collection MUST be empty of any content (no children collections and no resources),
        unless the 'recursive'parameter is set to True, in which case ALL descendants will be
        deleted.
        """
        return self._call("delete_collection", [collection_id, recursive])

    def delete_metadata(self, metadata_id: int) -> bool:
        """
        Delete metadata based on its id.
        """
        return self._call("delete_metadata", [metadata_id])

    def delete_metadataset(self, metadataset_id: int, recursive: bool = False) -> Dict:
        """
            Delete metadata set based on its id. Optional recursive
        call.
        """
        return self._call("delete_metadataset", [metadataset_id, recursive])

    def delete_project_property(self, project_id: int, property_key: str) -> bool:
        """
            Delete a property from the project.

        property_key is NOT case sensitive, ie. "ProPertY" is the same as "pRoperTy" or "property".
        """
        return self._call("delete_project_property", [project_id, property_key])

    def delete_resource(self, resource_id: int) -> bool:
        """
        Permanently (soft) delete a resource given its id.
        """
        return self._call("delete_resource", [resource_id])

    def delete_role(self, project_id: int, role_label: str) -> bool:
        """
            Delete role within given project.

        Requires superuser
        """
        return self._call("delete_role", [project_id, role_label])

    def delete_tag(self, uid: str) -> bool:
        """
            Remove (delete) a tag based on its uid.

        Beware: This will remove ALL associations with the tag.
        """
        return self._call("delete_tag", [uid])

    def has_permission(self, project_id: int, permission: str) -> bool:
        """
        Test current user for given permission.
        """
        return self._call("has_permission", [project_id, permission])

    def list_annotations(self, resource_id: int) -> List[dict]:
        """
        List all annotations for a given resource
        """
        return self._call("list_annotations", [resource_id])

    def list_permissions(self) -> List[Dict]:
        """
            Lists all available permissions in the application:

        ```
        [
            {'id': 1, 'label': 'collection.create'},
            {'id': 2, 'label': 'collection.read'},
            {'id': 3, 'label': 'collection.update'},
            {'id': 4, 'label': 'collection.delete'},
            {'id': 5, 'label': 'resource.create'},
            {'id': 6, 'label': 'resource.read'},
            {'id': 7, 'label': 'resource.update'},
            {'id': 8, 'label': 'resource.delete'},
            {'id': 9, 'label': 'metadata.create'},
            {'id': 10, 'label': 'metadata.read'},
            {'id': 11, 'label': 'metadata.update'},
            {'id': 12, 'label': 'metadata.delete'},
            {'id': 13, 'label': 'metadataset.create'},
            {'id': 14, 'label': 'metadataset.read'},
            {'id': 15, 'label': 'metadataset.update'},
            {'id': 16, 'label': 'metadataset.delete'},
            {'id': 17, 'label': 'file.create'},
            {'id': 18, 'label': 'file.read'},
            {'id': 19, 'label': 'file.update'},
            {'id': 20, 'label': 'file.delete'},
            {'id': 21, 'label': 'tag.create'},
            {'id': 22, 'label': 'tag.read'},
            {'id': 23, 'label': 'tag.update'},
            {'id': 24, 'label': 'tag.delete'},
            {'id': 25, 'label': 'file.download_source'}
        ]
        ```
        """
        return self._call("list_permissions", [])

    def list_roles(self, project_id: int) -> List[Dict]:
        """
        Fetch all roles defined in the project, no matter the user.
        """
        return self._call("list_roles", [project_id])

    def meta_count(self, metadata_id: int, collection_id: int) -> dict:
        """
        Count metadata usage.
        """
        return self._call("meta_count", [metadata_id, collection_id])

    def metadata(self, metadata_id: int) -> Dict:
        """
            Get one particular metadata given its id.

        Example output:

        ```
        {
            "id": 2,
            "title": "ICC_Profile:GrayTRC",
            "set_id": 1,
            "set_title": "exif metas",
            "rank": 1,
            "project_id": 1,
        }
        ```
        """
        return self._call("metadata", [metadata_id])

    def metadatas(self, metadata_set_id: int) -> List[Dict]:
        """
            Get all metadatas given a metadata set id.

        Metadatas MAY be ordered with the rank attribute.

        Example output:

        ```
        [
            {
                "id": 1,
                "title": "PNG:ProfileName",
                "set_id": 1,
                "set_title": "exif metas",
                "rank": 0,
                "project_id": 1,
            },
            {
                "id": 2,
                "title": "ICC_Profile:GrayTRC",
                "set_id": 1,
                "set_title": "exif metas",
                "rank": 1,
                "project_id": 1,
            }
        ]
        ```
        """
        return self._call("metadatas", [metadata_set_id])

    def metadatasets(self, project_id: int) -> List[Dict]:
        """
            Get the list of all the project's metadata sets.
        For each metadatas set, the number of metadatas is given in metas_count.

        Example output:

        ```
        [
            {"id": 1, "title": "exif metas", "project_id": 1, "metas_count": 23},
            {"id": 2, "title": "dublin core", "project_id": 1, "metas_count": 17}
        ]
        ```
        """
        return self._call("metadatasets", [project_id])

    def move_collection(
        self, child_collection_id: int, parent_collection_id: int
    ) -> bool:
        """
            Move a collection from a parent to another.

        Will raise ServiceException in the following cases:

        - 'child_collection_id' and 'parent_collection_id' are equal
        - parent collection does not exist
        - parent collection is a descendant of child collection
        """
        return self._call(
            "move_collection", [child_collection_id, parent_collection_id]
        )

    def move_items(
        self,
        from_collection_id: int,
        to_collection_id: int,
        collections_ids: List[int],
        resources_ids: List[int],
    ) -> Dict[str, Dict]:
        """
        Move items (collections or resources) from one Collection to another
        """
        return self._call(
            "move_items",
            [from_collection_id, to_collection_id, collections_ids, resources_ids],
        )

    def move_selection(
        self, from_collection_id: int, selection: dict, to_collection_id: int
    ) -> Dict[str, Dict]:
        """
            Will mass move items (resources AND collections) based on parent collection and destination collection

        Use such an object for inclusion/exclusion:

        ```
        {
            "include": {
                "resources_ids": [3493, 159]
                "collections_ids:" [20, 31]
            },
            "exclude": {
                "resources_ids": [12, 10, 15]
                "collections_ids:" [4, 254, 17]
            }
        }
        ```
        """
        return self._call(
            "move_selection", [from_collection_id, selection, to_collection_id]
        )

    def picture_rotate_crop(
        self,
        resource_id: int,
        rotation: float = 0,
        top_crop: int = 0,
        right_crop: int = 0,
        bottom_crop: int = 0,
        left_crop: int = 0,
    ) -> dict:
        """
            Rotate and crop an image. The resulting image then replaces the
        original in the current resource.

        Will return the resource upon success. Throws a ServiceException
        otherwise.
        """
        return self._call(
            "picture_rotate_crop",
            [resource_id, rotation, top_crop, right_crop, bottom_crop, left_crop],
        )

    def ping(self) -> str:
        """
            This is a test method to ensure the server-client communication works.
        Will return "pong [name authenticated of user]"

        Example output:

        ```
        pong john
        ```
        """
        return self._call("ping", [])

    def project_items(
        self,
        search_terms: List[Dict],
        project_id: int,
        include_metas: bool = False,
        collection_id: int = None,
        limit_from: int = 0,
        limit_to: int = 2000,
        order_by: str = "title",
        public_access: bool = None,
    ) -> Dict[str, List]:
        """
        Alias to advanced_search.
        """
        return self._call(
            "project_items",
            [
                search_terms,
                project_id,
                include_metas,
                collection_id,
                limit_from,
                limit_to,
                order_by,
                public_access,
            ],
        )

    def project_properties(self, project_id: int) -> List[dict]:
        """
        Get ALL properties from a project.
        """
        return self._call("project_properties", [project_id])

    def project_property(self, project_id: int, property_key: str) -> dict:
        """
            Get a property value from the project.

        property_key is NOT case sensitive, ie. "ProPertY" is the same as "pRoperTy" or "property".

        Will raise an exception if property does not exist.
        """
        return self._call("project_property", [project_id, property_key])

    def project_stats(self, project_id: int) -> dict:
        """
            Get infos from given project:

        - id of project collection root
        - number of descendants
        - number of descendant resources
        - number of resources
        - number of children collections
        """
        return self._call("project_stats", [project_id])

    def projects_user_permissions(self) -> List[Dict]:
        """
            Get all rights for the current user.

        Example output:

        ```
        [
            {
                'project': {'id': 7, 'label': 'john doe main project'},
                'role': {'id': 7, 'label': 'admin', 'permissions': [{"id": 1, "label": "do_anything"}]},
                'user': 'john doe'
            }
        ]
        ```
        """
        return self._call("projects_user_permissions", [])

    def public_collections(self, project_id: int) -> List[dict]:
        """
        Get public collections
        """
        return self._call("public_collections", [project_id])

    def publish_collection(self, collection_id: int) -> bool:
        """
        Mark a collection as public
        """
        return self._call("publish_collection", [collection_id])

    def recycle_bin(self, project_id: int) -> List[Dict]:
        """
            Gets deleted elements:

        - object type
        - label
        - id
        - deleted_at
        """
        return self._call("recycle_bin", [project_id])

    def remove_meta_value_from_collection(
        self, collection_id: int, meta_value_id: int, recursive: bool = False
    ) -> bool:
        """
        Remove a meta value from a collection given their ids.
        """
        return self._call(
            "remove_meta_value_from_collection",
            [collection_id, meta_value_id, recursive],
        )

    def remove_meta_value_from_resource(
        self, resource_id: int, meta_value_id: int
    ) -> bool:
        """
        Remove a meta_value from a resource given their ids.
        """
        return self._call(
            "remove_meta_value_from_resource", [resource_id, meta_value_id]
        )

    def remove_meta_value_from_selection(
        self, from_collection_id: int, selection: dict, meta_value_id: int
    ) -> bool:
        """
            Use such a dict for selection:
        ```
        {
            "include": {
                "resources_ids": [3493, 159]
                "collections_ids:" [20, 31]
            },
            "exclude": {
                "resources_ids": [12, 10, 15]
                "collections_ids:" [4, 254, 17]
            }
        }
        ```
        """
        return self._call(
            "remove_meta_value_from_selection",
            [from_collection_id, selection, meta_value_id],
        )

    def remove_resource_from_collection(
        self, resource_id: int, collection_id: int
    ) -> bool:
        """
        Remove a resource from a collection given ids.
        """
        return self._call(
            "remove_resource_from_collection", [resource_id, collection_id]
        )

    def remove_selection(self, parent_collection_id: int, selection: dict) -> bool:
        """
            Will mass remove items (resources AND collections) based on parent collection

        Use such an object for inclusion/exclusion:

        ```
        {
            "include": {
                "resources_ids": [3493, 159]
                "collections_ids:" [20, 31]
            },
            "exclude": {
                "resources_ids": [12, 10, 15]
                "collections_ids:" [4, 254, 17]
            }
        }
        ```

        deleteCollection (with recursion) and deleteResource are used under the hood.

        The parent collection is left as-is.
        """
        return self._call("remove_selection", [parent_collection_id, selection])

    def remove_tag_from_collection(self, tag_uid: str, collection_id: int) -> bool:
        """
        Remove tag from a collection based on tag uid and collection id.
        """
        return self._call("remove_tag_from_collection", [tag_uid, collection_id])

    def remove_tag_from_resource(self, tag_uid: str, resource_id: int) -> bool:
        """
        Remove tag from a resource based on tag uid and resource id.
        """
        return self._call("remove_tag_from_resource", [tag_uid, resource_id])

    def rename_collection(self, collection_id: int, title: str) -> bool:
        """
        Rename a collection (ie. change its title).
        """
        return self._call("rename_collection", [collection_id, title])

    def rename_meta(self, meta_id: int, title: str) -> bool:
        """
        Rename a metadata (ie. change its title).
        """
        return self._call("rename_meta", [meta_id, title])

    def rename_resource(self, resource_id: int, title: str) -> bool:
        """
        Rename a resource (ie. change its title).
        """
        return self._call("rename_resource", [resource_id, title])

    def replace_file(self, from_resource_id: int, to_resource_id: int) -> bool:
        """
            Replace a file by another using two existing resources.

        The two resources are expected to be of File type. Then the
        following operations are performed:

        - metas from the "ExifTool" set are removed from the destination resource instance
        - metas from the "ExifTool" set are transfered from the source resource instance to the destination resource instance
        - the destination resource instance gets the file hash from the source resource instance
        - the source resource instance is (hard) deleted
        - the destination resource instance is saved

        Such that all title/metas/tags/collections of the destination resource instance are untouched,
        excluding exif metas that are transfered from the source.
        """
        return self._call("replace_file", [from_resource_id, to_resource_id])

    def resource(self, resource_id: int, include_metas: bool = True) -> Dict:
        """
            Get a resource given its id.

        Example output (file resource):

        ```
        {
            "id": 1,
            "title": "letter",
            "original_name": "letter.txt",
            "type": "text/plain",
            "hash": "0dd93a59aeaccfb6d35b1ff5a49bde1196aa90dfef02892f9aa2ef4087d8738e",
            "metas": null,
            "urls": [],
            "tags": [],
        }
        ```
        """
        return self._call("resource", [resource_id, include_metas])

    def resources(
        self,
        collection_id: int,
        include_metas: bool = False,
        limit_from: int = 0,
        limit_to: int = 2000,
        order_by: str = "title",
        only_deleted_items: bool = False,
        only_tags: List[str] = None,
    ) -> List[Dict]:
        """
            Get all resources from a collection.

        If 'include_metas' is true, will return the resources metadatas.
        If 'include_metas' is false, 'metas' will be null.

        Different resources types may have different object keys. The bare
        minimum is 'id', 'title' and 'tags'.

        Example output (file resource):

        ```
        [
            {
                "id": 1,
                "title": "letter",
                "original_name": "letter.txt",
                "type": "text/plain",
                "hash": "0dd93a59aeaccfb6d35b1ff5a49bde1196aa90dfef02892f9aa2ef4087d8738e",
                "metas": null,
                "urls": [],
                "tags": [],
            }
        ]
        ```
        """
        return self._call(
            "resources",
            [
                collection_id,
                include_metas,
                limit_from,
                limit_to,
                order_by,
                only_deleted_items,
                only_tags,
            ],
        )

    def restore_collection(
        self, collection_id: int, destination_collection_id: int
    ) -> bool:
        """
        Restore a deleted collection from the recycle bin
        """
        return self._call(
            "restore_collection", [collection_id, destination_collection_id]
        )

    def restore_resource(
        self, resource_id: int, destination_collection_id: int
    ) -> bool:
        """
        Restore a deleted resource from the recycle bin
        """
        return self._call("restore_resource", [resource_id, destination_collection_id])

    def set_metas_to_collection(
        self,
        collection_id: int,
        metas: List[dict],
        recursive: bool = False,
        async_mode: bool = True,
    ) -> bool:
        """
            Sets all metas for a unique metadata set.

        Metas is a list of metadata id => metadata value dictionaries.

        All metas must share the same metadata set.

        If recursive is True, the meta will be set to all direct children resources.

        *Not* actually recursive: Descendants (sub-collections and sub-collections resources) are IGNORED.

        async_mode is IGNORED
        """
        return self._call(
            "set_metas_to_collection", [collection_id, metas, recursive, async_mode]
        )

    def set_metas_to_resource(self, resource_id: int, metas: List[dict]) -> bool:
        """
            Sets all metas for a unique metadata set.

        Metas is a list of metadata id => metadata value dictionaries.

        All metas must share the same metadata set.
        """
        return self._call("set_metas_to_resource", [resource_id, metas])

    def set_project_property(
        self, project_id: int, property_key: str, property_value: dict
    ) -> dict:
        """
            Set a property value to the project.

        property_key is NOT case sensitive, ie. "ProPertY" is the same as "pRoperTy" or "property".
        """
        return self._call(
            "set_project_property", [project_id, property_key, property_value]
        )

    def set_representative_resource(
        self, collection_id: int, resource_id: int = None
    ) -> bool:
        """
            Choose a Resource that is the best representation of a collection.
        Typical use case: set a miniature for a collection.

        The Resource does not have to be contained in the collection.

        Resource id may be set set to None/Null.
        """
        return self._call("set_representative_resource", [collection_id, resource_id])

    def set_role(
        self, project_id: int, role_label: str, permissions: List[int]
    ) -> Dict:
        """
            Create or update a role on a project, with the given permissions.

        Requires superuser.
        """
        return self._call("set_role", [project_id, role_label, permissions])

    def set_tag(
        self, uid: str, project_id: int, label: str = None, ark: str = None
    ) -> dict:
        """
            Get or create a Tag by uid (unique identifier). 'label' is an optional human-readable name.

        Example output:

        ```
        {
            "id": 1,
            "uid": "PAINTINGS",
            "label": "peintures",
            "ark": null,
        }
        ```
        """
        return self._call("set_tag", [uid, project_id, label, ark])

    def simple_search(
        self,
        query: str,
        project_id: int,
        limit_from: int = 0,
        limit_to: int = 2000,
        order_by: str = "title",
    ) -> Dict[str, List]:
        """
            Performs a simple search on resources and collections, based on their titles.

        Example output:

        ```
        {
            "collections": [
                {
                "id": 1,
                "title": "photos",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": null,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
                }
            ],
            "resources": [
                {
                "id": 1,
                "title": "letter",
                "original_name": "letter.txt",
                "type": "text/plain",
                "hash": "0dd93a59aeaccfb6d35b1ff5a49bde1196aa90dfef02892f9aa2ef4087d8738e",
                "metas": null,
                "urls": [],
                "tags": [],
                }
            ]
        }
        ```
        """
        return self._call(
            "simple_search", [query, project_id, limit_from, limit_to, order_by]
        )

    def supported_file_types(self) -> List[Dict]:
        """
            Get a list of all supported file type, complete with their mimes.

        Example output:

        ```
        [
            {
            "mime": "image/jpeg",
            "extensions": [".jpg", ".jpeg"],
            "iiif_support": true,
            }
        ]
        ```
        """
        return self._call("supported_file_types", [])

    def tags(self, project_id: int) -> List[dict]:
        """
            Returns all tags available in the project.

        Example output:

        ```
        [
            {
            "id": 1,
            "uid": "PAINTINGS",
            "label": "peintures",
            "ark": null,
            },
            {
            "id": 2,
            "uid": "PHOTOS",
            "label": "photos",
            "ark": null,
            }
        ]
        ```
        """
        return self._call("tags", [project_id])

    def unpublish_collection(self, collection_id: int) -> bool:
        """
        Mark a collection as private
        """
        return self._call("unpublish_collection", [collection_id])

    def update_annotation(self, annotation_id: int, data: dict) -> dict:
        """
        Updates an annotation, returning the serialized annotation
        """
        return self._call("update_annotation", [annotation_id, data])

    def update_resource_from_xlsx_row(self, resource_data: dict) -> bool:
        """
        Compound method to update resource and resources metadata from a xlsx file row.
        """
        return self._call("update_resource_from_xlsx_row", [resource_data])

    def upload_infos(self, sha256_hash: str, project_id: int) -> Dict:
        """
            Get information for an upload based on the file hash.

        Example output:

        ```
        {
            "status": "not available",
            "id": null,
            "available_chunks":[]
        }
        ```

        "status" being one of "not available", "available" or "incomplete"
        """
        return self._call("upload_infos", [sha256_hash, project_id])

    def user_tasks_status(self, project_id: int = None) -> List[dict]:
        """
            Returns list of user tasks. Each task being serialized like so:

        ```
        {
            "object_type": "task",
            "id": user_task_instance.id,
            "description": user_task_instance.description,
            "created_at": user_task_instance.created_at.isoformat(),
            "started_at": user_task_instance.started_at.isoformat(),
            "finished_at": user_task_instance.finished_at.isoformat(),
            "failed_at": user_task_instance.failed_at.isoformat(),
            "project_id": user_task_instance.project_id
        }
        ```
        """
        return self._call("user_tasks_status", [project_id])
