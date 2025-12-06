package com.example.aiorchestrator.domain;

import com.fasterxml.jackson.annotation.JsonFormat;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * 工作流执行结果
 */
public class ExecutionResult {

    private String workflowId;
    private Boolean success;
    private List<WorkflowStep> completedSteps;
    private List<WorkflowStep> failedSteps;
    private Map<String, Object> finalContext;
    private Float executionTime;
    private String userMessage;
    private String errorMessage;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime executedAt;

    // Constructors
    public ExecutionResult() {
        this.executedAt = LocalDateTime.now();
    }

    public ExecutionResult(String workflowId, Boolean success, List<WorkflowStep> completedSteps,
                           List<WorkflowStep> failedSteps, Float executionTime, String userMessage) {
        this.workflowId = workflowId;
        this.success = success;
        this.completedSteps = completedSteps;
        this.failedSteps = failedSteps;
        this.executionTime = executionTime;
        this.userMessage = userMessage;
        this.executedAt = LocalDateTime.now();
    }

    // Getters and Setters
    public String getWorkflowId() {
        return workflowId;
    }

    public void setWorkflowId(String workflowId) {
        this.workflowId = workflowId;
    }

    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public List<WorkflowStep> getCompletedSteps() {
        return completedSteps;
    }

    public void setCompletedSteps(List<WorkflowStep> completedSteps) {
        this.completedSteps = completedSteps;
    }

    public List<WorkflowStep> getFailedSteps() {
        return failedSteps;
    }

    public void setFailedSteps(List<WorkflowStep> failedSteps) {
        this.failedSteps = failedSteps;
    }

    public Map<String, Object> getFinalContext() {
        return finalContext;
    }

    public void setFinalContext(Map<String, Object> finalContext) {
        this.finalContext = finalContext;
    }

    public Float getExecutionTime() {
        return executionTime;
    }

    public void setExecutionTime(Float executionTime) {
        this.executionTime = executionTime;
    }

    public String getUserMessage() {
        return userMessage;
    }

    public void setUserMessage(String userMessage) {
        this.userMessage = userMessage;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public LocalDateTime getExecutedAt() {
        return executedAt;
    }

    public void setExecutedAt(LocalDateTime executedAt) {
        this.executedAt = executedAt;
    }
}