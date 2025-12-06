package com.example.aiorchestrator.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * MCP工具集成控制器
 * 提供MCP工具的HTTP接口
 */
@RestController
@RequestMapping("/api/mcp")
@CrossOrigin(origins = {"http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"}, allowCredentials = "true")
public class MCPController {

    private static final Logger logger = LoggerFactory.getLogger(MCPController.class);

    @Autowired
    private com.example.aiorchestrator.service.AiOrchestratorService aiOrchestratorService;

    /**
     * 获取MCP服务状态
     */
    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getMCPStatus() {
        try {
            Map<String, Object> status = aiOrchestratorService.getMCPStatus();

            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("status", status);
            result.put("timestamp", System.currentTimeMillis());

            return ResponseEntity.ok(result);

        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("message", "获取MCP状态失败");

            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 智能MCP增强对话
     */
    @PostMapping("/enhanced-chat")
    public ResponseEntity<Map<String, Object>> enhancedChat(
            @RequestBody Map<String, Object> request) {

        try {
            String message = (String) request.get("message");
            String context = (String) request.get("context");
            @SuppressWarnings("unchecked")
            List<String> requiredTools = (List<String>) request.get("required_tools");

            logger.info("收到MCP增强聊天请求: {}, 工具: {}", message, requiredTools);

            // 构建完整的提示词
            String prompt = buildEnhancedChatPrompt(message, context);

            // 调用MCP增强的LLM服务
            String llmResponse = aiOrchestratorService.orchestrateWithMCP(prompt, requiredTools);

            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("response", llmResponse);
            result.put("message", message);
            result.put("tools_used", requiredTools);
            result.put("timestamp", System.currentTimeMillis());

            logger.info("MCP增强聊天响应成功");
            return ResponseEntity.ok(result);

        } catch (Exception e) {
            logger.error("MCP增强聊天处理失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("response", "MCP增强对话暂时不可用");

            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 执行复杂工作流
     */
    @PostMapping("/execute-workflow")
    public ResponseEntity<Map<String, Object>> executeWorkflow(
            @RequestBody Map<String, Object> request) {

        try {
            String workflowName = (String) request.get("workflow_name");
            @SuppressWarnings("unchecked")
            Map<String, Object> context = (Map<String, Object>) request.get("context");

            logger.info("执行工作流: {}", workflowName);

            String result = aiOrchestratorService.executeComplexWorkflow(workflowName, context);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("response", result);
            response.put("workflow_name", workflowName);
            response.put("timestamp", System.currentTimeMillis());

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            logger.error("工作流执行失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("response", "工作流执行失败");

            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 快速新闻邮件工作流
     */
    @PostMapping("/news-email-workflow")
    public ResponseEntity<Map<String, Object>> newsEmailWorkflow(
            @RequestBody Map<String, Object> request) {

        try {
            String email = (String) request.getOrDefault("email", "1730495747@qq.com");
            String city = (String) request.getOrDefault("city", "北京");

            logger.info("执行新闻邮件工作流: 邮箱={}, 城市={}", email, city);

            Map<String, Object> context = new HashMap<>();
            context.put("email", email);
            context.put("city", city);

            String result = aiOrchestratorService.executeComplexWorkflow("news_weather_email", context);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("response", result);
            response.put("email", email);
            response.put("city", city);
            response.put("workflow_type", "news_weather_email");
            response.put("timestamp", System.currentTimeMillis());

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            logger.error("新闻邮件工作流失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("response", "新闻邮件工作流执行失败");

            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 天气查询
     */
    @PostMapping("/weather")
    public ResponseEntity<Map<String, Object>> getWeather(
            @RequestBody Map<String, Object> request) {

        try {
            String city = (String) request.getOrDefault("city", "北京");

            logger.info("查询天气: {}", city);

            Map<String, Object> context = new HashMap<>();
            context.put("city", city);

            String result = aiOrchestratorService.executeComplexWorkflow("get_weather", context);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("response", result);
            response.put("city", city);
            response.put("timestamp", System.currentTimeMillis());

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            logger.error("天气查询失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("response", "天气查询失败");

            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 发送邮件
     */
    @PostMapping("/send-email")
    public ResponseEntity<Map<String, Object>> sendEmail(
            @RequestBody Map<String, Object> request) {

        try {
            String to = (String) request.get("to");
            String subject = (String) request.get("subject");
            String content = (String) request.get("content");

            logger.info("发送邮件: to={}, subject={}", to, subject);

            Map<String, Object> context = new HashMap<>();
            context.put("to", to);
            context.put("subject", subject);
            context.put("content", content);

            String result = aiOrchestratorService.executeComplexWorkflow("send_email", context);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("response", result);
            response.put("to", to);
            response.put("subject", subject);
            response.put("timestamp", System.currentTimeMillis());

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            logger.error("发送邮件失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("response", "邮件发送失败");

            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 构建增强对话提示词
     */
    private String buildEnhancedChatPrompt(String message, String context) {
        StringBuilder promptBuilder = new StringBuilder();

        promptBuilder.append("你是YOLO-LLM平台的智能助手，具备多种工具调用能力。\n\n");

        if (context != null && !context.trim().isEmpty()) {
            promptBuilder.append("上下文: ").append(context).append("\n\n");
        }

        promptBuilder.append("用户请求: ").append(message).append("\n\n");

        promptBuilder.append("请分析用户请求，如果需要调用工具（如发送邮件、查询天气、获取新闻等），");
        promptBuilder.append("请使用相应的工具完成任务，然后提供综合性的回答。\n");

        promptBuilder.append("如果不需要调用工具，请直接回答用户问题。");

        return promptBuilder.toString();
    }
}