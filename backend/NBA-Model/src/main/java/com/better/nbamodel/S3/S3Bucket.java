package com.better.nbamodel.S3;

import com.better.nbamodel.NBAModel;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "aws.s3.bucket")
public class S3Bucket {
    private NBAModel NBAModel;
    @Value("${aws.s3.model-key}")
    private String modelKey;
    @Value("${aws.s3.bucket-name}")
    private String bucketName;


    public void setBucketName(String bucketName) {
        this.bucketName = bucketName;
    }



    public String getModelKey() {
        return modelKey;
    }

    public void setModelKey(String modelKey) {
        this.modelKey = modelKey;
    }



    public String getBucketName() {
        return bucketName;
    }

    public NBAModel getNBAModel() {
        return NBAModel;
    }

    public void setNBAModel(NBAModel NBAModel) {
        this.NBAModel = NBAModel;
    }


}
