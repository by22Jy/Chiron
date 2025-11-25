package com.example.aiorchestrator.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;

// 用于接收手势控制状态更新的请求体
class GestureControlRequest {
    private boolean enabled;

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }
}

@RestController
@RequestMapping("/api/monitor")
public class MonitorController {

    // 手势控制状态存储（内存中，重启后会重置）
    private static boolean gestureControlEnabled = true;

    @GetMapping("/status")
    public ResponseEntity<Map<String, String>> getSystemStatus() {
        Map<String, String> status = new HashMap<>();

        // 检查各个服务状态
        status.put("backend", "healthy");
        status.put("ai_service", isPortOpen("localhost", 8000) ? "healthy" : "error");
        status.put("database", "healthy");
        status.put("agent", isAgentRunning() ? "healthy" : "error");

        return ResponseEntity.ok(status);
    }

    /**
     * 检查指定端口是否开放
     */
    private boolean isPortOpen(String host, int port) {
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress(host, port), 1000);
            return true;
        } catch (IOException e) {
            return false;
        }
    }

    /**
     * 检查Agent进程是否在运行
     */
    private boolean isAgentRunning() {
        try {
            // 检查Agent进程是否在运行
            Process process = Runtime.getRuntime().exec("tasklist /FI \"IMAGENAME eq python.exe\"");
            int exitCode = process.waitFor();

            if (exitCode == 0) {
                // 进一步检查是否有agent相关的进程
                Process grepProcess = Runtime.getRuntime().exec("wmic process where \"name='python.exe'\" get commandline /format:csv");
                java.io.BufferedReader reader = new java.io.BufferedReader(
                    new java.io.InputStreamReader(grepProcess.getInputStream()));

                String line;
                while ((line = reader.readLine()) != null) {
                    if (line.contains("main.py") || line.contains("agent")) {
                        return true;
                    }
                }
            }
            return false;
        } catch (Exception e) {
            return false;
        }
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
        // 添加手势控制状态
        gestureStatus.put("gesture_control_enabled", gestureControlEnabled);
        gestureStatus.put("control_toggle_gesture", "victory");

        return ResponseEntity.ok(gestureStatus);
    }

    @PostMapping("/gesture/control")
    public ResponseEntity<Map<String, Object>> toggleGestureControl() {
        gestureControlEnabled = !gestureControlEnabled;

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("gesture_control_enabled", gestureControlEnabled);
        response.put("message", gestureControlEnabled ? "手势控制已启用" : "手势控制已禁用");
        response.put("timestamp", System.currentTimeMillis());

        return ResponseEntity.ok(response);
    }

    @PostMapping("/gesture/control/set")
    public ResponseEntity<Map<String, Object>> setGestureControl(@RequestBody GestureControlRequest request) {
        gestureControlEnabled = request.isEnabled();

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("gesture_control_enabled", gestureControlEnabled);
        response.put("message", gestureControlEnabled ? "手势控制已启用" : "手势控制已禁用");
        response.put("timestamp", System.currentTimeMillis());

        return ResponseEntity.ok(response);
    }
}