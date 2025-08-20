package com.better.nbamodel.S3;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

@Configuration
public class S3Config {

    @Value("${aws.s3.region}")
    private String awsRegion;


    @Bean
    public S3Client s3Client() {

        return S3Client.builder()
                .region(Region.of(awsRegion))
                .build();
    }

//    public S3Bucket putS3Bucket(String bucketName, String key, byte[] file) {
//        PutObjectRequest GetObject = PutObjectRequest.builder()
//                .bucket(bucketName)
//                .key(key)
//                .build();
//    }
}
