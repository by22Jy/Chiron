package com.example.aiorchestrator.controller;

import com.example.aiorchestrator.service.AiOrchestratorService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/ai")
public class AiController {

    private final AiOrchestratorService aiService;

    public AiController(AiOrchestratorService aiService) { this.aiService = aiService; }

    @PostMapping(value = "/ask-sync", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<String> askSync(@RequestParam("image") MultipartFile image,
                                          @RequestParam("question") String question) {
        return ResponseEntity.ok(aiService.orchestrate(image, question));
    }

    @PostMapping("/ask-sync-by-url")
    public ResponseEntity<String> askSyncByUrl(@RequestParam("imageUrl") String imageUrl,
                                               @RequestParam("question") String question) {
        return ResponseEntity.ok(aiService.orchestrateByUrl(imageUrl, question));
    }
}


