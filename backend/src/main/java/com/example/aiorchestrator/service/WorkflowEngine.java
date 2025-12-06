package com.example.aiorchestrator.service;

import com.example.aiorchestrator.domain.ExecutionResult;
import com.example.aiorchestrator.domain.Workflow;
import com.example.aiorchestrator.domain.WorkflowStep;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 工作流编排引擎 - 负责执行工作流
 */
@Service
public class WorkflowEngine {

    private static final Logger logger = LoggerFactory.getLogger(WorkflowEngine.class);

    @Autowired
    private LlmService llmService;

    @Autowired
    private AgentCommunicationService agentCommunicationService;

    private final ObjectMapper objectMapper = new ObjectMapper();

    // 需要在本地执行的工具
    private final Set<String> localTools = Set.of("messaging", "web", "ai");

    /**
     * 执行工作流
     */
    public ExecutionResult executeWorkflow(Workflow workflow, Map<String, Object> context) {
        logger.info("开始执行工作流 - 工作流ID: {}", workflow.getWorkflowId());

        long startTime = System.currentTimeMillis();
        List<WorkflowStep> completedSteps = new ArrayList<>();
        List<WorkflowStep> failedSteps = new ArrayList<>();
        Map<String, Object> executionContext = new HashMap<>(context);

        try {
            // 按依赖关系排序步骤
            List<WorkflowStep> sortedSteps = sortStepsByDependencies(workflow.getSteps());

            for (WorkflowStep step : sortedSteps) {
                if (canExecuteStep(step, completedSteps)) {
                    step.setStatus("RUNNING");
                    step.setExecutedAt(LocalDateTime.now());

                    try {
                        // 检查是否需要确认
                        if (step.getRequiresConfirmation() != null && step.getRequiresConfirmation()) {
                            boolean confirmed = requestUserConfirmation(step);
                            if (!confirmed) {
                                step.setStatus("SKIPPED");
                                continue;
                            }
                        }

                        // 执行步骤
                        ExecutionStepResult result = executeStep(step, executionContext);

                        // 更新步骤状态
                        if (result.isSuccess()) {
                            step.setStatus("COMPLETED");
                            step.setExecutionResult(objectMapper.writeValueAsString(result.getData()));
                            completedSteps.add(step);

                            // 更新执行上下文
                            if (result.getContextUpdate() != null) {
                                executionContext.putAll(result.getContextUpdate());
                            }

                            logger.info("步骤 {} 执行成功: {}", step.getStepId(), result.getMessage());
                        } else {
                            step.setStatus("FAILED");
                            step.setErrorMessage(result.getMessage());
                            failedSteps.add(step);
                            logger.error("步骤 {} 执行失败: {}", step.getStepId(), result.getMessage());

                            // 根据错误处理策略决定是否继续
                            if (!shouldContinueOnError(step, failedSteps)) {
                                break;
                            }
                        }

                    } catch (Exception e) {
                        step.setStatus("FAILED");
                        step.setErrorMessage(e.getMessage());
                        failedSteps.add(step);
                        logger.error("步骤 {} 执行异常: {}", step.getStepId(), e.getMessage());

                        if (!shouldContinueOnError(step, failedSteps)) {
                            break;
                        }
                    }
                } else {
                    step.setStatus("SKIPPED");
                    logger.warn("跳过步骤 {}: 依赖未满足", step.getStepId());
                }
            }

            // 计算执行结果
            float executionTime = (System.currentTimeMillis() - startTime) / 1000.0f;
            boolean success = failedSteps.isEmpty();
            String userMessage = generateUserMessage(workflow, completedSteps, failedSteps);

            ExecutionResult executionResult = new ExecutionResult();
            executionResult.setWorkflowId(workflow.getWorkflowId());
            executionResult.setSuccess(success);
            executionResult.setCompletedSteps(completedSteps);
            executionResult.setFailedSteps(failedSteps);
            executionResult.setFinalContext(executionContext);
            executionResult.setExecutionTime(executionTime);
            executionResult.setUserMessage(userMessage);

            logger.info("工作流执行完成 - 成功: {}, 执行时间: {}秒", success, executionTime);

            return executionResult;

        } catch (Exception e) {
            logger.error("工作流执行异常", e);

            ExecutionResult errorResult = new ExecutionResult();
            errorResult.setWorkflowId(workflow.getWorkflowId());
            errorResult.setSuccess(false);
            errorResult.setCompletedSteps(completedSteps);
            errorResult.setFailedSteps(failedSteps);
            errorResult.setExecutionTime((System.currentTimeMillis() - startTime) / 1000.0f);
            errorResult.setErrorMessage(e.getMessage());
            errorResult.setUserMessage("工作流执行失败: " + e.getMessage());

            return errorResult;
        }
    }

    /**
     * 执行单个步骤
     */
    private ExecutionStepResult executeStep(WorkflowStep step, Map<String, Object> context) {
        try {
            String toolName = step.getToolName();
            String action = step.getAction();
            Map<String, Object> parameters = parseParameters(step.getParameters());

            logger.info("执行步骤 - 工具: {}, 动作: {}, 参数: {}", toolName, action, parameters);

            if (localTools.contains(toolName)) {
                // 本地执行
                return executeLocalStep(toolName, action, parameters, context);
            } else {
                // 交由Agent执行
                return executeAgentStep(step, context);
            }

        } catch (Exception e) {
            logger.error("步骤执行异常", e);
            return ExecutionStepResult.failure("步骤执行失败: " + e.getMessage());
        }
    }

    /**
     * 执行本地步骤
     */
    private ExecutionStepResult executeLocalStep(String toolName, String action,
                                                Map<String, Object> parameters, Map<String, Object> context) {
        switch (toolName) {
            case "messaging":
                return executeMessagingAction(action, parameters, context);
            case "web":
                return executeWebAction(action, parameters, context);
            case "ai":
                return executeAIAction(action, parameters, context);
            default:
                return ExecutionStepResult.failure("不支持的本地工具: " + toolName);
        }
    }

    /**
     * 执行Agent步骤
     */
    private ExecutionStepResult executeAgentStep(WorkflowStep step, Map<String, Object> context) {
        try {
            Map<String, Object> agentRequest = new HashMap<>();
            agentRequest.put("workflow_id", step.getWorkflowId());
            agentRequest.put("step_id", step.getStepId());
            agentRequest.put("tool_name", step.getToolName());
            agentRequest.put("action", step.getAction());
            agentRequest.put("parameters", parseParameters(step.getParameters()));
            agentRequest.put("context", context);

            // 发送给Agent执行
            Map<String, Object> agentResponse = agentCommunicationService.sendCommandToAgent(agentRequest);

            if ((Boolean) agentResponse.getOrDefault("success", false)) {
                return ExecutionStepResult.success(
                    (String) agentResponse.get("message"),
                    (Map<String, Object>) agentResponse.get("data"),
                    (Map<String, Object>) agentResponse.get("context_update")
                );
            } else {
                return ExecutionStepResult.failure((String) agentResponse.get("error"));
            }

        } catch (Exception e) {
            logger.error("Agent通信失败", e);
            return ExecutionStepResult.failure("Agent通信失败: " + e.getMessage());
        }
    }

    /**
     * 执行消息发送动作
     */
    private ExecutionStepResult executeMessagingAction(String action, Map<String, Object> parameters, Map<String, Object> context) {
        switch (action) {
            case "send_notification":
                try {
                    String title = (String) parameters.getOrDefault("title", "YOLO-LLM 通知");
                    String message = (String) parameters.getOrDefault("message", "");

                    // 这里可以调用桌面通知API
                    logger.info("发送桌面通知 - 标题: {}, 内容: {}", title, message);

                    Map<String, Object> data = new HashMap<>();
                    data.put("notification_type", "desktop");

                    return ExecutionStepResult.success("桌面通知已发送", data);
                } catch (Exception e) {
                    return ExecutionStepResult.failure("发送通知失败: " + e.getMessage());
                }
            default:
                return ExecutionStepResult.failure("不支持的消息动作: " + action);
        }
    }

    /**
     * 执行网络动作
     */
    private ExecutionStepResult executeWebAction(String action, Map<String, Object> parameters, Map<String, Object> context) {
        switch (action) {
            case "summarize_content":
                try {
                    String content = (String) parameters.getOrDefault("content", "");
                    if (content.isEmpty()) {
                        return ExecutionStepResult.failure("内容不能为空");
                    }

                    // 调用LLM进行总结
                    String prompt = "请总结以下内容：\n" + content;
                    String summary = llmService.planWorkflow(prompt, context, new ArrayList<>()).getDescription();

                    Map<String, Object> data = new HashMap<>();
                    data.put("summary", summary);

                    return ExecutionStepResult.success("内容总结完成", data);
                } catch (Exception e) {
                    return ExecutionStepResult.failure("内容总结失败: " + e.getMessage());
                }
            default:
                return ExecutionStepResult.failure("不支持的网络动作: " + action);
        }
    }

    /**
     * 执行AI动作
     */
    private ExecutionStepResult executeAIAction(String action, Map<String, Object> parameters, Map<String, Object> context) {
        switch (action) {
            case "generate_todo":
                try {
                    String date = (String) parameters.getOrDefault("date", "今天");
                    String prompt = String.format("请为%s生成一个TODO列表，包含5-8个重要任务", date);

                    Workflow todoWorkflow = llmService.planWorkflow(prompt, context, new ArrayList<>());
                    String todoContent = todoWorkflow.getDescription();

                    Map<String, Object> data = new HashMap<>();
                    data.put("todo_list", todoContent);
                    data.put("generated_date", date);

                    return ExecutionStepResult.success("TODO列表生成完成", data);
                } catch (Exception e) {
                    return ExecutionStepResult.failure("TODO生成失败: " + e.getMessage());
                }
            default:
                return ExecutionStepResult.failure("不支持的AI动作: " + action);
        }
    }

    /**
     * 按依赖关系排序步骤
     */
    private List<WorkflowStep> sortStepsByDependencies(List<WorkflowStep> steps) {
        if (steps == null || steps.isEmpty()) {
            return new ArrayList<>();
        }

        // 简单实现：按step_id排序
        // 实际项目中需要实现完整的拓扑排序
        return steps.stream()
                .sorted(Comparator.comparing(WorkflowStep::getStepId))
                .collect(Collectors.toList());
    }

    /**
     * 检查步骤是否可以执行
     */
    private boolean canExecuteStep(WorkflowStep step, List<WorkflowStep> completedSteps) {
        try {
            List<Integer> dependencies = parseDependencies(step.getDependencies());
            if (dependencies.isEmpty()) {
                return true;
            }

            Set<Integer> completedStepIds = completedSteps.stream()
                    .map(WorkflowStep::getStepId)
                    .collect(Collectors.toSet());

            return dependencies.stream().allMatch(completedStepIds::contains);
        } catch (Exception e) {
            logger.error("检查步骤依赖失败", e);
            return false;
        }
    }

    /**
     * 决定遇到错误时是否继续执行
     */
    private boolean shouldContinueOnError(WorkflowStep step, List<WorkflowStep> failedSteps) {
        // 简单策略：失败步骤少于3个时继续
        return failedSteps.size() < 3;
    }

    /**
     * 请求用户确认
     */
    private boolean requestUserConfirmation(WorkflowStep step) {
        // 这里可以实现具体的确认逻辑
        // 例如：等待用户做"OK"手势或语音确认
        logger.info("请求用户确认 - 步骤: {}", step.getDescription());
        return true; // 暂时直接返回true
    }

    /**
     * 生成用户友好的执行结果消息
     */
    private String generateUserMessage(Workflow workflow, List<WorkflowStep> completedSteps, List<WorkflowStep> failedSteps) {
        if (failedSteps.isEmpty()) {
            return String.format("✅ 工作流执行成功！完成了 %d 个步骤：%s",
                                completedSteps.size(), workflow.getDescription());
        } else {
            return String.format("⚠️ 工作流部分完成。成功 %d 个步骤，失败 %d 个步骤。",
                                completedSteps.size(), failedSteps.size());
        }
    }

    /**
     * 解析参数JSON
     */
    private Map<String, Object> parseParameters(String parametersJson) {
        try {
            if (parametersJson == null || parametersJson.trim().isEmpty()) {
                return new HashMap<>();
            }
            return objectMapper.readValue(parametersJson, new TypeReference<Map<String, Object>>() {});
        } catch (JsonProcessingException e) {
            logger.error("参数解析失败", e);
            return new HashMap<>();
        }
    }

    /**
     * 解析依赖列表
     */
    private List<Integer> parseDependencies(String dependenciesJson) {
        try {
            if (dependenciesJson == null || dependenciesJson.trim().isEmpty()) {
                return new ArrayList<>();
            }
            return objectMapper.readValue(dependenciesJson, new TypeReference<List<Integer>>() {});
        } catch (JsonProcessingException e) {
            logger.error("依赖解析失败", e);
            return new ArrayList<>();
        }
    }

    /**
     * 执行步骤结果
     */
    private static class ExecutionStepResult {
        private boolean success;
        private String message;
        private Map<String, Object> data;
        private Map<String, Object> contextUpdate;

        public static ExecutionStepResult success(String message, Map<String, Object> data) {
            return success(message, data, null);
        }

        public static ExecutionStepResult success(String message, Map<String, Object> data, Map<String, Object> contextUpdate) {
            ExecutionStepResult result = new ExecutionStepResult();
            result.success = true;
            result.message = message;
            result.data = data != null ? data : new HashMap<>();
            result.contextUpdate = contextUpdate;
            return result;
        }

        public static ExecutionStepResult failure(String message) {
            ExecutionStepResult result = new ExecutionStepResult();
            result.success = false;
            result.message = message;
            result.data = new HashMap<>();
            return result;
        }

        // Getters
        public boolean isSuccess() { return success; }
        public String getMessage() { return message; }
        public Map<String, Object> getData() { return data; }
        public Map<String, Object> getContextUpdate() { return contextUpdate; }
    }
}