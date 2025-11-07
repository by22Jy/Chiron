package com.example.aiorchestrator.controller;

import com.example.aiorchestrator.dto.ConfigResponseDto;
import com.example.aiorchestrator.service.ConfigService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class ConfigController {

    private final ConfigService configService;

    public ConfigController(ConfigService configService) {
        this.configService = configService;
    }

    @GetMapping("/config")
    public ResponseEntity<ConfigResponseDto> getConfig(@RequestParam(required = false) String username,
                                                       @RequestParam(required = false) String application,
                                                       @RequestParam(required = false, name = "os") String osType) {
        ConfigResponseDto response = configService.fetchConfig(username, application, osType);
        return ResponseEntity.ok(response);
    }
}


