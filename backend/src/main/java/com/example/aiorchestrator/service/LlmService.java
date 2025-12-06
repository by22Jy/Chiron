package com.example.aiorchestrator.service;

import com.example.aiorchestrator.domain.Workflow;
import com.example.aiorchestrator.domain.WorkflowStep;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;

/**
 * LLM智能分析服务 - 专门用于工作流规划和意图理解
 */
@Service
public class LlmService {

    private static final Logger logger = LoggerFactory.getLogger(LlmService.class);

    @Autowired
    private AiOrchestratorService aiOrchestratorService;

    private final ObjectMapper objectMapper = new ObjectMapper();

    // 可用工具列表
    private final Map<String, String> availableTools = Map.of(
        "system", "系统操作工具：打开应用、窗口管理、文件操作、截图",
        "input", "输入工具：键盘输入、鼠标点击、滚动",
        "file", "文件工具：创建文件、读写文件、保存内容",
        "messaging", "通信工具：发送邮件、微信通知、桌面通知",
        "web", "网络工具：打开网页、搜索、获取网页内容",
        "ai", "AI工具：内容生成、文本总结、智能分析"
    );

    /**
     * 规划工作流 - 核心方法
     */
    public Workflow planWorkflow(String userInput, Map<String, Object> context, List<String> detectedObjects) {
        logger.info("开始规划工作流 - 用户输入: {}", userInput);
        logger.info("上下文: {}", context);
        logger.info("检测到的物体: {}", detectedObjects);

        try {
            // 构建工作流规划提示词
            String prompt = buildWorkflowPlanningPrompt(userInput, context, detectedObjects);

            // 调用LLM生成工作流
            String llmResponse = aiOrchestratorService.orchestrateByUrl("", prompt);
            logger.info("LLM响应: {}", llmResponse);

            // 解析LLM响应为工作流
            Workflow workflow = parseWorkflowResponse(llmResponse, userInput);

            logger.info("工作流规划完成 - 工作流ID: {}, 步骤数: {}", workflow.getWorkflowId(),
                       workflow.getSteps() != null ? workflow.getSteps().size() : 0);

            return workflow;

        } catch (Exception e) {
            logger.error("工作流规划失败", e);
            return createErrorWorkflow(userInput, e.getMessage());
        }
    }

    /**
     * 构建工作流规划提示词
     */
    private String buildWorkflowPlanningPrompt(String userInput, Map<String, Object> context, List<String> detectedObjects) {
        StringBuilder prompt = new StringBuilder();

        prompt.append("你是一个专业的智能工作流规划助手。请分析用户请求并生成详细的工作流计划。\n\n");

        // 用户输入
        prompt.append("用户请求: ").append(userInput).append("\n");

        // 当前上下文
        if (context != null && !context.isEmpty()) {
            prompt.append("当前上下文: ").append(formatContext(context)).append("\n");
        }

        // 视觉上下文
        if (detectedObjects != null && !detectedObjects.isEmpty()) {
            prompt.append("视觉上下文 - 检测到的物体: ").append(String.join(", ", detectedObjects)).append("\n");
        }

        // 可用工具信息
        prompt.append("\n可用工具列表:\n");
        availableTools.forEach((toolName, description) -> {
            prompt.append("- ").append(toolName).append(": ").append(description).append("\n");
        });

        prompt.append("\n请生成JSON格式的工作流计划，必须包含以下字段:\n");
        prompt.append("{\n");
        prompt.append("  \"intent\": \"用户的核心意图\",\n");
        prompt.append("  \"description\": \"工作流描述\",\n");
        prompt.append("  \"steps\": [\n");
        prompt.append("    {\n");
        prompt.append("      \"step_id\": 1,\n");
        prompt.append("      \"tool_name\": \"工具名称\",\n");
        prompt.append("      \"action\": \"具体动作\",\n");
        prompt.append("      \"parameters\": {\"参数1\": \"值1\", \"参数2\": \"值2\"},\n");
        prompt.append("      \"dependencies\": [],  // 依赖的前置步骤ID\n");
        prompt.append("      \"description\": \"步骤描述\",\n");
        prompt.append("      \"requires_confirmation\": false  // 是否需要用户确认\n");
        prompt.append("    }\n");
        prompt.append("  ],\n");
        prompt.append("  \"estimated_duration\": 30,  // 预估执行时间（秒）\n");
        prompt.append("  \"required_permissions\": [\"file_access\", \"network\"]  // 所需权限\n");
        prompt.append("}\n");

        prompt.append("\n重要要求:\n");
        prompt.append("1. 步骤要具体可执行\n");
        prompt.append("2. 参数要明确指定\n");
        prompt.append("3. 考虑步骤间的依赖关系\n");
        prompt.append("4. 确保工具和动作的正确性\n");
        prompt.append("5. 提供合理的执行时间估算\n");
        prompt.append("6. 对于用户提到的'这个'、'它'等代词，根据视觉上下文理解具体指代的物体\n");

        return prompt.toString();
    }

    /**
     * 解析LLM响应为工作流对象
     */
    private Workflow parseWorkflowResponse(String llmResponse, String originalInput) {
        try {
            // 提取JSON部分
            String jsonStr = extractJsonFromResponse(llmResponse);
            if (jsonStr == null) {
                throw new RuntimeException("无法从LLM响应中提取JSON");
            }

            logger.info("提取的JSON: {}", jsonStr);

            // 解析JSON
            JsonNode rootNode = objectMapper.readTree(jsonStr);

            // 创建工作流
            Workflow workflow = new Workflow();
            workflow.setWorkflowId("workflow_" + System.currentTimeMillis());
            workflow.setIntent(rootNode.path("intent").asText("未知意图"));
            workflow.setDescription(rootNode.path("description").asText(""));
            workflow.setEstimatedDuration(rootNode.path("estimated_duration").asInt(0));
            workflow.setRequiredPermissions(rootNode.path("required_permissions").toString());
            workflow.setStatus("PENDING");
            workflow.setCreatedAt(LocalDateTime.now());

            // 解析步骤
            List<WorkflowStep> steps = new ArrayList<>();
            JsonNode stepsNode = rootNode.path("steps");

            if (stepsNode.isArray()) {
                for (JsonNode stepNode : stepsNode) {
                    WorkflowStep step = new WorkflowStep();
                    step.setWorkflowId(workflow.getWorkflowId());
                    step.setStepId(stepNode.path("step_id").asInt());
                    step.setToolName(stepNode.path("tool_name").asText());
                    step.setAction(stepNode.path("action").asText());
                    step.setParameters(stepNode.path("parameters").toString());
                    step.setDependencies(stepNode.path("dependencies").toString());
                    step.setDescription(stepNode.path("description").asText());
                    step.setRequiresConfirmation(stepNode.path("requires_confirmation").asBoolean(false));
                    step.setStatus("PENDING");
                    step.setCreatedAt(LocalDateTime.now());

                    steps.add(step);
                }
            }

            workflow.setSteps(steps);

            logger.info("工作流解析成功 - 工作流: {}, 步骤数: {}",
                       workflow.getDescription(), steps.size());

            return workflow;

        } catch (JsonProcessingException e) {
            logger.error("JSON解析失败", e);
            throw new RuntimeException("工作流解析失败: " + e.getMessage());
        } catch (Exception e) {
            logger.error("工作流解析异常", e);
            throw new RuntimeException("工作流解析异常: " + e.getMessage());
        }
    }

    /**
     * 从LLM响应中提取JSON部分
     */
    private String extractJsonFromResponse(String response) {
        if (response == null || response.trim().isEmpty()) {
            return null;
        }

        String trimmedResponse = response.trim();

        // 查找JSON开始
        int jsonStart = trimmedResponse.indexOf('{');
        if (jsonStart == -1) {
            return null;
        }

        // 查找JSON结束
        int braceCount = 0;
        int jsonEnd = -1;

        for (int i = jsonStart; i < trimmedResponse.length(); i++) {
            char c = trimmedResponse.charAt(i);
            if (c == '{') {
                braceCount++;
            } else if (c == '}') {
                braceCount--;
                if (braceCount == 0) {
                    jsonEnd = i + 1;
                    break;
                }
            }
        }

        if (jsonEnd == -1) {
            return null;
        }

        return trimmedResponse.substring(jsonStart, jsonEnd);
    }

    /**
     * 格式化上下文
     */
    private String formatContext(Map<String, Object> context) {
        try {
            return objectMapper.writeValueAsString(context);
        } catch (JsonProcessingException e) {
            return context.toString();
        }
    }

    /**
     * 创建错误工作流
     */
    private Workflow createErrorWorkflow(String userInput, String errorMessage) {
        Workflow workflow = new Workflow();
        workflow.setWorkflowId("error_" + System.currentTimeMillis());
        workflow.setIntent("规划失败");
        workflow.setDescription("工作流规划失败: " + errorMessage);
        workflow.setStatus("FAILED");
        workflow.setCreatedAt(LocalDateTime.now());
        workflow.setSteps(new ArrayList<>());

        logger.error("创建错误工作流: {}", errorMessage);
        return workflow;
    }

    /**
     * 获取可用工具列表
     */
    public Map<String, String> getAvailableTools() {
        return new HashMap<>(availableTools);
    }
}