package com.better.nbamodel.config;

import io.github.cdimascio.dotenv.Dotenv;
import io.github.cdimascio.dotenv.DotenvException;
import org.springframework.context.ApplicationContextInitializer;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.core.env.ConfigurableEnvironment;
import org.springframework.core.env.MapPropertySource;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

public class DotenvConfig implements ApplicationContextInitializer<ConfigurableApplicationContext> {

    @Override
    public void initialize(ConfigurableApplicationContext applicationContext) {
        ConfigurableEnvironment environment = applicationContext.getEnvironment();
        
        // Try to load .env from project root first (for local development)
        Dotenv dotenv = null;
        try {
            // Check if .env exists in project root (../../.env from Spring Boot working directory)
            File projectRootEnv = new File("../../.env");
            if (projectRootEnv.exists()) {
                dotenv = Dotenv.configure()
                    .directory("../../")
                    .filename(".env")
                    .ignoreIfMissing()
                    .load();
            }
        } catch (DotenvException e) {
            // Try local .env file
            try {
                dotenv = Dotenv.configure()
                    .directory(".")
                    .filename(".env")
                    .ignoreIfMissing()
                    .load();
            } catch (DotenvException ignored) {
                // No .env file found, will use system environment variables
            }
        }
        
        // Add dotenv variables to Spring environment
        if (dotenv != null) {
            Map<String, Object> envVars = new HashMap<>();
            dotenv.entries().forEach(entry -> envVars.put(entry.getKey(), entry.getValue()));
            environment.getPropertySources().addFirst(new MapPropertySource("dotenv", envVars));
        }
    }
}