package com.example.aiorchestrator.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * 工作流步骤实体
 */
@TableName("workflow_steps")
public class WorkflowStep {

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    @TableField("workflow_id")
    private String workflowId;

    @TableField("step_id")
    private Integer stepId;

    @TableField("tool_name")
    private String toolName;

    @TableField("action")
    private String action;

    @TableField("parameters")
    private String parameters; // JSON string

    @TableField("dependencies")
    private String dependencies; // JSON array string

    @TableField("description")
    private String description;

    @TableField("status")
    private String status; // PENDING, RUNNING, COMPLETED, FAILED, SKIPPED

    @TableField("error_message")
    private String errorMessage;

    @TableField("execution_result")
    private String executionResult; // JSON string

    @TableField("requires_confirmation")
    private Boolean requiresConfirmation;

    @TableField("executed_at")
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime executedAt;

    @TableField("created_at")
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime createdAt;

    // Runtime fields
    @TableField(exist = false)
    private Map<String, Object> parameterMap;

    @TableField(exist = false)
    private List<Integer> dependencyList;

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getWorkflowId() {
        return workflowId;
    }

    public void setWorkflowId(String workflowId) {
        this.workflowId = workflowId;
    }

    public Integer getStepId() {
        return stepId;
    }

    public void setStepId(Integer stepId) {
        this.stepId = stepId;
    }

    public String getToolName() {
        return toolName;
    }

    public void setToolName(String toolName) {
        this.toolName = toolName;
    }

    public String getAction() {
        return action;
    }

    public void setAction(String action) {
        this.action = action;
    }

    public String getParameters() {
        return parameters;
    }

    public void setParameters(String parameters) {
        this.parameters = parameters;
    }

    public String getDependencies() {
        return dependencies;
    }

    public void setDependencies(String dependencies) {
        this.dependencies = dependencies;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public String getExecutionResult() {
        return executionResult;
    }

    public void setExecutionResult(String executionResult) {
        this.executionResult = executionResult;
    }

    public Boolean getRequiresConfirmation() {
        return requiresConfirmation;
    }

    public void setRequiresConfirmation(Boolean requiresConfirmation) {
        this.requiresConfirmation = requiresConfirmation;
    }

    public LocalDateTime getExecutedAt() {
        return executedAt;
    }

    public void setExecutedAt(LocalDateTime executedAt) {
        this.executedAt = executedAt;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public Map<String, Object> getParameterMap() {
        return parameterMap;
    }

    public void setParameterMap(Map<String, Object> parameterMap) {
        this.parameterMap = parameterMap;
    }

    public List<Integer> getDependencyList() {
        return dependencyList;
    }

    public void setDependencyList(List<Integer> dependencyList) {
        this.dependencyList = dependencyList;
    }
}