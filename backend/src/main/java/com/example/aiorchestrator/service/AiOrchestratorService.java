package com.example.aiorchestrator.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.util.UriUtils;

import java.nio.charset.StandardCharsets;
import java.util.*;

@Service
public class AiOrchestratorService {

    private static final Logger logger = LoggerFactory.getLogger(AiOrchestratorService.class);
    private final RestTemplate restTemplate = new RestTemplate();

    @Autowired(required = false)
    private MCPIntegrationService mcpIntegrationService;

    @Value("${ai.yolo.url-detect-file}") private String yoloDetectFileUrl;
    @Value("${ai.yolo.url-detect-url}")  private String yoloDetectUrlUrl;

    @Value("${ai.llm.provider}") private String provider;
    @Value("${ai.llm.kimi.api-url}") private String kimiUrl;
    @Value("${ai.llm.kimi.api-key}") private String kimiKey;
    @Value("${ai.llm.kimi.model}")  private String kimiModel;

    @Value("${ai.llm.qwen.api-url}") private String qwenUrl;
    @Value("${ai.llm.qwen.api-key}") private String qwenKey;
    @Value("${ai.llm.qwen.model}")  private String qwenModel;

    @Value("${ai.llm.glm.api-url}") private String glmUrl;
    @Value("${ai.llm.glm.api-key}") private String glmKey;
    @Value("${ai.llm.glm.model}")  private String glmModel;

    @Value("${ai.llm.deepseek.api-url}") private String deepseekUrl;
    @Value("${ai.llm.deepseek.api-key}") private String deepseekKey;
    @Value("${ai.llm.deepseek.model}")  private String deepseekModel;

    public String orchestrate(MultipartFile image, String question) {
        List<String> objects = callYoloWithFile(image);
        String prompt = buildPrompt(objects, question);
        return callLlm(prompt);
    }

    public String orchestrateByUrl(String imageUrl, String question) {
        // 如果没有图片URL，直接调用LLM
        if (imageUrl == null || imageUrl.trim().isEmpty()) {
            logger.info("没有图片URL，直接调用LLM");
            return callLlm(question);
        }

        List<String> objects = callYoloWithUrl(imageUrl);
        String prompt = buildPrompt(objects, question);
        return callLlm(prompt);
    }

    private List<String> callYoloWithFile(MultipartFile image) {
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        try {
            body.add("file", new ByteArrayResource(image.getBytes()) {
                @Override public String getFilename() { return image.getOriginalFilename(); }
            });
        } catch (Exception e) { throw new RuntimeException(e); }
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);
        HttpEntity<MultiValueMap<String, Object>> req = new HttpEntity<>(body, headers);
        ResponseEntity<Map> resp = restTemplate.postForEntity(yoloDetectFileUrl, req, Map.class);
        return extractObjects(resp.getBody());
    }

    private List<String> callYoloWithUrl(String url) {
        String reqUrl = yoloDetectUrlUrl + "?url=" + UriUtils.encode(url, StandardCharsets.UTF_8);
        ResponseEntity<Map> resp = restTemplate.postForEntity(reqUrl, null, Map.class);
        return extractObjects(resp.getBody());
    }

    @SuppressWarnings("unchecked")
    private List<String> extractObjects(Map body) {
        if (body == null) return List.of();
        Object objs = body.get("objects");
        if (objs instanceof List<?> l) return l.stream().map(Object::toString).distinct().toList();
        return List.of();
    }

    private String buildPrompt(List<String> objects, String question) {
        return "图像中的关键物体有: " + String.join(", ", objects) + "。基于这些物体，请回答用户的问题: '" + question + "'。请简洁作答。";
    }

    private String callLlm(String prompt) {
        if ("kimi".equalsIgnoreCase(provider)) {
            return callOpenAICompat(kimiUrl, kimiKey, kimiModel, prompt);
        } else if ("qwen".equalsIgnoreCase(provider)) {
            return callOpenAICompat(qwenUrl, qwenKey, qwenModel, prompt);
        } else if ("glm".equalsIgnoreCase(provider)) {
            return callGLM(glmUrl, glmKey, glmModel, prompt);
        } else if ("deepseek".equalsIgnoreCase(provider)) {
            return callOpenAICompat(deepseekUrl, deepseekKey, deepseekModel, prompt);
        } else {
            return callOpenAICompat(deepseekUrl, deepseekKey, deepseekModel, prompt);
        }
    }

    private String callOpenAICompat(String url, String apiKey, String model, String prompt) {
        HttpHeaders h = new HttpHeaders();
        h.setContentType(MediaType.APPLICATION_JSON);
        h.setBearerAuth(apiKey);
        Map<String, Object> body = Map.of(
                "model", model,
                "messages", List.of(Map.of("role", "user", "content", prompt))
        );
        ResponseEntity<Map> resp = restTemplate.postForEntity(url, new HttpEntity<>(body, h), Map.class);
        return parseOpenAIStyle(resp.getBody());
    }

    private String callGLM(String url, String apiKey, String model, String prompt) {
        logger.info("开始调用GLM API");
        logger.info("URL: {}", url);
        logger.info("Model: {}", model);
        logger.info("API Key: {}", apiKey != null ? apiKey.substring(0, Math.min(10, apiKey.length())) + "***" : "null");
        logger.info("Prompt: {}", prompt);

        try {
            HttpHeaders h = new HttpHeaders();
            h.setContentType(MediaType.APPLICATION_JSON);
            h.set("Authorization", "Bearer " + apiKey);

            Map<String, Object> body = Map.of(
                    "model", model,
                    "messages", List.of(Map.of("role", "user", "content", prompt)),
                    "max_tokens", 65536,
                    "temperature", 0.7
            );

            logger.info("请求体: {}", body);

            ResponseEntity<Map> resp = restTemplate.postForEntity(url, new HttpEntity<>(body, h), Map.class);

            logger.info("响应状态码: {}", resp.getStatusCode());
            logger.info("响应体: {}", resp.getBody());

            String result = parseOpenAIStyle(resp.getBody());
            logger.info("解析结果: {}", result);

            return result;
        } catch (Exception e) {
            logger.error("GLM API调用失败", e);
            logger.error("错误详情: {}", e.getMessage());
            return "GLM API调用失败: " + e.getMessage();
        }
    }

    @SuppressWarnings("unchecked")
    private String parseOpenAIStyle(Map body) {
        try {
            var choices = (List<Map<String, Object>>) body.get("choices");
            if (choices == null || choices.isEmpty()) return "LLM无结果";
            var msg = (Map<String, Object>) choices.get(0).get("message");
            return msg.getOrDefault("content", "").toString();
        } catch (Exception e) { return "解析失败: " + e.getMessage(); }
    }

    /**
     * 增强的LLM编排方法，支持MCP工具调用
     */
    public String orchestrateWithMCP(String prompt, List<String> requiredTools) {
        try {
            logger.info("开始MCP增强编排: {}, 所需工具: {}", prompt, requiredTools);

            // 1. 如果没有MCP服务，回退到普通LLM调用
            if (mcpIntegrationService == null) {
                logger.info("MCP服务不可用，使用普通LLM调用");
                return callLlm(prompt);
            }

            // 2. LLM分析任务，确定工具调用参数
            String analysisPrompt = buildAnalysisPrompt(prompt, requiredTools);
            String analysisResult = callLlm(analysisPrompt);
            logger.info("LLM分析结果: {}", analysisResult);

            // 3. 调用MCP工具
            Map<String, Object> toolResults = new HashMap<>();
            for (String tool : requiredTools) {
                try {
                    Map<String, Object> toolParams = extractToolParameters(analysisResult, tool);
                    Map<String, Object> toolResult = mcpIntegrationService.callMCPTool(tool, toolParams);
                    toolResults.put(tool, toolResult);
                    logger.info("工具 {} 调用结果: {}", tool, toolResult);
                } catch (Exception e) {
                    logger.error("工具 {} 调用失败: {}", tool, e.getMessage());
                    toolResults.put(tool, Map.of("success", false, "error", e.getMessage()));
                }
            }

            // 4. LLM整合工具结果，生成最终响应
            String finalPrompt = buildFinalPrompt(prompt, analysisResult, toolResults);
            String finalResponse = callLlm(finalPrompt);

            logger.info("MCP增强编排完成");
            return finalResponse;

        } catch (Exception e) {
            logger.error("MCP增强编排失败", e);
            return callLlm(prompt); // 回退到普通调用
        }
    }

    /**
     * 执行复杂工作流
     */
    public String executeComplexWorkflow(String workflowName, Map<String, Object> context) {
        try {
            logger.info("执行复杂工作流: {}", workflowName);

            if (mcpIntegrationService == null) {
                return "MCP服务不可用，无法执行复杂工作流";
            }

            Map<String, Object> result = mcpIntegrationService.executeWorkflow(workflowName, context);

            if ((Boolean) result.getOrDefault("success", false)) {
                return "工作流执行成功: " + result.get("message");
            } else {
                return "工作流执行失败: " + result.get("error");
            }

        } catch (Exception e) {
            logger.error("复杂工作流执行失败", e);
            return "工作流执行异常: " + e.getMessage();
        }
    }

    /**
     * 构建分析提示词
     */
    private String buildAnalysisPrompt(String originalPrompt, List<String> requiredTools) {
        StringBuilder sb = new StringBuilder();
        sb.append("你是一个智能任务分析专家。请分析用户任务，确定如何调用指定的工具。\n\n");
        sb.append("用户任务: ").append(originalPrompt).append("\n");
        sb.append("可用工具: ").append(String.join(", ", requiredTools)).append("\n\n");

        sb.append("请分析这个任务，为每个工具提供调用参数。返回JSON格式:\n");
        sb.append("{\n");
        sb.append("  \"analysis\": \"任务分析结果\",\n");
        sb.append("  \"tools\": {\n");

        for (String tool : requiredTools) {
            sb.append("    \"").append(tool).append("\": {\n");
            sb.append("      \"action\": \"具体操作\",\n");
            sb.append("      \"parameters\": {\"key\": \"value\"}\n");
            sb.append("    },\n");
        }

        sb.append("  }\n");
        sb.append("}\n");

        return sb.toString();
    }

    /**
     * 从LLM分析结果中提取工具参数
     */
    @SuppressWarnings("unchecked")
    private Map<String, Object> extractToolParameters(String analysisResult, String toolName) {
        try {
            // 尝试解析JSON格式
            if (analysisResult.contains("{") && analysisResult.contains("}")) {
                // 简单的JSON解析，实际项目中建议使用Jackson等JSON库
                if (analysisResult.contains("\"" + toolName + "\"")) {
                    // 提取对应工具的参数部分
                    int toolIndex = analysisResult.indexOf("\"" + toolName + "\"");
                    if (toolIndex != -1) {
                        // 简化实现，返回基本参数
                        Map<String, Object> params = new HashMap<>();
                        params.put("analysis", analysisResult);
                        params.put("tool", toolName);
                        return params;
                    }
                }
            }
        } catch (Exception e) {
            logger.warn("解析工具参数失败，使用默认参数", e);
        }

        // 默认参数
        Map<String, Object> defaultParams = new HashMap<>();
        defaultParams.put("action", "execute");
        defaultParams.put("context", analysisResult);
        return defaultParams;
    }

    /**
     * 构建最终整合提示词
     */
    private String buildFinalPrompt(String originalPrompt, String analysisResult, Map<String, Object> toolResults) {
        StringBuilder sb = new StringBuilder();
        sb.append("请基于以下信息，回答用户的原始问题。\n\n");

        sb.append("用户原始问题: ").append(originalPrompt).append("\n\n");

        sb.append("任务分析结果: ").append(analysisResult).append("\n\n");

        sb.append("工具执行结果:\n");
        for (Map.Entry<String, Object> entry : toolResults.entrySet()) {
            sb.append("- ").append(entry.getKey()).append(": ").append(entry.getValue()).append("\n");
        }

        sb.append("\n请基于以上所有信息，给出专业、友好的回答。如果工具执行失败，请说明原因并提供替代建议。");

        return sb.toString();
    }

    /**
     * 检查MCP服务状态
     */
    public Map<String, Object> getMCPStatus() {
        if (mcpIntegrationService == null) {
            return Map.of("status", "unavailable", "message", "MCP集成服务未启用");
        }

        try {
            return mcpIntegrationService.getMCPStatus();
        } catch (Exception e) {
            return Map.of("status", "error", "message", e.getMessage());
        }
    }
}


