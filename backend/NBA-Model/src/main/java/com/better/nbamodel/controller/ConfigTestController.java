package com.better.nbamodel.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/config")
public class ConfigTestController {
    
    @Value("${aws.s3.bucket-name:NOT_SET}")
    private String bucketName;
    
    @Value("${aws.s3.region:NOT_SET}")
    private String region;
    
    @Value("${AWS_ACCESS_KEY_ID:NOT_SET}")
    private String accessKeyId;
    
    @Value("${AWS_SECRET_ACCESS_KEY:NOT_SET}")
    private String secretAccessKey;
    
    @GetMapping("/test")
    public Map<String, Object> testConfiguration() {
        Map<String, Object> config = new HashMap<>();
        config.put("bucketName", bucketName);
        config.put("region", region);
        config.put("accessKeyId", accessKeyId.substring(0, Math.min(8, accessKeyId.length())) + "...");
        config.put("secretKeyMasked", secretAccessKey.equals("NOT_SET") ? "NOT_SET" : secretAccessKey.substring(0, 8) + "...");
        config.put("envLoaded", !accessKeyId.equals("NOT_SET"));
        
        // Check system environment as fallback
        String sysAccessKey = System.getenv("AWS_ACCESS_KEY_ID");
        config.put("systemEnvAccessKey", sysAccessKey != null ? sysAccessKey.substring(0, Math.min(8, sysAccessKey.length())) + "..." : "NOT_SET");
        
        return config;
    }
}