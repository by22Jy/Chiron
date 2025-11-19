package com.example.aiorchestrator.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/monitor")
public class MonitorController {

    @GetMapping("/status")
    public ResponseEntity<Map<String, String>> getSystemStatus() {
        Map<String, String> status = new HashMap<>();

        // 检查各个服务状态
        status.put("backend", "healthy");
        status.put("ai_service", "healthy");
        status.put("database", "healthy");
        status.put("agent", "unknown"); // Agent状态需要通过其他方式检测

        return ResponseEntity.ok(status);
    }

    @GetMapping("/performance")
    public ResponseEntity<Map<String, Object>> getPerformanceMetrics() {
        Map<String, Object> performance = new HashMap<>();

        // 模拟性能指标
        performance.put("cpu_usage", 25.5);
        performance.put("memory_usage", 45.2);
        performance.put("gpu_usage", 12.8);
        performance.put("network_in", 1024.5);
        performance.put("network_out", 512.3);

        return ResponseEntity.ok(performance);
    }

    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getStatistics() {
        Map<String, Object> statistics = new HashMap<>();

        // 模拟统计数据
        statistics.put("gesture_count", 156);
        statistics.put("success_rate", 94.5);
        statistics.put("avg_response_time", 120.5);
        statistics.put("total_requests", 1250);
        statistics.put("error_count", 12);

        return ResponseEntity.ok(statistics);
    }

    @GetMapping("/gesture")
    public ResponseEntity<Map<String, Object>> getGestureStatus() {
        Map<String, Object> gestureStatus = new HashMap<>();

        // 模拟手势识别状态
        gestureStatus.put("current_gesture", null);
        gestureStatus.put("confidence", 0.0);
        gestureStatus.put("last_update", System.currentTimeMillis());
        gestureStatus.put("is_detecting", false);

        return ResponseEntity.ok(gestureStatus);
    }
}