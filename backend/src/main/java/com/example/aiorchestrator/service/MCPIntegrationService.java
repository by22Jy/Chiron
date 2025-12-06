package com.example.aiorchestrator.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * MCP工具集成服务
 * 负责调用Python MCP服务器执行各种工具任务
 */
@Service
public class MCPIntegrationService {

    private static final Logger logger = LoggerFactory.getLogger(MCPIntegrationService.class);
    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${mcp.server.url:http://localhost:8081}")
    private String mcpServerUrl;

    /**
     * 调用MCP工具
     */
    public Map<String, Object> callMCPTool(String toolName, Map<String, Object> params) {
        try {
            logger.info("调用MCP工具: {}, 参数: {}", toolName, params);

            String url = mcpServerUrl + "/mcp/" + toolName;

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, Object>> request = new HttpEntity<>(params, headers);

            ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);

            logger.info("MCP工具响应: {}", response.getBody());

            return response.getBody();

        } catch (Exception e) {
            logger.error("调用MCP工具失败: " + toolName, e);

            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("message", "MCP工具调用失败");

            return errorResponse;
        }
    }

    /**
     * 执行完整工作流
     */
    public Map<String, Object> executeWorkflow(String workflowName, Map<String, Object> context) {
        try {
            logger.info("执行工作流: {}, 上下文: {}", workflowName, context);

            Map<String, Object> params = new HashMap<>();
            params.put("workflow_name", workflowName);
            params.put("context", context);

            String url = mcpServerUrl + "/workflow/execute";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, Object>> request = new HttpEntity<>(params, headers);

            ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);

            logger.info("工作流执行结果: {}", response.getBody());

            return response.getBody();

        } catch (Exception e) {
            logger.error("执行工作流失败: " + workflowName, e);

            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("message", "工作流执行失败");

            return errorResponse;
        }
    }

    /**
     * 获取MCP服务状态
     */
    public Map<String, Object> getMCPStatus() {
        try {
            String url = mcpServerUrl + "/health";

            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);

            return response.getBody();

        } catch (Exception e) {
            logger.error("获取MCP状态失败", e);

            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "unhealthy");
            errorResponse.put("error", e.getMessage());

            return errorResponse;
        }
    }

    /**
     * 获取可用MCP工具列表
     */
    public Map<String, Object> getAvailableTools() {
        try {
            String url = mcpServerUrl + "/tools";

            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);

            return response.getBody();

        } catch (Exception e) {
            logger.error("获取MCP工具列表失败", e);

            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("tools", List.of());

            return errorResponse;
        }
    }

    // 便捷方法

    /**
     * 发送邮件
     */
    public Map<String, Object> sendEmail(String to, String subject, String content) {
        Map<String, Object> params = new HashMap<>();
        params.put("to", to);
        params.put("subject", subject);
        params.put("content", content);

        return callMCPTool("email", params);
    }

    /**
     * 获取天气信息
     */
    public Map<String, Object> getWeather(String city) {
        Map<String, Object> params = new HashMap<>();
        params.put("city", city);

        return callMCPTool("weather", params);
    }

    /**
     * 获取新闻
     */
    public Map<String, Object> getNews(int count) {
        Map<String, Object> params = new HashMap<>();
        params.put("count", count);

        return callMCPTool("news", params);
    }

    /**
     * 截图
     */
    public Map<String, Object> takeScreenshot() {
        return callMCPTool("screenshot", new HashMap<>());
    }

    /**
     * 文件操作
     */
    public Map<String, Object> fileOperation(String operation, String path, String content) {
        Map<String, Object> params = new HashMap<>();
        params.put("operation", operation);
        params.put("path", path);
        params.put("content", content);

        return callMCPTool("filesystem", params);
    }

    /**
     * 浏览器自动化
     */
    public Map<String, Object> browserAutomation(String action, Map<String, Object> params) {
        params.put("action", action);

        return callMCPTool("browser", params);
    }
}