package com.example.aiorchestrator.controller;

import com.example.aiorchestrator.domain.ExecutionResult;
import com.example.aiorchestrator.domain.Workflow;
import com.example.aiorchestrator.service.AgentCommunicationService;
import com.example.aiorchestrator.service.LlmService;
import com.example.aiorchestrator.service.WorkflowEngine;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 工作流控制器
 */
@RestController
@RequestMapping("/api/workflow")
@CrossOrigin(origins = {"http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"}, allowCredentials = "true")
public class WorkflowController {

    private static final Logger logger = LoggerFactory.getLogger(WorkflowController.class);

    @Autowired
    private LlmService llmService;

    @Autowired
    private WorkflowEngine workflowEngine;

    @Autowired
    private AgentCommunicationService agentCommunicationService;

    /**
     * 规划工作流
     */
    @PostMapping("/plan")
    public ResponseEntity<Map<String, Object>> planWorkflow(@RequestBody Map<String, Object> request) {
        logger.info("收到工作流规划请求: {}", request);

        try {
            String userInput = (String) request.get("user_input");
            Map<String, Object> context = (Map<String, Object>) request.getOrDefault("context", new HashMap<>());
            List<String> detectedObjects = (List<String>) request.getOrDefault("detected_objects", new java.util.ArrayList<>());

            if (userInput == null || userInput.trim().isEmpty()) {
                return createErrorResponse("用户输入不能为空");
            }

            // 规划工作流
            Workflow workflow = llmService.planWorkflow(userInput, context, detectedObjects);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("workflow", workflow);
            response.put("available_tools", llmService.getAvailableTools());
            response.put("timestamp", System.currentTimeMillis());

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            logger.error("工作流规划失败", e);
            return createErrorResponse("工作流规划失败: " + e.getMessage());
        }
    }

    /**
     * 执行工作流
     */
    @PostMapping("/execute")
    public ResponseEntity<Map<String, Object>> executeWorkflow(@RequestBody Map<String, Object> request) {
        logger.info("收到工作流执行请求: {}", request);

        try {
            Workflow workflow = convertToWorkflow(request.get("workflow"));
            Map<String, Object> context = (Map<String, Object>) request.getOrDefault("context", new HashMap<>());

            if (workflow == null) {
                return createErrorResponse("工作流数据不能为空");
            }

            // 检查Agent是否在线
            if (!agentCommunicationService.isAgentOnline()) {
                return createErrorResponse("Agent未在线，请先启动Agent服务");
            }

            // 执行工作流
            ExecutionResult result = workflowEngine.executeWorkflow(workflow, context);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("result", result);
            response.put("timestamp", System.currentTimeMillis());

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            logger.error("工作流执行失败", e);
            return createErrorResponse("工作流执行失败: " + e.getMessage());
        }
    }

    /**
     * 一键规划并执行工作流
     */
    @PostMapping("/smart-execute")
    public ResponseEntity<Map<String, Object>> smartExecute(@RequestBody Map<String, Object> request) {
        logger.info("收到智能执行请求: {}", request);

        try {
            String userInput = (String) request.get("user_input");
            Map<String, Object> context = (Map<String, Object>) request.getOrDefault("context", new HashMap<>());
            List<String> detectedObjects = (List<String>) request.getOrDefault("detected_objects", new java.util.ArrayList<>());

            if (userInput == null || userInput.trim().isEmpty()) {
                return createErrorResponse("用户输入不能为空");
            }

            // 检查Agent是否在线
            if (!agentCommunicationService.isAgentOnline()) {
                return createErrorResponse("Agent未在线，请先启动Agent服务");
            }

            // 1. 规划工作流
            Workflow workflow = llmService.planWorkflow(userInput, context, detectedObjects);

            // 2. 执行工作流
            ExecutionResult result = workflowEngine.executeWorkflow(workflow, context);

            Map<String, Object> response = new HashMap<>();
            response.put("success", result.getSuccess());
            response.put("workflow", workflow);
            response.put("result", result);
            response.put("timestamp", System.currentTimeMillis());

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            logger.error("智能执行失败", e);
            return createErrorResponse("智能执行失败: " + e.getMessage());
        }
    }

    /**
     * 获取可用工具列表
     */
    @GetMapping("/tools")
    public ResponseEntity<Map<String, Object>> getAvailableTools() {
        logger.info("获取可用工具列表");

        try {
            Map<String, String> availableTools = llmService.getAvailableTools();

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("tools", availableTools);
            response.put("agent_online", agentCommunicationService.isAgentOnline());
            response.put("timestamp", System.currentTimeMillis());

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            logger.error("获取工具列表失败", e);
            return createErrorResponse("获取工具列表失败: " + e.getMessage());
        }
    }

    /**
     * 获取Agent状态
     */
    @GetMapping("/agent-status")
    public ResponseEntity<Map<String, Object>> getAgentStatus() {
        logger.info("获取Agent状态");

        try {
            Map<String, Object> agentStatus = agentCommunicationService.getAgentStatus();

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("agent_status", agentStatus);
            response.put("timestamp", System.currentTimeMillis());

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            logger.error("获取Agent状态失败", e);
            return createErrorResponse("获取Agent状态失败: " + e.getMessage());
        }
    }

    /**
     * 停止Agent
     */
    @PostMapping("/agent-stop")
    public ResponseEntity<Map<String, Object>> stopAgent() {
        logger.info("停止Agent");

        try {
            Map<String, Object> result = agentCommunicationService.stopAgent();

            Map<String, Object> response = new HashMap<>();
            response.put("success", result.getOrDefault("success", false));
            response.put("result", result);
            response.put("timestamp", System.currentTimeMillis());

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            logger.error("停止Agent失败", e);
            return createErrorResponse("停止Agent失败: " + e.getMessage());
        }
    }

    /**
     * 转换为Workflow对象
     */
    private Workflow convertToWorkflow(Object workflowData) {
        // 这里需要根据实际的workflow数据格式进行转换
        // 暂时返回null，需要实现具体的转换逻辑
        return null;
    }

    /**
     * 创建错误响应
     */
    private ResponseEntity<Map<String, Object>> createErrorResponse(String errorMessage) {
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("success", false);
        errorResponse.put("error", errorMessage);
        errorResponse.put("timestamp", System.currentTimeMillis());

        return ResponseEntity.status(500).body(errorResponse);
    }
}