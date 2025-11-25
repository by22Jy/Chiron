package com.example.aiorchestrator.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * GLM 官方 SDK 控制器
 * 提供基于官方 SDK 的增强型 LLM 服务
 */
@RestController
@RequestMapping("/api/glm-sdk")
@CrossOrigin(origins = {"http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"}, allowCredentials = "true")
public class GlmSdkController {

    private static final Logger logger = LoggerFactory.getLogger(GlmSdkController.class);

    @Autowired
    private com.example.aiorchestrator.service.GlmSdkService glmSdkService;

    /**
     * 基础对话
     */
    @PostMapping("/chat")
    public ResponseEntity<Map<String, Object>> chat(@RequestBody Map<String, Object> request) {
        logger.info("收到GLM SDK聊天请求: {}", request);

        String message = (String) request.get("message");

        logger.info("提取消息参数: {}", message);

        try {
            // 调用GLM SDK服务
            String llmResponse = glmSdkService.chat(message);
            logger.info("GLM SDK响应: {}", llmResponse);

            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("response", llmResponse);
            result.put("timestamp", System.currentTimeMillis());
            result.put("provider", "glm-sdk");

            logger.info("GLM SDK成功响应: {}", result);
            return ResponseEntity.ok(result);

        } catch (Exception e) {
            logger.error("GLM SDK聊天处理失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("response", "GLM SDK智能对话暂时不可用");

            logger.info("GLM SDK错误响应: {}", errorResponse);
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 手势意图分析
     */
    @PostMapping("/gesture-analysis")
    public ResponseEntity<Map<String, Object>> analyzeGesture(@RequestBody Map<String, Object> request) {
        logger.info("收到GLM SDK手势分析请求: {}", request);

        String prompt = (String) request.get("prompt");
        String gestureCode = (String) request.get("gesture_code");
        Object confidenceObj = request.get("confidence");
        Double confidence = confidenceObj instanceof Number ? ((Number) confidenceObj).doubleValue() : null;
        String context = (String) request.get("context");

        try {
            // 使用GLM SDK进行手势分析
            String llmResponse = glmSdkService.analyzeGesture(gestureCode, confidence, context, prompt);
            logger.info("GLM SDK手势分析响应: {}", llmResponse);

            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("response", llmResponse);
            result.put("gesture_code", gestureCode);
            result.put("timestamp", System.currentTimeMillis());
            result.put("provider", "glm-sdk");

            return ResponseEntity.ok(result);

        } catch (Exception e) {
            logger.error("GLM SDK手势分析失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("response", "GLM SDK手势分析暂时不可用");

            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 语音命令分析
     */
    @PostMapping("/voice-command")
    public ResponseEntity<Map<String, Object>> analyzeVoiceCommand(@RequestBody Map<String, Object> request) {
        logger.info("收到GLM SDK语音命令分析请求: {}", request);

        String command = (String) request.get("command");
        String context = (String) request.get("context");

        try {
            // 使用GLM SDK进行语音命令分析
            String llmResponse = glmSdkService.analyzeVoiceCommand(command, context);
            logger.info("GLM SDK语音命令分析响应: {}", llmResponse);

            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("response", llmResponse);
            result.put("command", command);
            result.put("timestamp", System.currentTimeMillis());
            result.put("provider", "glm-sdk");

            return ResponseEntity.ok(result);

        } catch (Exception e) {
            logger.error("GLM SDK语音命令分析失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("response", "GLM SDK语音命令分析暂时不可用");

            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 智能对话助手
     */
    @PostMapping("/intelligent-chat")
    public ResponseEntity<Map<String, Object>> intelligentChat(@RequestBody Map<String, Object> request) {
        logger.info("收到GLM SDK智能对话请求: {}", request);

        String message = (String) request.get("message");
        String context = (String) request.get("context");
        String conversationHistory = (String) request.get("history");

        logger.info("提取智能对话参数 - Message: {}, Context: {}, History: {}", message, context, conversationHistory);

        try {
            // 使用GLM SDK进行智能对话
            String llmResponse = glmSdkService.intelligentChat(message, context, conversationHistory);
            logger.info("GLM SDK智能对话响应: {}", llmResponse);

            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("response", llmResponse);
            result.put("timestamp", System.currentTimeMillis());
            result.put("provider", "glm-sdk");

            logger.info("GLM SDK智能对话成功响应: {}", result);
            return ResponseEntity.ok(result);

        } catch (Exception e) {
            logger.error("GLM SDK智能对话处理失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("response", "GLM SDK智能对话暂时不可用");

            logger.info("GLM SDK智能对话错误响应: {}", errorResponse);
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 多轮对话
     */
    @PostMapping("/chat-with-history")
    public ResponseEntity<Map<String, Object>> chatWithHistory(@RequestBody Map<String, Object> request) {
        logger.info("收到GLM SDK多轮对话请求: {}", request);

        String message = (String) request.get("message");
        @SuppressWarnings("unchecked")
        java.util.List<Map<String, String>> conversationHistory = (java.util.List<Map<String, String>>) request.get("history");

        logger.info("提取多轮对话参数 - Message: {}, History length: {}", message, conversationHistory != null ? conversationHistory.size() : 0);

        try {
            // 使用GLM SDK进行多轮对话
            String llmResponse = glmSdkService.chatWithHistory(message, conversationHistory);
            logger.info("GLM SDK多轮对话响应: {}", llmResponse);

            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("response", llmResponse);
            result.put("timestamp", System.currentTimeMillis());
            result.put("provider", "glm-sdk");

            logger.info("GLM SDK多轮对话成功响应: {}", result);
            return ResponseEntity.ok(result);

        } catch (Exception e) {
            logger.error("GLM SDK多轮对话处理失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("response", "GLM SDK多轮对话暂时不可用");

            logger.info("GLM SDK多轮对话错误响应: {}", errorResponse);
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 健康检查
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> result = new HashMap<>();
        result.put("status", "healthy");
        result.put("service", "GLM SDK Controller");
        result.put("timestamp", System.currentTimeMillis());
        result.put("version", "1.0.0");

        return ResponseEntity.ok(result);
    }
}