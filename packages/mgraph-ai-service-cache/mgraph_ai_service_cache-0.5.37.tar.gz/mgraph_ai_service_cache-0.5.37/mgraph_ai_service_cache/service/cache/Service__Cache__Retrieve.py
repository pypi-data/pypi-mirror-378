from typing import Optional, Dict, Any, List
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                      import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                     import Random_Guid
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now          import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id           import Safe_Str__Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                            import type_safe
from osbot_utils.utils.Http                                                               import url_join_safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash  import Safe_Str__Cache_Hash
from mgraph_ai_service_cache.schemas.cache.Schema__Cache__Entry__Details                  import Schema__Cache__Entry__Details
from mgraph_ai_service_cache.schemas.cache.Schema__Cache__Metadata                        import Schema__Cache__Metadata
from mgraph_ai_service_cache.schemas.cache.Schema__Cache__Retrieve__Success               import Schema__Cache__Retrieve__Success
from mgraph_ai_service_cache.schemas.cache.consts__Cache_Service                          import DEFAULT_CACHE__NAMESPACE
from mgraph_ai_service_cache.schemas.cache.enums.Enum__Cache__Data_Type                   import Enum__Cache__Data_Type
from mgraph_ai_service_cache.schemas.errors.Schema__Cache__Error__Gone                    import Schema__Cache__Error__Gone
from mgraph_ai_service_cache.schemas.errors.Schema__Cache__Error__Not_Found               import Schema__Cache__Error__Not_Found
from mgraph_ai_service_cache.service.cache.Cache__Service                                 import Cache__Service

# todo: rename to Cache__Service__Retrieve

class Service__Cache__Retrieve(Type_Safe):                                            # Service layer for cache retrieval operations
    cache_service : Cache__Service                                                    # Underlying cache service
    
    @type_safe
    def retrieve_by_hash(self, cache_hash : Safe_Str__Cache_Hash,
                               namespace  : Safe_Str__Id        = DEFAULT_CACHE__NAMESPACE
                         ) -> Optional[Schema__Cache__Retrieve__Success]:               # Retrieve entry by content hash

        result = self.cache_service.retrieve_by_hash(cache_hash, namespace)             # Use cache service to get the data
        
        if result is None:
            return None                                                                 # Caller decides how to handle not found

        metadata = self._build_metadata(result)                                         # Convert to Type_Safe response schema
        
        return Schema__Cache__Retrieve__Success(data      = result.get("data")     ,
                                                metadata  = metadata               ,
                                                data_type = self._determine_data_type(result))
    
    @type_safe
    def retrieve_by_id(self, cache_id  : Random_Guid,
                             namespace : Safe_Str__Id = None
                        ) -> Optional[Schema__Cache__Retrieve__Success]:                # Retrieve entry by cache ID

        result = self.cache_service.retrieve_by_id(cache_id, namespace)                 # Use cache service to get the data
        
        if result is None:
            return None

        metadata = self._build_metadata(result)                                         # Convert to Type_Safe response
        
        return Schema__Cache__Retrieve__Success(data      = result.get("data")     ,
                                                metadata  = metadata               ,
                                                data_type = self._determine_data_type(result))
    
    @type_safe
    def check_exists(self, cache_hash : Safe_Str__Cache_Hash,
                           namespace  : Safe_Str__Id        = DEFAULT_CACHE__NAMESPACE
                     ) -> bool:                                                       # Check if cache entry exists

        handler   = self.cache_service.get_or_create_handler(namespace)
        
        with handler.fs__refs_hash.file__json(Safe_Str__Id(str(cache_hash))) as ref_fs:
            return ref_fs.exists()
    
    @type_safe
    def get_entry_details(self, cache_id  : Random_Guid,
                                namespace : Safe_Str__Id = DEFAULT_CACHE__NAMESPACE
                          ) -> Schema__Cache__Entry__Details:                                # Get detailed information about cache entry
        details = self.cache_service.retrieve_by_id__config(cache_id, namespace)            #

        return Schema__Cache__Entry__Details(cache_id      = details.get("cache_id"         ),                              # todo: we don't need to do this here (since this should had been provided by self.retrieve_service.get_entry_details)
                                             cache_hash    = details.get("hash"             ),
                                             namespace     = details.get("namespace"        ),
                                             strategy      = details.get("strategy"         ),
                                             all_paths     = details.get("all_paths"        ),
                                             content_paths = details.get("content_paths"    ),
                                             file_type     = details.get("file_type", "json"),
                                             timestamp     = details.get("timestamp")       )


    def get_entry_details__all(self, cache_id  : Random_Guid,
                                     namespace : Safe_Str__Id = DEFAULT_CACHE__NAMESPACE
                                ) -> Optional[Dict[str, Any]]:                                # Get detailed information about cache entry
        details  = self.get_entry_details(cache_id=cache_id, namespace=namespace)
        if not details:
            return None

        all_details   = {}
        content_paths = details.content_paths                                            # capture this path, since we don't want to show it (i.e. don't add the file's content)
        storage_fs    = self.cache_service.storage_fs()
        for file_type, file_paths in details.all_paths.items():
            for file_path in file_paths:
                if file_path not in content_paths:
                    full_file_path             = url_join_safe(str(namespace), file_path)
                    if full_file_path:
                        file_contents          = storage_fs.file__json(full_file_path)          # all these files are json files
                        all_details[file_path] = file_contents
        return dict(by_id   =  details.json()   ,
                    details = all_details)

    @type_safe
    def get_not_found_error(self, resource_id : Safe_Str__Id         = None,
                                  cache_hash  : Safe_Str__Cache_Hash = None,
                                  cache_id    : Random_Guid          = None,
                                  namespace   : Safe_Str__Id         = None
                            ) -> Schema__Cache__Error__Not_Found:                                                          # Build not found error response
        return Schema__Cache__Error__Not_Found(error_type    = "NOT_FOUND"                                           ,     # todo: refactor error_type to Enum
                                               message       = "The requested cache entry was not found"             ,
                                               resource_type = "cache_entry"                                         ,
                                               resource_id   = resource_id                                           ,
                                               cache_hash    = cache_hash                                            ,
                                               cache_id      = cache_id                                              ,
                                               namespace     = namespace                                              )
    
    @type_safe
    def get_expired_error(self, cache_id   : Random_Guid   = None,
                                expired_at : Timestamp_Now = None,
                                ttl_hours  : Safe_UInt     = None,
                                namespace  : Safe_Str__Id  = None
                          ) -> Schema__Cache__Error__Gone:                                                                  # Build expired error response
        return Schema__Cache__Error__Gone(error_type = "EXPIRED"                                                ,           # todo: refactor error_type to Enum
                                          message    = "The cache entry has expired and is no longer available" ,
                                          cache_id   = cache_id                                                 ,
                                          expired_at = expired_at                                               ,
                                          ttl_hours  = ttl_hours                                                ,
                                          namespace  = namespace                                                 )
    
    def _build_metadata(self, cache_result: Dict[str, Any]) -> Schema__Cache__Metadata:                                     # Build metadata from cache result
        metadata_raw = cache_result.get("metadata", {})

        # todo: this should be able to just be Schema__Cache__Metadata.from_json(metadata_raw),
        #       in fact metadata_raw should be Type_Safe
        return Schema__Cache__Metadata(cache_id         = metadata_raw.get("cache_id")         ,
                                       cache_hash       = metadata_raw.get("cache_hash")       ,
                                       cache_key        = metadata_raw.get("cache_key")        ,
                                       file_id          = metadata_raw.get("file_id")          ,
                                       namespace        = metadata_raw.get("namespace")        ,
                                       strategy         = metadata_raw.get("strategy")         ,
                                       stored_at        = metadata_raw.get("stored_at")        ,
                                       file_type        = metadata_raw.get("file_type", "json"),
                                       content_encoding = metadata_raw.get("content_encoding") ,
                                       content_size     = metadata_raw.get("content__size", 0)  )

    # todo: we should just be able to use Enum__Cache__Data_Type from cache_result.get("data_type") and let Type_Safe handle the rest
    def _determine_data_type(self, cache_result: Dict[str, Any]) -> Enum__Cache__Data_Type:  # Determine data type from result
        data_type_str = cache_result.get("data_type", "string")
        
        if data_type_str == "binary":
            return Enum__Cache__Data_Type.BINARY
        elif data_type_str == "json":
            return Enum__Cache__Data_Type.JSON
        else:
            return Enum__Cache__Data_Type.STRING
    
    def _is_expired(self, id_ref: Dict[str, Any]) -> bool:                           # Check if cache entry has expired
        # TODO: Implement TTL expiration logic
        # For now, always return False (nothing expires)
        return False