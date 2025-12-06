package com.example.aiorchestrator.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

/**
 * Agent通信服务 - 负责与Python Agent通信
 */
@Service
public class AgentCommunicationService {

    private static final Logger logger = LoggerFactory.getLogger(AgentCommunicationService.class);

    @Value("${agent.base-url:http://localhost:8081}")
    private String agentBaseUrl;

    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * 发送命令给Agent
     */
    public Map<String, Object> sendCommandToAgent(Map<String, Object> command) {
        logger.info("发送命令给Agent - 命令: {}", command);

        try {
            String url = agentBaseUrl + "/api/execute";
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, Object>> request = new HttpEntity<>(command, headers);
            ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);

            if (response.getStatusCode().is2xxSuccessful()) {
                Map<String, Object> responseBody = response.getBody();
                logger.info("Agent响应成功: {}", responseBody);
                return responseBody != null ? responseBody : new HashMap<>();
            } else {
                logger.error("Agent响应失败 - 状态码: {}", response.getStatusCode());
                return createErrorResponse("Agent通信失败 - 状态码: " + response.getStatusCode());
            }

        } catch (Exception e) {
            logger.error("Agent通信异常", e);
            return createErrorResponse("Agent通信异常: " + e.getMessage());
        }
    }

    /**
     * 发送工作流步骤给Agent执行
     */
    public Map<String, Object> executeWorkflowStep(String workflowId, Integer stepId, String toolName,
                                                   String action, Map<String, Object> parameters) {
        Map<String, Object> command = new HashMap<>();
        command.put("workflow_id", workflowId);
        command.put("step_id", stepId);
        command.put("tool_name", toolName);
        command.put("action", action);
        command.put("parameters", parameters);
        command.put("type", "workflow_step");

        return sendCommandToAgent(command);
    }

    /**
     * 获取Agent状态
     */
    public Map<String, Object> getAgentStatus() {
        logger.info("获取Agent状态");

        try {
            String url = agentBaseUrl + "/api/status";
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);

            if (response.getStatusCode().is2xxSuccessful()) {
                Map<String, Object> responseBody = response.getBody();
                logger.info("Agent状态: {}", responseBody);
                return responseBody != null ? responseBody : new HashMap<>();
            } else {
                logger.error("获取Agent状态失败 - 状态码: {}", response.getStatusCode());
                return createErrorResponse("获取Agent状态失败");
            }

        } catch (Exception e) {
            logger.error("获取Agent状态异常", e);
            return createErrorResponse("获取Agent状态异常: " + e.getMessage());
        }
    }

    /**
     * 停止Agent
     */
    public Map<String, Object> stopAgent() {
        logger.info("停止Agent");

        try {
            String url = agentBaseUrl + "/api/stop";
            ResponseEntity<Map> response = restTemplate.postForEntity(url, null, Map.class);

            if (response.getStatusCode().is2xxSuccessful()) {
                Map<String, Object> responseBody = response.getBody();
                logger.info("Agent停止响应: {}", responseBody);
                return responseBody != null ? responseBody : new HashMap<>();
            } else {
                logger.error("停止Agent失败 - 状态码: {}", response.getStatusCode());
                return createErrorResponse("停止Agent失败");
            }

        } catch (Exception e) {
            logger.error("停止Agent异常", e);
            return createErrorResponse("停止Agent异常: " + e.getMessage());
        }
    }

    /**
     * 发送视觉上下文给Agent
     */
    public Map<String, Object> sendVisualContext(Map<String, Object> visualContext) {
        Map<String, Object> command = new HashMap<>();
        command.put("visual_context", visualContext);
        command.put("type", "context_update");

        return sendCommandToAgent(command);
    }

    /**
     * 创建错误响应
     */
    private Map<String, Object> createErrorResponse(String errorMessage) {
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("success", false);
        errorResponse.put("error", errorMessage);
        errorResponse.put("timestamp", System.currentTimeMillis());
        return errorResponse;
    }

    /**
     * 检查Agent是否在线
     */
    public boolean isAgentOnline() {
        try {
            Map<String, Object> status = getAgentStatus();
            return status.containsKey("success") && (Boolean) status.get("success");
        } catch (Exception e) {
            return false;
        }
    }
}