package com.example.aiorchestrator.service;

import com.example.aiorchestrator.dto.EventRequest;
import com.example.aiorchestrator.dto.LogRequest;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.HashMap;
import java.util.Map;

@Service
public class EventService {

    private final LogService logService;

    public EventService(LogService logService) {
        this.logService = logService;
    }

    public Map<String, Object> handleEvent(EventRequest request) {
        // 目前先写入日志，后续可扩展 LLM / 外部 API
        LogRequest logRequest = new LogRequest();
        logRequest.setUsername(request.getUsername());
        logRequest.setApplication(request.getApplication());
        logRequest.setGestureCode(request.getEventType());
        logRequest.setActionType("event");
        logRequest.setActionValue(request.getPayload());
        logRequest.setStatus("received");
        logRequest.setMessage("Event received by platform");
        logRequest.setSourceAgent("event-api");
        Long logId = logService.recordLog(logRequest);

        Map<String, Object> resp = new HashMap<>();
        resp.put("status", "accepted");
        resp.put("logId", logId);
        resp.put("nextStep", nextStepHint(request.getEventType()));
        return resp;
    }

    private String nextStepHint(String eventType) {
        if (!StringUtils.hasText(eventType)) {
            return "No event type specified";
        }
        return switch (eventType.toLowerCase()) {
            case "thumbs_up" -> "后续可调用 LLM 进行意图分析";
            case "thumbs_down" -> "可触发警告或取消操作";
            default -> "等待进一步编排逻辑实现";
        };
    }
}


