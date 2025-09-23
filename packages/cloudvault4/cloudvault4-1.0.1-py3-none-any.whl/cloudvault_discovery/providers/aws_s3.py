"""
AWS S3 provider for CloudVault
Handles S3 bucket discovery with both authenticated and unauthenticated access methods,
ACL checking, owner identification, and proper rate limiting.
"""
import logging
import requests
from typing import List, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
try:
    import boto3
    from boto3.session import Session
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
from ..core.worker import BaseWorker, WorkerResult, AccessLevel
from ..core.queue_manager import ProviderType
logger = logging.getLogger(__name__)
class AWSS3Worker(BaseWorker):
    """
    AWS S3 worker for bucket discovery
    Supports both authenticated (via AWS credentials) and unauthenticated methods.
    Authenticated mode provides better rate limits, ACL checking, and owner identification.
    """
    def __init__(self, config, queue_manager, result_handler, keywords=None, *args, **kwargs):
        """
        Initialize AWS S3 worker
        Args:
            config: Configuration object with AWS settings
            queue_manager: Queue manager instance
            result_handler: Function to handle found buckets
            keywords: List of keywords for interesting content detection
        """
        super().__init__("aws", config, queue_manager, result_handler, keywords, *args, **kwargs)
        self.aws_config = config.aws
        self.use_boto3 = BOTO3_AVAILABLE and self.aws_config.is_authenticated()
        if self.use_boto3:
            self._init_boto3_session()
        else:
            self._init_http_session()
        logger.info(f"AWS S3 worker initialized (authenticated: {self.use_boto3})")
    def _init_boto3_session(self):
        try:
            self.session = Session(
                aws_access_key_id=self.aws_config.access_key,
                aws_secret_access_key=self.aws_config.secret_key,
                region_name=self.aws_config.region
            )
            boto_config = BotoConfig(
                max_pool_connections=50,
                retries={'max_attempts': 3, 'mode': 'adaptive'},
                read_timeout=self.aws_config.timeout,
                connect_timeout=self.aws_config.timeout
            )
            self.s3_client = self.session.client('s3', config=boto_config)
            self.s3_resource = self.session.resource('s3', config=boto_config)
            try:
                self.s3_client.list_buckets(MaxKeys=1)
                logger.info("AWS credentials validated successfully")
            except ClientError as e:
                if e.response['Error']['Code'] in ['InvalidAccessKeyId', 'SignatureDoesNotMatch']:
                    logger.warning("Invalid AWS credentials, falling back to HTTP mode")
                    raise
                else:
                    logger.info("AWS credentials valid but limited permissions")
        except Exception as e:
            logger.warning(f"Failed to initialize boto3 session, falling back to HTTP: {e}")
            self.use_boto3 = False
            self._init_http_session()
    def _init_http_session(self):
        self.http_session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=2,
            raise_on_status=False
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=15,
            pool_maxsize=100,
            pool_block=False
        )
        self.http_session.mount("http://", adapter)
        self.http_session.mount("https://", adapter)
        
        self.connect_timeout = min(self.aws_config.timeout // 3, 10)
        self.read_timeout = self.aws_config.timeout - self.connect_timeout
        self.http_session.timeout = self.aws_config.timeout
    def get_provider_type(self):
        return ProviderType.AWS
    def check_target(self, target) -> WorkerResult:
        """
        Check if an S3 bucket exists and get its properties
        Args:
            target: BucketTarget to check
        Returns:
            WorkerResult: Result of the bucket check
        """
        bucket_name = target.name
        bucket_url = f"https://{bucket_name}.s3.amazonaws.com"
        if self.use_boto3:
            return self._check_bucket_boto3(bucket_name, bucket_url, target)
        else:
            return self._check_bucket_http(bucket_name, bucket_url, target)
    def _check_bucket_boto3(self, bucket_name: str, bucket_url: str, target) -> WorkerResult:
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
            
            result = WorkerResult(
                bucket_name=bucket_name,
                provider="aws",
                found=True,
                access_level=AccessLevel.PRIVATE,
                bucket_url=bucket_url
            )
            
            try:
                location = self.s3_client.get_bucket_location(Bucket=bucket_name)
                region = location.get('LocationConstraint') or 'us-east-1'
                result.region = region
                if region == 'us-east-1':
                    result.bucket_url = f"https://{bucket_name}.s3.amazonaws.com"
                else:
                    result.bucket_url = f"https://{bucket_name}.s3.{region}.amazonaws.com"
            except ClientError:
                result.region = 'unknown'
                result.bucket_url = bucket_url
            
            try:
                acl = self.s3_client.get_bucket_acl(Bucket=bucket_name)
                owner_info = acl.get('Owner', {})
                
                display_name = owner_info.get('DisplayName', '')
                owner_id = owner_info.get('ID', '')
                
                if display_name and display_name.strip() != '':
                    result.owner = display_name.strip()
                elif owner_id and len(owner_id) > 10:
                    short_id = owner_id[:12]
                    result.owner = f"AWS-{short_id}"
                else:
                    result.owner = '(unknown)'
                    
                result.owner_id = owner_id
                result.access_level = self._determine_access_level_from_acl(acl)
                result.acl_info = self._format_acl_info(acl)
                
                result.permission_analysis = self._enhance_permission_analysis(acl)
                
                if not self._validate_bucket_access(bucket_name, result.access_level):
                    logger.debug(f"Bucket {bucket_name} validation failed - marking as false positive")
                    result.found = False
                    result.error_message = "Validation failed - possible false positive"
                    return result
                    
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'AccessDenied':
                    result.access_level = AccessLevel.PRIVATE
                    result.acl_info = {'error': 'Access denied to ACL'}
                    result.owner = '(access denied)'
                    
                    try:
                        http_owner = self._extract_owner_from_http(bucket_name, result.bucket_url)
                        if http_owner and http_owner != '(unknown)':
                            result.owner = http_owner
                    except Exception as http_e:
                        logger.debug(f"HTTP owner extraction failed for {bucket_name}: {http_e}")
                else:
                    logger.warning(f"Error getting ACL for {bucket_name}: {e}")
                    result.owner = '(unknown)'
                    
                    try:
                        http_owner = self._extract_owner_from_http(bucket_name, result.bucket_url)
                        if http_owner and http_owner != '(unknown)':
                            result.owner = http_owner
                    except Exception as http_e:
                        logger.debug(f"HTTP owner extraction failed for {bucket_name}: {http_e}")
            
            if result.is_public or not self.config.only_interesting:
                try:
                    self._get_bucket_contents(bucket_name, result)
                except ClientError:
                    pass
            
            return result
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                return WorkerResult(
                    bucket_name=bucket_name,
                    provider="aws", 
                    found=False,
                    access_level=AccessLevel.UNKNOWN,
                    bucket_url=bucket_url,
                    error_message="Bucket does not exist"
                )
            elif error_code == 'AccessDenied':
                if self._is_real_bucket_access_denied(bucket_name):
                    result = WorkerResult(
                        bucket_name=bucket_name,
                        provider="aws",
                        found=True,
                        access_level=AccessLevel.PRIVATE,
                        bucket_url=bucket_url,
                        owner='(access denied)',
                        error_message="Access denied"
                    )
                    
                    try:
                        http_owner = self._extract_owner_from_http(bucket_name, bucket_url)
                        if http_owner and http_owner != '(unknown)':
                            result.owner = http_owner
                    except Exception as http_e:
                        logger.debug(f"HTTP owner extraction failed for {bucket_name}: {http_e}")
                    
                    return result
                else:
                    return WorkerResult(
                        bucket_name=bucket_name,
                        provider="aws",
                        found=False,
                        access_level=AccessLevel.UNKNOWN,
                        bucket_url=bucket_url,
                        error_message="False positive - bucket does not exist"
                    )
            else:
                raise
    def _check_bucket_http(self, bucket_name: str, bucket_url: str, target) -> WorkerResult:
        try:
            s3_url = "http://s3-1-w.amazonaws.com"
            
            timeout_tuple = (self.connect_timeout, self.read_timeout)
            
            response = self.http_session.head(
                s3_url,
                headers={"Host": bucket_url.replace("https://", "").replace("http://", "")},
                timeout=timeout_tuple
            )
            
            if response.status_code == 307:
                location = response.headers.get('Location', bucket_url)
                result = WorkerResult(
                    bucket_name=bucket_name,
                    provider="aws",
                    found=True,
                    access_level=AccessLevel.UNKNOWN,
                    bucket_url=location
                )
                try:
                    list_response = self.http_session.get(
                        location,
                        timeout=timeout_tuple
                    )
                    if list_response.status_code == 200:
                        result.access_level = AccessLevel.PUBLIC_READ
                        content = list_response.text
                        if '<Key>' in content:
                            objects = self._extract_objects_from_xml(content)
                            result.sample_objects = objects[:10]  # First 10 objects
                            result.object_count = len(objects)
                            if self.keywords:
                                result.interesting_objects = self._check_for_interesting_content(objects)
                    elif list_response.status_code == 403:
                        result.access_level = AccessLevel.PRIVATE
                except requests.exceptions.Timeout as te:
                    logger.debug(f"Timeout checking bucket contents for {bucket_name}: {te}")
                    result.error_message = "Content check timeout"
                except Exception as e:
                    logger.debug(f"Error checking bucket contents for {bucket_name}: {e}")
                    result.error_message = f"Content check error: {str(e)}"
                return result
                
            elif response.status_code == 404:
                return WorkerResult(
                    bucket_name=bucket_name,
                    provider="aws",
                    found=False,
                    access_level=AccessLevel.UNKNOWN,
                    bucket_url=bucket_url
                )
            elif response.status_code == 503 and response.reason == "Slow Down":
                raise Exception("AWS rate limit exceeded")
            else:
                return WorkerResult(
                    bucket_name=bucket_name,
                    provider="aws",
                    found=False,
                    access_level=AccessLevel.UNKNOWN,
                    bucket_url=bucket_url,
                    error_message=f"HTTP {response.status_code}"
                )
                
        except requests.exceptions.ConnectTimeout:
            logger.debug(f"Connection timeout checking bucket {bucket_name}")
            return WorkerResult(
                bucket_name=bucket_name,
                provider="aws",
                found=False,
                access_level=AccessLevel.UNKNOWN,
                bucket_url=bucket_url,
                error_message="Connection timeout"
            )
        except requests.exceptions.ReadTimeout:
            logger.debug(f"Read timeout checking bucket {bucket_name}")
            return WorkerResult(
                bucket_name=bucket_name,
                provider="aws",
                found=False,
                access_level=AccessLevel.UNKNOWN,
                bucket_url=bucket_url,
                error_message="Read timeout"
            )
        except requests.exceptions.Timeout:
            logger.debug(f"General timeout checking bucket {bucket_name}")
            return WorkerResult(
                bucket_name=bucket_name,
                provider="aws",
                found=False,
                access_level=AccessLevel.UNKNOWN,
                bucket_url=bucket_url,
                error_message="Timeout"
            )
        except requests.exceptions.ConnectionError as ce:
            logger.debug(f"Connection error checking bucket {bucket_name}: {ce}")
            return WorkerResult(
                bucket_name=bucket_name,
                provider="aws",
                found=False,
                access_level=AccessLevel.UNKNOWN,
                bucket_url=bucket_url,
                error_message="Connection error"
            )
        except Exception as e:
            logger.debug(f"Error checking bucket {bucket_name}: {e}")
            raise
    def _determine_access_level_from_acl(self, acl: dict) -> AccessLevel:
        grants = acl.get('Grants', [])
        public_read = False
        public_write = False
        public_read_acp = False
        public_write_acp = False
        authenticated_read = False
        authenticated_write = False
        authenticated_read_acp = False
        authenticated_write_acp = False
        
        for grant in grants:
            grantee = grant.get('Grantee', {})
            permission = grant.get('Permission', '')
            
            if grantee.get('Type') == 'Group':
                uri = grantee.get('URI', '')
                if 'AllUsers' in uri:
                    if permission == 'READ':
                        public_read = True
                    elif permission == 'WRITE':
                        public_write = True
                    elif permission == 'READ_ACP':
                        public_read_acp = True
                    elif permission == 'WRITE_ACP':
                        public_write_acp = True
                    elif permission == 'FULL_CONTROL':
                        public_read = public_write = public_read_acp = public_write_acp = True
                elif 'AuthenticatedUsers' in uri:
                    if permission == 'READ':
                        authenticated_read = True
                    elif permission == 'WRITE':
                        authenticated_write = True
                    elif permission == 'READ_ACP':
                        authenticated_read_acp = True
                    elif permission == 'WRITE_ACP':
                        authenticated_write_acp = True
                    elif permission == 'FULL_CONTROL':
                        authenticated_read = authenticated_write = True
                        authenticated_read_acp = authenticated_write_acp = True
        
        if public_write and public_read:
            return AccessLevel.PUBLIC_READ_WRITE
        elif public_write:
            return AccessLevel.PUBLIC_WRITE
        elif public_read:
            return AccessLevel.PUBLIC_READ
        elif authenticated_write and authenticated_read:
            return AccessLevel.AUTHENTICATED_READ
        elif authenticated_read:
            return AccessLevel.AUTHENTICATED_READ
        else:
            return AccessLevel.PRIVATE

    def _format_acl_info(self, acl_info: dict) -> str:
        if not acl_info:
            return "No ACL information available"
        
        formatted = []
        if acl_info.get('owner'):
            formatted.append(f"Owner: {acl_info['owner']}")
        
        grants = acl_info.get('grants', [])
        if grants:
            formatted.append(f"Grants ({len(grants)}):")
            for grant in grants[:5]:
                grantee = grant.get('grantee', {})
                permission = grant.get('permission', 'Unknown')
                
                if grantee.get('type') == 'Group':
                    grantee_name = grantee.get('uri', '').split('/')[-1] or 'Unknown Group'
                elif grantee.get('type') == 'CanonicalUser':
                    grantee_name = grantee.get('display_name') or grantee.get('id', 'Unknown User')[:20]
                else:
                    grantee_name = str(grantee.get('display_name') or grantee.get('id', 'Unknown'))[:20]
                
                formatted.append(f"  - {grantee_name}: {permission}")
            
            if len(grants) > 5:
                formatted.append(f"  ... and {len(grants) - 5} more grants")
        
        return '\n'.join(formatted)

    def _extract_owner_from_http(self, bucket_name: str, bucket_url: str) -> Optional[str]:
        try:
            response = self.http_session.head(bucket_url, timeout=self.aws_config.timeout)
            
            server_header = response.headers.get('Server', '').lower()
            if 'amazon' in server_header or 'aws' in server_header:
                return f"AWS-{bucket_name}"
            
            response = self.http_session.get(bucket_url, timeout=self.aws_config.timeout)
            if response.status_code == 200:
                try:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response.content)
                    
                    for elem in root.iter():
                        if elem.tag.endswith('Owner'):
                            owner_id = elem.find('.//{*}ID')
                            display_name = elem.find('.//{*}DisplayName')
                            
                            if display_name is not None and display_name.text:
                                return display_name.text
                            elif owner_id is not None and owner_id.text:
                                return f"AWS-{owner_id.text[:12]}"
                    
                    return f"AWS-{bucket_name}"
                    
                except Exception as e:
                    logger.debug(f"XML parsing error for {bucket_name}: {e}")
                    return f"AWS-{bucket_name}"
            
        except Exception as e:
            logger.debug(f"HTTP owner extraction failed for {bucket_name}: {e}")
        
        return None

    def _enhance_aws_permission_analysis(self, acl_info: dict, bucket_name: str) -> dict:
        analysis = {
            'public_read': False,
            'public_write': False,
            'authenticated_read': False,
            'authenticated_write': False,
            'owner_permissions': [],
            'risk_level': 'LOW',
            'public_access_methods': [],
            'authenticated_access_methods': []
        }
        
        for grant in acl_info.get('Grants', []):
            grantee = grant.get('Grantee', {})
            permission = grant.get('Permission', '')
            
            if grantee.get('Type') == 'Group':
                uri = grantee.get('URI', '')
                if 'AllUsers' in uri:
                    if permission == 'READ':
                        analysis['public_read'] = True
                    elif permission == 'WRITE':
                        analysis['public_write'] = True
                    elif permission == 'READ_ACP':
                        analysis['public_read_acp'] = True
                    elif permission == 'WRITE_ACP':
                        analysis['public_write_acp'] = True
                elif 'AuthenticatedUsers' in uri:
                    if permission == 'READ':
                        analysis['authenticated_read'] = True
                    elif permission == 'WRITE':
                        analysis['authenticated_write'] = True
                    elif permission == 'READ_ACP':
                        analysis['authenticated_read_acp'] = True
                    elif permission == 'WRITE_ACP':
                        analysis['authenticated_write_acp'] = True
            elif grantee.get('Type') == 'CanonicalUser':
                owner_id = acl_info.get('Owner', {}).get('ID', '')
                if grantee.get('ID') == owner_id:
                    analysis['owner_permissions'].append(permission)
        
        if analysis['public_write'] or analysis['public_write_acp']:
            analysis['risk_level'] = 'CRITICAL'
        elif analysis['public_read'] or analysis['authenticated_write']:
            analysis['risk_level'] = 'HIGH'
        elif analysis['authenticated_read'] or analysis['public_read_acp']:
            analysis['risk_level'] = 'MEDIUM'
        
        return analysis

    def _validate_bucket_access(self, bucket_name: str, access_level: AccessLevel) -> bool:
        """
        Bucket'ın gerçekten erişilebilir olup olmadığını doğrular
        False positive'leri azaltmak için kullanılır
        """
        try:
            if access_level in [AccessLevel.PUBLIC_READ, AccessLevel.PUBLIC_READ_WRITE]:
                test_url = f"https://{bucket_name}.s3.amazonaws.com/"
                response = self.http_session.head(test_url, timeout=(5, 10))
                if response.status_code in [200, 403]:
                    return True
                elif response.status_code == 404:
                    return False
            
            try:
                self.s3_client.get_bucket_location(Bucket=bucket_name)
                return True
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchBucket':
                    return False
                elif error_code == 'AccessDenied':
                    return True
                    
        except Exception as e:
            logger.debug(f"Validation error for {bucket_name}: {e}")
            return True
            
        return True

    def _is_real_bucket_access_denied(self, bucket_name: str) -> bool:
        """
        Access denied hatası gerçek bir bucket'tan mı geliyor yoksa false positive mi?
        """
        try:
            test_urls = [
                f"https://{bucket_name}.s3.amazonaws.com/",
                f"https://s3.amazonaws.com/{bucket_name}/",
            ]
            
            for url in test_urls:
                try:
                    response = self.http_session.head(url, timeout=(3, 5))
                    if response.status_code == 403:
                        return True
                    elif response.status_code == 404:
                        return False
                except:
                    continue
                    
            return True
            
        except Exception:
            return True
    def _get_bucket_contents(self, bucket_name: str, result: WorkerResult):
        try:
            bucket = self.s3_resource.Bucket(bucket_name)
            objects = []
            for obj in bucket.objects.limit(100):
                objects.append(obj.key)
            result.sample_objects = objects[:10]
            result.object_count = len(objects)
            if self.keywords and objects:
                result.interesting_objects = self._check_for_interesting_content(objects)
        except ClientError as e:
            logger.debug(f"Error listing objects in {bucket_name}: {e}")
    def _extract_objects_from_xml(self, xml_content: str) -> List[str]:
        import re
        pattern = r'<Key>(.*?)</Key>'
        matches = re.findall(pattern, xml_content)
        return matches
    def is_rate_limit_error(self, error: Exception) -> bool:
        error_str = str(error).lower()
        if 'rate limit' in error_str or 'slow down' in error_str:
            return True
        if isinstance(error, ClientError):
            error_code = error.response.get('Error', {}).get('Code', '')
            if error_code in ['SlowDown', 'RequestLimitExceeded', 'Throttling']:
                return True
        if hasattr(error, 'response') and hasattr(error.response, 'status_code'):
            if error.response.status_code == 503:
                return True
        return False