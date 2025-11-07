package com.example.aiorchestrator.dto;

public class ConfigMappingRow {
    private String gestureCode;
    private String gestureName;
    private String gestureType;
    private String actionType;
    private String actionValue;
    private String osType;
    private String actionDescription;
    private String actionPayloadJson;
    private Integer priority;

    public String getGestureCode() {
        return gestureCode;
    }

    public void setGestureCode(String gestureCode) {
        this.gestureCode = gestureCode;
    }

    public String getGestureName() {
        return gestureName;
    }

    public void setGestureName(String gestureName) {
        this.gestureName = gestureName;
    }

    public String getGestureType() {
        return gestureType;
    }

    public void setGestureType(String gestureType) {
        this.gestureType = gestureType;
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

    public String getOsType() {
        return osType;
    }

    public void setOsType(String osType) {
        this.osType = osType;
    }

    public String getActionDescription() {
        return actionDescription;
    }

    public void setActionDescription(String actionDescription) {
        this.actionDescription = actionDescription;
    }

    public String getActionPayloadJson() {
        return actionPayloadJson;
    }

    public void setActionPayloadJson(String actionPayloadJson) {
        this.actionPayloadJson = actionPayloadJson;
    }

    public Integer getPriority() {
        return priority;
    }

    public void setPriority(Integer priority) {
        this.priority = priority;
    }
}


