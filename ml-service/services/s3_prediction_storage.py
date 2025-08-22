"""
S3-Based Prediction Storage Service
==================================

Stores and retrieves playoff predictions from S3 for persistent caching
and better scalability than in-memory cache.
"""

import json
import boto3
import gzip
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging
import hashlib
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class S3PredictionStorage:
    """S3-based storage for playoff predictions with intelligent retrieval"""
    
    def __init__(self, s3_service=None):
        self.s3_service = s3_service
        if s3_service:
            self.bucket_name = s3_service.bucket_name
            self.s3_client = s3_service.s3_client
        else:
            # Fallback initialization
            self.bucket_name = "my-nba-model-results"
            self.s3_client = boto3.client('s3')
    
    def _generate_prediction_key(self, operation: str, **params) -> str:
        """Generate S3 key for prediction storage"""
        # Create deterministic key from operation and parameters
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:12]
        
        # Include date for organization
        date_str = datetime.now().strftime('%Y/%m/%d')
        
        return f"playoff-predictions/{date_str}/{operation}/{param_hash}.json.gz"
    
    def _generate_daily_key(self, operation: str, **params) -> str:
        """Generate daily-based key (for operations that change daily)"""
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        return f"playoff-predictions/daily/{operation}-{date_str}-{param_hash}.json.gz"
    
    def store_prediction(self, operation: str, data: Dict, ttl_hours: int = 24, **params) -> str:
        """Store prediction result in S3 with metadata"""
        try:
            key = self._generate_prediction_key(operation, **params)
            
            # Prepare data with metadata
            storage_data = {
                'operation': operation,
                'parameters': params,
                'data': data,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=ttl_hours)).isoformat(),
                'ttl_hours': ttl_hours,
                'version': '1.0'
            }
            
            # Compress and store
            json_data = json.dumps(storage_data, default=str)
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                Metadata={
                    'operation': operation,
                    'created-at': datetime.now().isoformat(),
                    'expires-at': (datetime.now() + timedelta(hours=ttl_hours)).isoformat(),
                    'parameters': json.dumps(params)[:1000]  # Truncate if too long
                }
            )
            
            logger.info(f"Stored {operation} prediction in S3: {key}")
            return key
            
        except Exception as e:
            logger.error(f"Error storing prediction to S3: {e}")
            raise
    
    def retrieve_prediction(self, operation: str, **params) -> Optional[Dict]:
        """Retrieve prediction from S3 if valid"""
        try:
            key = self._generate_prediction_key(operation, **params)
            
            # Try to get the object
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            
            # Decompress and parse
            compressed_data = response['Body'].read()
            json_data = gzip.decompress(compressed_data).decode('utf-8')
            storage_data = json.loads(json_data)
            
            # Check if expired
            expires_at = datetime.fromisoformat(storage_data['expires_at'])
            if datetime.now() > expires_at:
                logger.info(f"S3 prediction expired: {key}")
                # Delete expired prediction
                self._delete_prediction(key)
                return None
            
            logger.info(f"Retrieved {operation} prediction from S3: {key}")
            return storage_data['data']
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.info(f"No cached prediction found for {operation}")
                return None
            else:
                logger.error(f"Error retrieving prediction from S3: {e}")
                return None
        except Exception as e:
            logger.error(f"Error parsing prediction from S3: {e}")
            return None
    
    def store_daily_prediction(self, operation: str, data: Dict, **params) -> str:
        """Store prediction that's valid for the entire day"""
        try:
            key = self._generate_daily_key(operation, **params)
            
            storage_data = {
                'operation': operation,
                'parameters': params,
                'data': data,
                'created_at': datetime.now().isoformat(),
                'valid_date': datetime.now().strftime('%Y-%m-%d'),
                'version': '1.0'
            }
            
            json_data = json.dumps(storage_data, default=str)
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                Metadata={
                    'operation': operation,
                    'valid-date': datetime.now().strftime('%Y-%m-%d'),
                    'created-at': datetime.now().isoformat()
                }
            )
            
            logger.info(f"Stored daily {operation} prediction in S3: {key}")
            return key
            
        except Exception as e:
            logger.error(f"Error storing daily prediction to S3: {e}")
            raise
    
    def retrieve_daily_prediction(self, operation: str, **params) -> Optional[Dict]:
        """Retrieve daily prediction from S3"""
        try:
            key = self._generate_daily_key(operation, **params)
            
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            compressed_data = response['Body'].read()
            json_data = gzip.decompress(compressed_data).decode('utf-8')
            storage_data = json.loads(json_data)
            
            # Check if still valid for today
            valid_date = storage_data['valid_date']
            today = datetime.now().strftime('%Y-%m-%d')
            
            if valid_date != today:
                logger.info(f"Daily prediction outdated: {key}")
                self._delete_prediction(key)
                return None
            
            logger.info(f"Retrieved daily {operation} prediction from S3: {key}")
            return storage_data['data']
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.info(f"No daily prediction found for {operation}")
                return None
            else:
                logger.error(f"Error retrieving daily prediction from S3: {e}")
                return None
        except Exception as e:
            logger.error(f"Error parsing daily prediction from S3: {e}")
            return None
    
    def _delete_prediction(self, key: str):
        """Delete expired or invalid prediction"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Deleted expired prediction: {key}")
        except Exception as e:
            logger.warning(f"Could not delete expired prediction {key}: {e}")
    
    def list_stored_predictions(self, operation: str = None, limit: int = 100) -> List[Dict]:
        """List stored predictions with metadata"""
        try:
            prefix = "playoff-predictions/"
            if operation:
                # List for specific operation across all dates
                today = datetime.now().strftime('%Y/%m/%d')
                prefix = f"playoff-predictions/{today}/{operation}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=limit
            )
            
            predictions = []
            for obj in response.get('Contents', []):
                # Extract metadata
                try:
                    head_response = self.s3_client.head_object(
                        Bucket=self.bucket_name,
                        Key=obj['Key']
                    )
                    
                    predictions.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'operation': head_response.get('Metadata', {}).get('operation'),
                        'created_at': head_response.get('Metadata', {}).get('created-at'),
                        'expires_at': head_response.get('Metadata', {}).get('expires-at')
                    })
                except Exception as e:
                    logger.warning(f"Could not get metadata for {obj['Key']}: {e}")
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error listing stored predictions: {e}")
            return []
    
    def cleanup_expired_predictions(self) -> int:
        """Clean up expired predictions from S3"""
        try:
            # List all playoff predictions
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix="playoff-predictions/"
            )
            
            deleted_count = 0
            now = datetime.now()
            
            for obj in response.get('Contents', []):
                try:
                    # Check metadata for expiration
                    head_response = self.s3_client.head_object(
                        Bucket=self.bucket_name,
                        Key=obj['Key']
                    )
                    
                    expires_at_str = head_response.get('Metadata', {}).get('expires-at')
                    if expires_at_str:
                        expires_at = datetime.fromisoformat(expires_at_str)
                        if now > expires_at:
                            self._delete_prediction(obj['Key'])
                            deleted_count += 1
                    
                    # Also clean up files older than 7 days regardless of expiration
                    if obj['LastModified'] < now - timedelta(days=7):
                        self._delete_prediction(obj['Key'])
                        deleted_count += 1
                        
                except Exception as e:
                    logger.warning(f"Could not check expiration for {obj['Key']}: {e}")
            
            logger.info(f"Cleaned up {deleted_count} expired predictions from S3")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during S3 cleanup: {e}")
            return 0
    
    def get_storage_stats(self) -> Dict:
        """Get statistics about stored predictions"""
        try:
            predictions = self.list_stored_predictions(limit=1000)
            
            # Organize by operation
            by_operation = {}
            total_size = 0
            
            for pred in predictions:
                operation = pred.get('operation', 'unknown')
                if operation not in by_operation:
                    by_operation[operation] = {'count': 0, 'total_size': 0}
                
                by_operation[operation]['count'] += 1
                by_operation[operation]['total_size'] += pred.get('size', 0)
                total_size += pred.get('size', 0)
            
            return {
                'total_predictions': len(predictions),
                'total_size_mb': total_size / (1024 * 1024),
                'by_operation': by_operation,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {'error': str(e)}

def s3_cached_prediction(operation: str, ttl_hours: int = 24, use_daily: bool = False):
    """Decorator for S3-based prediction caching"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Initialize storage (assumes first arg is self with s3_service)
            if hasattr(args[0], 's3_service'):
                storage = S3PredictionStorage(args[0].s3_service)
            else:
                storage = S3PredictionStorage()
            
            # Try to retrieve from S3
            if use_daily:
                cached_result = storage.retrieve_daily_prediction(operation, **kwargs)
            else:
                cached_result = storage.retrieve_prediction(operation, **kwargs)
            
            if cached_result is not None:
                logger.info(f"S3 cache hit for {operation}")
                return cached_result
            
            # Execute function
            logger.info(f"S3 cache miss for {operation}, executing...")
            result = func(*args, **kwargs)
            
            # Store result in S3
            try:
                if use_daily:
                    storage.store_daily_prediction(operation, result, **kwargs)
                else:
                    storage.store_prediction(operation, result, ttl_hours, **kwargs)
            except Exception as e:
                logger.warning(f"Could not store result in S3: {e}")
            
            return result
            
        return wrapper
    return decorator