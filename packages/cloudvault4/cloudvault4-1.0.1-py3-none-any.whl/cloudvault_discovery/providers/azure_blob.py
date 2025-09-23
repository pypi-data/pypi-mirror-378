"""
Azure Blob Storage provider for CloudVault
Implements Azure Blob Storage container discovery with authentication
and public access testing for Azure containers.
"""
import logging
import requests
from typing import List, Optional
from urllib.parse import urlencode
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
try:
    from azure.storage.blob import BlobServiceClient, ContainerClient
    from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
from ..core.worker import BaseWorker, WorkerResult, AccessLevel
from ..core.queue_manager import ProviderType
logger = logging.getLogger(__name__)
class AzureBlobWorker(BaseWorker):
    def __init__(self, config, queue_manager, result_handler, keywords=None, *args, **kwargs):
        super().__init__("azure", config, queue_manager, result_handler, keywords, *args, **kwargs)
        self.azure_config = config.azure
        self.use_azure_sdk = AZURE_AVAILABLE and self.azure_config.is_authenticated()
        if self.use_azure_sdk:
            self._init_azure_client()
        else:
            self._init_http_session()
        logger.info(f"Azure Blob worker initialized (authenticated: {self.use_azure_sdk})")
    def _init_azure_client(self):
        try:
            if self.azure_config.connection_string:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    self.azure_config.connection_string
                )
            elif self.azure_config.account_name and self.azure_config.account_key:
                account_url = f"https://{self.azure_config.account_name}.blob.core.windows.net"
                self.blob_service_client = BlobServiceClient(
                    account_url=account_url,
                    credential=self.azure_config.account_key
                )
            else:
                raise Exception("No Azure credentials provided")
            next(self.blob_service_client.list_containers(max_results=1), None)
            logger.info("Azure credentials validated successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Azure client, falling back to HTTP: {e}")
            self.use_azure_sdk = False
            self._init_http_session()
    def _init_http_session(self):
        self.http_session = requests.Session()
        retry_strategy = Retry(
            total=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=50,
            pool_block=False
        )
        self.http_session.mount("http://", adapter)
        self.http_session.mount("https://", adapter)
        self.http_session.timeout = self.azure_config.timeout

    def _ensure_http_session(self):
        """Lazily initialize HTTP session if not already created."""
        if not hasattr(self, 'http_session') or self.http_session is None:
            self._init_http_session()
    def get_provider_type(self):
        return ProviderType.AZURE
    def check_target(self, target) -> WorkerResult:
        container_name = target.name
        storage_accounts = self._generate_storage_account_names(container_name)
        for account_name in storage_accounts:
            container_url = f"https://{account_name}.blob.core.windows.net/{container_name}"
            if self.use_azure_sdk:
                result = self._check_container_azure(container_name, container_url, account_name, target)
            else:
                result = self._check_container_http(container_name, container_url, account_name, target)
            if result.found:
                return result
        return WorkerResult(
            bucket_name=container_name,
            provider="azure", 
            found=False,
            access_level=AccessLevel.UNKNOWN,
            bucket_url=f"https://[account].blob.core.windows.net/{container_name}"
        )
    def _generate_storage_account_names(self, container_name: str) -> List[str]:
        base_names = [container_name]
        patterns = [
            container_name,
            f"{container_name}storage",
            f"{container_name}data",
            f"{container_name}blob",
            f"storage{container_name}",
            f"data{container_name}",
            f"blob{container_name}",
            container_name.replace("-", ""),
            container_name.replace("_", ""),
        ]
        valid_accounts = []
        for pattern in patterns:
            clean_name = ''.join(c for c in pattern.lower() if c.isalnum())
            if 3 <= len(clean_name) <= 24:
                valid_accounts.append(clean_name)
        return list(dict.fromkeys(valid_accounts))[:5]  # Limit to first 5 to avoid too many requests
    def _check_container_azure(self, container_name: str, container_url: str, account_name: str, target) -> WorkerResult:
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            properties = container_client.get_container_properties()
            result = WorkerResult(
                bucket_name=container_name,
                provider="azure",
                found=True,
                access_level=AccessLevel.PRIVATE,
                bucket_url=container_url
            )
            
            public_access = getattr(properties, 'public_access', None) or 'none'
            if public_access == 'container':
                result.access_level = AccessLevel.PUBLIC_READ
            elif public_access == 'blob':
                result.access_level = AccessLevel.PUBLIC_READ
            else:
                result.access_level = AccessLevel.PRIVATE
            
            result.acl_info = self._get_azure_container_info(properties, account_name)
            
            if result.acl_info and 'owner' in result.acl_info:
                result.owner = result.acl_info['owner']
            else:
                result.owner = f"Azure-{account_name}"
            
            result.permission_analysis = self._enhance_azure_permission_analysis(result.acl_info, public_access)
            
            if not self._validate_azure_container_access(container_name, container_url, result.access_level):
                logger.debug(f"Container {container_name} validation failed - marking as false positive")
                result.found = False
                result.error_message = "Validation failed - possible false positive"
                return result
            
            if result.is_public or not self.config.only_interesting:
                try:
                    self._get_container_contents(container_client, result)
                except Exception as e:
                    logger.debug(f"Error getting container contents: {e}")
            return result
        except ResourceNotFoundError:
            return WorkerResult(
                bucket_name=container_name,
                provider="azure",
                found=False,
                access_level=AccessLevel.UNKNOWN,
                bucket_url=container_url
            )
        except HttpResponseError as e:
            if e.status_code == 403:
                result = WorkerResult(
                    bucket_name=container_name,
                    provider="azure",
                    found=True,
                    access_level=AccessLevel.PRIVATE,
                    bucket_url=container_url,
                    owner='(access denied)',
                    error_message="Access denied"
                )
                
                try:
                    http_owner = self._extract_azure_owner_from_http(container_url, account_name)
                    if http_owner and http_owner != '(unknown)':
                        result.owner = http_owner
                except Exception as http_e:
                    logger.debug(f"HTTP owner extraction failed for {container_name}: {http_e}")
                
                return result
            elif e.status_code == 429:
                raise  # Re-raise rate limit errors
            else:
                return WorkerResult(
                    bucket_name=container_name,
                    provider="azure",
                    found=False,
                    access_level=AccessLevel.UNKNOWN,
                    bucket_url=container_url,
                    error_message=str(e)
                )
        except Exception as e:
            logger.debug(f"Error checking Azure container {container_name}: {e}")
            return WorkerResult(
                bucket_name=container_name,
                provider="azure",
                found=False,
                access_level=AccessLevel.UNKNOWN,
                bucket_url=container_url,
                error_message=str(e)
            )

    def _get_azure_container_info(self, properties, account_name: str) -> dict:
        meta = getattr(properties, "metadata", {}) or {}
        lease = getattr(properties, "lease", None)
        info = {
            "public_access": (getattr(properties, "public_access", None) or "none"),
            "account_name": account_name,
            "owner": f"Azure-{account_name}",
            "owner_type": "storage_account",
            "last_modified": getattr(properties, "last_modified", None),
            "etag": getattr(properties, "etag", None),
            "metadata": meta,
            "lease_status": getattr(properties, "lease_status", getattr(lease, "status", None)),
            "lease_state": getattr(properties, "lease_state", getattr(lease, "state", None)),
        }
        owner_info = meta.get("owner") or meta.get("created_by") or meta.get("department")
        if owner_info:
            info["owner"] = f"Azure-{account_name} ({owner_info})"
        return info

    def _extract_azure_owner_from_http(self, container_url: str, account_name: str) -> str:
        try:
            self._ensure_http_session()
            response = self.http_session.head(container_url, timeout=self.azure_config.timeout)
            
            server_header = response.headers.get('Server', '')
            if 'Windows-Azure-Blob' in server_header:
                return f"Azure-{account_name}"
            
            account_header = response.headers.get('x-ms-account-name', '')
            if account_header:
                return f"Azure-{account_header}"
            
            return f"Azure-{account_name}"
            
        except AttributeError as e:
            logger.debug(f"HTTP session not available for owner extraction: {e}")
            return f"Azure-{account_name}"
        except requests.RequestException as e:
            logger.debug(f"HTTP request failed during owner extraction: {e}")
            return f"Azure-{account_name}"
        except Exception as e:
            logger.debug(f"Unexpected error during HTTP owner extraction: {e}")
            return f"Azure-{account_name}"

    def _enhance_azure_permission_analysis(self, acl_info: dict, public_access: str) -> dict:
        analysis = {
            'public_read': False,
            'public_write': False,
            'container_access': False,
            'blob_access': False,
            'owner_permissions': ['FULL_CONTROL'],
            'risk_level': 'LOW',
            'public_access_level': public_access
        }
        
        if public_access == 'container':
            analysis['public_read'] = True
            analysis['container_access'] = True
            analysis['risk_level'] = 'HIGH'
        elif public_access == 'blob':
            analysis['public_read'] = True
            analysis['blob_access'] = True
            analysis['risk_level'] = 'MEDIUM'
        
        if analysis['container_access']:
            analysis['risk_level'] = 'HIGH'
        
        return analysis

    def _validate_azure_container_access(self, container_name: str, container_url: str, access_level) -> bool:
        """
        Container'ın gerçekten erişilebilir olup olmadığını doğrular
        False positive'leri azaltmak için kullanılır
        """
        try:
            if hasattr(access_level, 'name') and 'PUBLIC' in access_level.name:
                response = self.http_session.head(container_url, timeout=self.azure_config.timeout)
                if response.status_code in [200, 403]:
                    return True
                elif response.status_code == 404:
                    logger.debug(f"Public container validation failed for {container_name}: 404 Not Found")
                    return False
            
            try:
                container_client = self.blob_service_client.get_container_client(container_name)
                container_client.get_container_properties()
                return True
            except ResourceNotFoundError:
                logger.debug(f"Container validation failed for {container_name}: ResourceNotFoundError")
                return False
            except HttpResponseError as e:
                if e.status_code == 403:
                    return self._verify_azure_container_via_http(container_url)
                return False
                    
        except Exception as e:
            logger.debug(f"Azure validation error for {container_name}: {e}")
            return True
            
        return True

    def _verify_azure_container_via_http(self, container_url: str) -> bool:
        try:
            response = self.http_session.head(container_url, timeout=self.azure_config.timeout)
            if response.status_code in [200, 403]:
                return True
            elif response.status_code == 404:
                return False
            return True
            
        except Exception as e:
            logger.debug(f"Azure HTTP verification failed: {e}")
            return True
    def _check_container_http(self, container_name: str, container_url: str, account_name: str, target) -> WorkerResult:
        try:
            response = self.http_session.head(
                container_url,
                timeout=self.azure_config.timeout
            )
            if response.status_code == 200:
                result = WorkerResult(
                    bucket_name=container_name,
                    provider="azure",
                    found=True,
                    access_level=AccessLevel.PUBLIC_READ,
                    bucket_url=container_url
                )
                try:
                    list_url = f"{container_url}?restype=container&comp=list"
                    list_response = self.http_session.get(
                        list_url,
                        timeout=self.azure_config.timeout
                    )
                    if list_response.status_code == 200:
                        content = list_response.text
                        objects = self._extract_objects_from_xml(content)
                        result.sample_objects = objects[:10]
                        result.object_count = len(objects)
                        if self.keywords:
                            result.interesting_objects = self._check_for_interesting_content(objects)
                except Exception as e:
                    logger.debug(f"Error listing blobs in Azure container {container_name}: {e}")
                return result
            elif response.status_code == 403:
                return WorkerResult(
                    bucket_name=container_name,
                    provider="azure",
                    found=True,
                    access_level=AccessLevel.PRIVATE,
                    bucket_url=container_url
                )
            elif response.status_code == 404:
                return WorkerResult(
                    bucket_name=container_name,
                    provider="azure",
                    found=False,
                    access_level=AccessLevel.UNKNOWN,
                    bucket_url=container_url
                )
            elif response.status_code == 429:
                raise Exception("Azure rate limit exceeded")
            else:
                return WorkerResult(
                    bucket_name=container_name,
                    provider="azure",
                    found=False,
                    access_level=AccessLevel.UNKNOWN,
                    bucket_url=container_url,
                    error_message=f"HTTP {response.status_code}"
                )
        except requests.exceptions.Timeout:
            return WorkerResult(
                bucket_name=container_name,
                provider="azure",
                found=False,
                access_level=AccessLevel.UNKNOWN,
                bucket_url=container_url,
                error_message="Timeout"
            )
        except requests.exceptions.ConnectionError as e:
            # Handle DNS resolution errors specifically
            if "NameResolutionError" in str(e) or "Failed to resolve" in str(e) or "nodename nor servname provided" in str(e):
                logger.debug(f"DNS resolution failed for Azure container {container_name} at {account_name}.blob.core.windows.net - container likely doesn't exist")
                return WorkerResult(
                    bucket_name=container_name,
                    provider="azure",
                    found=False,
                    access_level=AccessLevel.UNKNOWN,
                    bucket_url=container_url,
                    error_message="DNS resolution failed - container not found"
                )
            else:
                logger.debug(f"Connection error checking Azure container {container_name}: {e}")
                return WorkerResult(
                    bucket_name=container_name,
                    provider="azure",
                    found=False,
                    access_level=AccessLevel.UNKNOWN,
                    bucket_url=container_url,
                    error_message=f"Connection error: {str(e)}"
                )
        except Exception as e:
            if "rate limit" in str(e).lower() or "429" in str(e):
                raise  # Re-raise rate limit errors
            logger.debug(f"Error checking Azure container {container_name}: {e}")
            return WorkerResult(
                bucket_name=container_name,
                provider="azure",
                found=False,
                access_level=AccessLevel.UNKNOWN,
                bucket_url=container_url,
                error_message=str(e)
            )
    def _get_container_contents(self, container_client, result: WorkerResult):
        try:
            objects = []
            blobs = container_client.list_blobs(max_results=100)
            for blob in blobs:
                objects.append(blob.name)
            result.sample_objects = objects[:10]
            result.object_count = len(objects)
            if self.keywords and objects:
                result.interesting_objects = self._check_for_interesting_content(objects)
        except Exception as e:
            logger.debug(f"Error listing blobs in container: {e}")
    def _extract_objects_from_xml(self, xml_content: str) -> List[str]:
        import re
        pattern = r'<Name>(.*?)</Name>'
        matches = re.findall(pattern, xml_content)
        return matches
    def is_rate_limit_error(self, error: Exception) -> bool:
        error_str = str(error).lower()
        if '429' in error_str or 'rate limit' in error_str or 'throttl' in error_str:
            return True
        if AZURE_AVAILABLE:
            if isinstance(error, HttpResponseError) and error.status_code == 429:
                return True
        if hasattr(error, 'response') and hasattr(error.response, 'status_code'):
            if error.response.status_code == 429:
                return True
        return False