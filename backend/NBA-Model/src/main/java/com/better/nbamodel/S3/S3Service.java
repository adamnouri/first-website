package com.better.nbamodel.S3;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.awscore.exception.AwsServiceException;
import software.amazon.awssdk.core.exception.SdkClientException;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.*;
import software.amazon.awssdk.services.s3.presigner.model.GetObjectPresignRequest;

import java.io.IOException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Map;

@Service
public class S3Service {

    private final S3Client s3;
    private final ObjectMapper objectMapper;
    
    @Value("${aws.s3.bucket-name}")
    private String bucketName;
    
    @Value("${aws.s3.predictions-folder}")
    private String predictionsFolder;
    
    @Value("${aws.s3.analytics-folder}")
    private String analyticsFolder;
    
    @Value("${aws.s3.backups-folder}")
    private String backupsFolder;

    public S3Service(S3Client s3, ObjectMapper objectMapper) {
        this.s3 = s3;
        this.objectMapper = objectMapper;
    }


    public void putObject(String bucketName, String key, byte[] file) {
        PutObjectRequest objectRequest = PutObjectRequest.builder()
                .bucket(bucketName)
                .key(key)
                .build();
        s3.putObject(objectRequest, RequestBody.fromBytes(file));
    }
    public byte[] getObject(String bucketName, String key) throws IOException {
        GetObjectRequest getObjectRequest = GetObjectRequest.builder()
                .bucket(bucketName)
                .key(key)
                .build();
        return s3.getObject(getObjectRequest).readAllBytes();
    }
    public void deleteObject(String bucketName, String key) {
        try {
            s3.deleteObject(builder -> builder.bucket(bucketName).key(key));
        } catch (AwsServiceException | SdkClientException e) {
            throw new RuntimeException(e);
        }
    }
    public boolean doesObjectExist(String bucketName, String key) {
        try {
            s3.headObject(builder -> builder.bucket(bucketName).key(key));
            return true;
        } catch (Exception e) {
            return false;
        }
    }
    
    public String generatePredictionPath(String predictionUuid, LocalDate gameDate) {
        DateTimeFormatter dateFormatter = DateTimeFormatter.ofPattern("yyyy/MM/dd");
        String datePath = gameDate.format(dateFormatter);
        return predictionsFolder + datePath + "/" + predictionUuid + ".json";
    }
    
    public String generateChartPath(String predictionUuid, LocalDate gameDate) {
        DateTimeFormatter dateFormatter = DateTimeFormatter.ofPattern("yyyy/MM/dd");
        String datePath = gameDate.format(dateFormatter);
        return predictionsFolder + datePath + "/" + predictionUuid + "_chart.png";
    }
    
    public void storePredictionData(String predictionUuid, LocalDate gameDate, Map<String, Object> predictionData) 
            throws JsonProcessingException {
        String s3Key = generatePredictionPath(predictionUuid, gameDate);
        String jsonData = objectMapper.writeValueAsString(predictionData);
        
        PutObjectRequest request = PutObjectRequest.builder()
                .bucket(bucketName)
                .key(s3Key)
                .contentType("application/json")
                .build();
                
        s3.putObject(request, RequestBody.fromString(jsonData));
    }
    
    public void storeChartImage(String predictionUuid, LocalDate gameDate, byte[] chartImageData) {
        String s3Key = generateChartPath(predictionUuid, gameDate);
        
        PutObjectRequest request = PutObjectRequest.builder()
                .bucket(bucketName)
                .key(s3Key)
                .contentType("image/png")
                .build();
                
        s3.putObject(request, RequestBody.fromBytes(chartImageData));
    }
    
    public Map<String, Object> getPredictionData(String s3Key) throws IOException {
        try {
            GetObjectRequest request = GetObjectRequest.builder()
                    .bucket(bucketName)
                    .key(s3Key)
                    .build();
                    
            byte[] data = s3.getObject(request).readAllBytes();
            return objectMapper.readValue(data, Map.class);
        } catch (AwsServiceException | SdkClientException e) {
            throw new IOException("Failed to retrieve prediction data from S3: " + e.getMessage(), e);
        }
    }
    
    public byte[] getChartImage(String s3Key) throws IOException {
        try {
            GetObjectRequest request = GetObjectRequest.builder()
                    .bucket(bucketName)
                    .key(s3Key)
                    .build();
                    
            return s3.getObject(request).readAllBytes();
        } catch (AwsServiceException | SdkClientException e) {
            throw new IOException("Failed to retrieve chart image from S3: " + e.getMessage(), e);
        }
    }
    
    public String generateSignedUrl(String s3Key, int durationMinutes) {
        try {
            GetObjectRequest getObjectRequest = GetObjectRequest.builder()
                    .bucket(bucketName)
                    .key(s3Key)
                    .build();
                    
            GetObjectPresignRequest presignRequest = GetObjectPresignRequest.builder()
                    .signatureDuration(java.time.Duration.ofMinutes(durationMinutes))
                    .getObjectRequest(getObjectRequest)
                    .build();
                    
            return s3.utilities().getUrl(GetUrlRequest.builder()
                    .bucket(bucketName)
                    .key(s3Key)
                    .build()).toString();
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate signed URL: " + e.getMessage(), e);
        }
    }
    
    public void storeDailySummary(LocalDate date, Map<String, Object> summaryData) throws JsonProcessingException {
        DateTimeFormatter dateFormatter = DateTimeFormatter.ofPattern("yyyyMMdd");
        String dateStr = date.format(dateFormatter);
        String s3Key = analyticsFolder + "daily_summary_" + dateStr + ".json";
        String jsonData = objectMapper.writeValueAsString(summaryData);
        
        PutObjectRequest request = PutObjectRequest.builder()
                .bucket(bucketName)
                .key(s3Key)
                .contentType("application/json")
                .build();
                
        s3.putObject(request, RequestBody.fromString(jsonData));
    }
    
    public boolean doesPredictionExist(String predictionUuid, LocalDate gameDate) {
        String s3Key = generatePredictionPath(predictionUuid, gameDate);
        return doesObjectExist(bucketName, s3Key);
    }
    
    public boolean doesChartExist(String predictionUuid, LocalDate gameDate) {
        String s3Key = generateChartPath(predictionUuid, gameDate);
        return doesObjectExist(bucketName, s3Key);
    }


}


