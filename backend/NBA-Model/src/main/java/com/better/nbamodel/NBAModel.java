package com.better.nbamodel;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@Entity
public class NBAModel {
    @Id
    private Long id;

    public void setId(Long id) {
        this.id = id;
    }

    public Long getId() {
        return id;
    }

}
