import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'your-nba-model-bucket')
        self.region = os.getenv('AWS_S3_REGION', 'us-east-2')
        
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=self.region
            )
            logger.info("S3 client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.s3_client = None
    
    def upload_model(self, key: str, model_data: bytes) -> bool:
        """Upload model file to S3"""
        if not self.s3_client:
            logger.error("S3 client not available")
            return False
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"models/{key}",
                Body=model_data,
                ContentType='application/octet-stream'
            )
            logger.info(f"Model uploaded successfully: {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload model {key}: {e}")
            return False
    
    def download_model(self, key: str) -> Optional[bytes]:
        """Download model file from S3"""
        if not self.s3_client:
            logger.error("S3 client not available")
            return None
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=f"models/{key}"
            )
            return response['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.info(f"Model not found in S3: {key}")
            else:
                logger.error(f"Failed to download model {key}: {e}")
            return None
    
    def upload_prediction(self, key: str, prediction_data: dict) -> bool:
        """Upload prediction result to S3"""
        if not self.s3_client:
            logger.error("S3 client not available")
            return False
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(prediction_data, indent=2),
                ContentType='application/json'
            )
            logger.info(f"Prediction uploaded successfully: {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload prediction {key}: {e}")
            return False
    
    def list_predictions(self, prefix: str = "predictions/") -> list:
        """List prediction files in S3"""
        if not self.s3_client:
            logger.error("S3 client not available")
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except ClientError as e:
            logger.error(f"Failed to list predictions: {e}")
            return []
    
    def download_prediction(self, key: str) -> Optional[dict]:
        """Download prediction result from S3"""
        if not self.s3_client:
            logger.error("S3 client not available")
            return None
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return json.loads(response['Body'].read().decode('utf-8'))
        except ClientError as e:
            logger.error(f"Failed to download prediction {key}: {e}")
            return None
    
    def model_exists(self, key: str) -> bool:
        """Check if model exists in S3"""
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=f"models/{key}"
            )
            return True
        except ClientError:
            return False