package com.example.aiorchestrator.controller;

import com.example.aiorchestrator.dto.LogRequest;
import com.example.aiorchestrator.service.LogService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/audit")
public class AuditController {

    private final LogService logService;

    public AuditController(LogService logService) {
        this.logService = logService;
    }

    @PostMapping("/log")
    public ResponseEntity<Map<String, Object>> recordLog(@RequestBody LogRequest request) {
        Long logId = logService.recordLog(request);
        Map<String, Object> resp = new HashMap<>();
        resp.put("status", "ok");
        resp.put("logId", logId);
        return ResponseEntity.ok(resp);
    }
}


