package com.example.aiorchestrator.util;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

/**
 * 数据格式标准化工具
 * 负责将非标准格式的数据转换为标准格式
 */
@Component
public class DataFormatStandardizer {

    private static final DateTimeFormatter ISO_FORMATTER =
        DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss'Z'").withZone(ZoneOffset.UTC);

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * 标准化响应格式
     * 将旧格式转换为标准格式
     */
    public Map<String, Object> standardizeResponse(Map<String, Object> oldResponse, String status, String message) {
        Map<String, Object> standardResponse = new HashMap<>();

        // 标准字段
        standardResponse.put("status", status);
        standardResponse.put("message", message);
        standardResponse.put("timestamp", getCurrentIsoTimestamp());

        // 将原来的success和response字段合并到data中
        Map<String, Object> data = new HashMap<>();
        data.put("original_response", oldResponse.get("response"));
        data.put("original_success", oldResponse.get("success"));

        // 复制其他字段到data中
        oldResponse.forEach((key, value) -> {
            if (!key.equals("success") && !key.equals("timestamp")) {
                data.put(key, value);
            }
        });

        standardResponse.put("data", data);

        return standardResponse;
    }

    /**
     * 标准化错误响应
     */
    public Map<String, Object> standardizeErrorResponse(Exception e, String defaultMessage) {
        Map<String, Object> standardResponse = new HashMap<>();

        standardResponse.put("status", "error");
        standardResponse.put("message", defaultMessage);
        standardResponse.put("timestamp", getCurrentIsoTimestamp());

        Map<String, Object> data = new HashMap<>();
        data.put("error_type", e.getClass().getSimpleName());
        data.put("error_message", e.getMessage());
        data.put("stack_trace", getStackTraceString(e));

        standardResponse.put("data", data);

        return standardResponse;
    }

    /**
     * 转换时间戳为ISO格式
     */
    public String convertTimestampToIso(Object timestamp) {
        if (timestamp == null) {
            return getCurrentIsoTimestamp();
        }

        if (timestamp instanceof Long) {
            // Java时间戳（毫秒）
            return Instant.ofEpochMilli((Long) timestamp).atZone(ZoneOffset.UTC).format(ISO_FORMATTER);
        } else if (timestamp instanceof Integer) {
            // Java时间戳（秒）
            return Instant.ofEpochSecond((Integer) timestamp).atZone(ZoneOffset.UTC).format(ISO_FORMATTER);
        } else if (timestamp instanceof String) {
            // 已经是字符串格式，验证是否为ISO格式
            String strTimestamp = (String) timestamp;
            if (strTimestamp.contains("T") && (strTimestamp.contains("Z") || strTimestamp.contains("+"))) {
                return strTimestamp; // 已经是ISO格式
            } else {
                // 尝试解析为数字时间戳
                try {
                    long numericTimestamp = Long.parseLong(strTimestamp);
                    return Instant.ofEpochMilli(numericTimestamp).atZone(ZoneOffset.UTC).format(ISO_FORMATTER);
                } catch (NumberFormatException e) {
                    return getCurrentIsoTimestamp(); // 无法解析，使用当前时间
                }
            }
        }

        return getCurrentIsoTimestamp();
    }

    /**
     * 验证请求格式是否符合标准
     */
    public Map<String, Object> validateRequestFormat(Map<String, Object> request) {
        Map<String, Object> validation = new HashMap<>();
        validation.put("valid", true);
        validation.put("errors", new java.util.ArrayList<String>());

        @SuppressWarnings("unchecked")
        java.util.List<String> errors = (java.util.List<String>) validation.get("errors");

        // 检查必需字段
        if (request == null) {
            errors.add("请求体不能为空");
            validation.put("valid", false);
            return validation;
        }

        // 根据不同的端点检查必需字段
        if (request.containsKey("command") && !(request.get("command") instanceof String)) {
            errors.add("command字段必须是字符串");
        }

        if (request.containsKey("prompt") && !(request.get("prompt") instanceof String)) {
            errors.add("prompt字段必须是字符串");
        }

        if (request.containsKey("confidence") && !(request.get("confidence") instanceof Number)) {
            errors.add("confidence字段必须是数字");
        }

        // 检查时间戳格式
        if (request.containsKey("timestamp")) {
            String isoTimestamp = convertTimestampToIso(request.get("timestamp"));
            if (isoTimestamp == null) {
                errors.add("timestamp格式无效");
            }
        }

        if (!errors.isEmpty()) {
            validation.put("valid", false);
        }

        return validation;
    }

    /**
     * 标准化枚举值
     */
    public String standardizeEnumValue(String value, String enumType) {
        if (value == null) {
            return null;
        }

        switch (enumType.toLowerCase()) {
            case "status":
                return value.toLowerCase(); // 统一使用小写
            case "action_type":
                return value.toLowerCase(); // 统一使用小写
            case "gesture_name":
                return value.toUpperCase().replace(" ", "_"); // 大写下划线格式
            default:
                return value;
        }
    }

    /**
     * 获取当前ISO格式时间戳
     */
    private String getCurrentIsoTimestamp() {
        return Instant.now().atZone(ZoneOffset.UTC).format(ISO_FORMATTER);
    }

    /**
     * 获取异常堆栈跟踪字符串
     */
    private String getStackTraceString(Exception e) {
        java.io.StringWriter sw = new java.io.StringWriter();
        java.io.PrintWriter pw = new java.io.PrintWriter(sw);
        e.printStackTrace(pw);
        return sw.toString();
    }
}