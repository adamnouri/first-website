package com.better.nbamodel.config;

import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Primary;
import org.springframework.web.client.RestTemplate;

@TestConfiguration
public class TestConfig {

    @Bean
    @Primary
    public RestTemplate testRestTemplate() {
        return new RestTemplate();
    }
}