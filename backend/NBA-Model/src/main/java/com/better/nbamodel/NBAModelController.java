package com.better.nbamodel;

import com.better.nbamodel.service.NBAModelService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/nbamodel")
public class NBAModelController {

    @Autowired
    private NBAModelService nbaModelService;

    @GetMapping
    public ResponseEntity<String> getNBAModel(){
        return ResponseEntity.ok("NBA Model API is running");
    }
    
    @GetMapping("/predict/{gameId}")
    public ResponseEntity<Map<String, Object>> predictGame(@PathVariable Long gameId) {
        Map<String, Object> prediction = nbaModelService.predictGame(gameId);
        if (prediction == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(prediction);
    }
}
