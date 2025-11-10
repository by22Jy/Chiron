package com.example.aiorchestrator.controller;

import com.example.aiorchestrator.dto.EventRequest;
import com.example.aiorchestrator.service.EventService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api")
public class EventController {

    private final EventService eventService;

    public EventController(EventService eventService) {
        this.eventService = eventService;
    }

    @PostMapping("/event")
    public ResponseEntity<Map<String, Object>> handleEvent(@RequestBody EventRequest request) {
        Map<String, Object> resp = eventService.handleEvent(request);
        return ResponseEntity.ok(resp);
    }
}


