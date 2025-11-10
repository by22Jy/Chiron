package com.example.aiorchestrator.dto;

public class LogRequest {

    private String username;
    private String application;
    private String gestureCode;
    private String actionType;
    private String actionValue;
    private String status;
    private String message;
    private String sourceAgent;

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getApplication() {
        return application;
    }

    public void setApplication(String application) {
        this.application = application;
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
}


