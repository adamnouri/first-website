import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import json
import logging
import os
from typing import Optional, List, Dict
from datetime import datetime, date
import uuid



logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'nba-predictions-bucket')
        self.region = os.getenv('AWS_S3_REGION', 'us-east-2')
        self.predictions_folder = os.getenv('AWS_S3_PREDICTIONS_FOLDER', 'predictions/')
        self.analytics_folder = os.getenv('AWS_S3_ANALYTICS_FOLDER', 'analytics/')
        self.backups_folder = os.getenv('AWS_S3_BACKUPS_FOLDER', 'backups/')
        
        try:
            self.s3_client = boto3.client(
                's3',
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
    
    def generate_prediction_path(self, prediction_uuid: str, game_date: date) -> str:
        """Generate S3 path for prediction JSON file"""
        date_path = game_date.strftime("%Y/%m/%d")
        return f"{self.predictions_folder}{date_path}/{prediction_uuid}.json"
    
    def generate_chart_path(self, prediction_uuid: str, game_date: date) -> str:
        """Generate S3 path for prediction chart image"""
        date_path = game_date.strftime("%Y/%m/%d")
        return f"{self.predictions_folder}{date_path}/{prediction_uuid}_chart.png"
    
    def upload_prediction_with_chart(self, prediction_uuid: str, game_date: date, 
                                   prediction_data: dict, chart_image: bytes) -> tuple[bool, str, str]:
        """Upload both prediction data and chart image to S3"""
        if not self.s3_client:
            logger.error("S3 client not available")
            return False, "", ""
        
        prediction_path = self.generate_prediction_path(prediction_uuid, game_date)
        chart_path = self.generate_chart_path(prediction_uuid, game_date)
        
        try:
            # Upload prediction JSON
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=prediction_path,
                Body=json.dumps(prediction_data, indent=2, default=str),
                ContentType='application/json'
            )
            
            # Upload chart image
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=chart_path,
                Body=chart_image,
                ContentType='image/png'
            )
            
            logger.info(f"Uploaded prediction and chart: {prediction_uuid}")
            return True, prediction_path, chart_path
            
        except ClientError as e:
            logger.error(f"Failed to upload prediction {prediction_uuid}: {e}")
            return False, "", ""
    
    def upload_batch_predictions(self, predictions_with_charts: List[Dict]) -> Dict[str, bool]:
        """Upload multiple predictions and charts in batch"""
        results = {}
        
        for item in predictions_with_charts:
            prediction_uuid = item['prediction_uuid']
            game_date = item['game_date']
            prediction_data = item['prediction_data']
            chart_image = item['chart_image']
            
            success, pred_path, chart_path = self.upload_prediction_with_chart(
                prediction_uuid, game_date, prediction_data, chart_image
            )
            
            results[prediction_uuid] = {
                'success': success,
                'prediction_path': pred_path,
                'chart_path': chart_path
            }
        
        return results
    
    def upload_analytics_summary(self, date_key: str, analytics_data: dict) -> bool:
        """Upload daily/weekly analytics summary"""
        if not self.s3_client:
            logger.error("S3 client not available")
            return False
        
        key = f"{self.analytics_folder}summary_{date_key}.json"
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(analytics_data, indent=2, default=str),
                ContentType='application/json'
            )
            logger.info(f"Analytics summary uploaded: {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload analytics {key}: {e}")
            return False
    
    def get_prediction_with_chart_urls(self, prediction_uuid: str, game_date: date) -> Optional[Dict]:
        """Get prediction data with signed URLs for chart access"""
        prediction_path = self.generate_prediction_path(prediction_uuid, game_date)
        chart_path = self.generate_chart_path(prediction_uuid, game_date)
        
        try:
            # Get prediction data
            prediction_data = self.download_prediction(prediction_path)
            if not prediction_data:
                return None
            
            # Generate signed URL for chart (valid for 1 hour)
            chart_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': chart_path},
                ExpiresIn=3600
            )
            
            return {
                'prediction_data': prediction_data,
                'chart_url': chart_url,
                'prediction_path': prediction_path,
                'chart_path': chart_path
            }
            
        except ClientError as e:
            logger.error(f"Failed to get prediction with chart URLs: {e}")
            return None
    
    def list_predictions_by_date_range(self, start_date: date, end_date: date) -> List[str]:
        """List all prediction files within a date range"""
        if not self.s3_client:
            return []
        
        predictions = []
        current_date = start_date
        
        while current_date <= end_date:
            date_prefix = f"{self.predictions_folder}{current_date.strftime('%Y/%m/%d')}/"
            
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=date_prefix
                )
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        if obj['Key'].endswith('.json'):  # Only JSON prediction files
                            predictions.append(obj['Key'])
                            
            except ClientError as e:
                logger.error(f"Failed to list predictions for {current_date}: {e}")
            
            # Move to next day
            current_date = current_date.replace(day=current_date.day + 1)
        
        return predictions
    
    def cleanup_old_predictions(self, days_to_keep: int = 30) -> int:
        """Remove predictions older than specified days"""
        if not self.s3_client:
            return 0
        
        cutoff_date = datetime.now().date()
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)
        
        deleted_count = 0
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=self.predictions_folder
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Extract date from key path
                    key_parts = obj['Key'].split('/')
                    if len(key_parts) >= 4:  # predictions/YYYY/MM/DD/file
                        try:
                            obj_date = date(
                                int(key_parts[1]),  # year
                                int(key_parts[2]),  # month
                                int(key_parts[3])   # day
                            )
                            
                            if obj_date < cutoff_date:
                                self.s3_client.delete_object(
                                    Bucket=self.bucket_name,
                                    Key=obj['Key']
                                )
                                deleted_count += 1
                                
                        except (ValueError, IndexError):
                            continue  # Skip malformed keys
            
            logger.info(f"Cleaned up {deleted_count} old prediction files")
            return deleted_count
            
        except ClientError as e:
            logger.error(f"Failed to cleanup old predictions: {e}")
            return 0