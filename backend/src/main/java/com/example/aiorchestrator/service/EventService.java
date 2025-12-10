package com.example.aiorchestrator.service;

import com.example.aiorchestrator.dto.EventRequest;
import com.example.aiorchestrator.dto.LogRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.HashMap;
import java.util.Map;

@Service
public class EventService {

    private static final Logger logger = LoggerFactory.getLogger(EventService.class);

    private final LogService logService;

    public EventService(LogService logService) {
        this.logService = logService;
    }

    public Map<String, Object> handleEvent(EventRequest request) {
        try {
            logger.info("处理事件请求: eventType={}, username={}, application={}",
                       request.getEventType(), request.getUsername(), request.getApplication());

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
            logger.info("事件记录成功，logId={}", logId);

            Map<String, Object> resp = new HashMap<>();
            resp.put("status", "accepted");
            resp.put("logId", logId);
            resp.put("nextStep", nextStepHint(request.getEventType()));
            return resp;

        } catch (Exception e) {
            logger.error("处理事件时发生错误: {}", e.getMessage(), e);

            Map<String, Object> resp = new HashMap<>();
            resp.put("status", "error");
            resp.put("error", e.getMessage());
            resp.put("logId", null);
            resp.put("nextStep", "处理失败，请检查日志");
            return resp;
        }
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


