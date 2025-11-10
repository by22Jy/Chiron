package com.example.aiorchestrator.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import java.time.LocalDateTime;

@TableName("logs")
public class LogEntry {

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    @TableField("user_id")
    private Long userId;

    @TableField("application_id")
    private Long applicationId;

    @TableField("gesture_code")
    private String gestureCode;

    @TableField("action_type")
    private String actionType;

    @TableField("action_value")
    private String actionValue;

    private String status;

    private String message;

    @TableField("source_agent")
    private String sourceAgent;

    @TableField("created_at")
    private LocalDateTime createdAt;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public Long getApplicationId() {
        return applicationId;
    }

    public void setApplicationId(Long applicationId) {
        this.applicationId = applicationId;
    }

    public String getGestureCode() {
        return gestureCode;
    }

    public void setGestureCode(String gestureCode) {
        this.gestureCode = gestureCode;
    }

    public String getActionType() {
        return actionType;
    }

    public void setActionType(String actionType) {
        this.actionType = actionType;
    }

    public String getActionValue() {
        return actionValue;
    }

    public void setActionValue(String actionValue) {
        this.actionValue = actionValue;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getSourceAgent() {
        return sourceAgent;
    }

    public void setSourceAgent(String sourceAgent) {
        this.sourceAgent = sourceAgent;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}


