package com.better.nbamodel;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class NbaModelApplication {


    public static void main(String[] args) {
        SpringApplication.run(NbaModelApplication.class, args);
    }

}

