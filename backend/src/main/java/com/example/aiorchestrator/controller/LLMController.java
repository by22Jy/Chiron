package com.example.aiorchestrator.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * LLM智能分析控制器
 */
@RestController
@RequestMapping("/api/llm")
@CrossOrigin(origins = {"http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"}, allowCredentials = "true")
public class LLMController {

    private static final Logger logger = LoggerFactory.getLogger(LLMController.class);

    @Autowired
    private com.example.aiorchestrator.service.AiOrchestratorService aiOrchestratorService;

    /**
     * 手势意图分析
     */
    @PostMapping("/gesture-analysis")
    public ResponseEntity<Map<String, Object>> analyzeGesture(
            @RequestBody Map<String, Object> request) {

        String prompt = (String) request.get("prompt");
        String gestureCode = (String) request.get("gesture_code");
        Double confidence = (Double) request.get("confidence");
        String context = (String) request.get("context");

        try {
            // 构建完整的分析提示词
            String fullPrompt = buildGestureAnalysisPrompt(prompt, gestureCode, confidence, context);

            // 调用LLM进行分析
            String llmResponse = aiOrchestratorService.orchestrateByUrl("", fullPrompt);

            // 解析LLM响应
            Map<String, Object> response = parseGestureAnalysisResponse(llmResponse);

            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("response", llmResponse);
            result.put("analysis", response);
            result.put("gesture_code", gestureCode);
            result.put("timestamp", System.currentTimeMillis());

            return ResponseEntity.ok(result);

        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("response", "手势分析暂时不可用，请稍后重试");

            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 语音命令分析
     */
    @PostMapping("/voice-command")
    public ResponseEntity<Map<String, Object>> analyzeVoiceCommand(
            @RequestBody Map<String, Object> request) {

        String command = (String) request.get("command");
        String context = (String) request.get("context");

        try {
            logger.info("收到语音命令: {}, 上下文: {}", command, context);

            // 使用智能编排服务，包含MCP工具支持
            List<String> requiredTools = List.of("news", "weather", "deepseek_llm", "task_management");
            String response = aiOrchestratorService.orchestrateWithMCP(command, requiredTools);

            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("response", response);
            result.put("command", command);
            result.put("timestamp", System.currentTimeMillis());

            logger.info("语音命令分析完成，响应: {}", response);

            return ResponseEntity.ok(result);

        } catch (Exception e) {
            logger.error("语音命令分析失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("response", "语音命令分析失败，请稍后重试");

            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 智能对话
     */
    @PostMapping("/chat")
    public ResponseEntity<Map<String, Object>> chat(
            @RequestBody Map<String, Object> request) {

        logger.info("收到聊天请求: {}", request);

        String message = (String) request.get("message");
        String context = (String) request.get("context");
        String conversationHistory = (String) request.get("history");

        logger.info("提取参数 - Message: {}, Context: {}, History: {}", message, context, conversationHistory);

        try {
            // 构建对话提示词
            String prompt = buildChatPrompt(message, context, conversationHistory);
            logger.info("构建的提示词: {}", prompt);

            // 调用LLM进行对话
            String llmResponse = aiOrchestratorService.orchestrateByUrl("", prompt);
            logger.info("LLM响应: {}", llmResponse);

            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("response", llmResponse);
            result.put("timestamp", System.currentTimeMillis());

            logger.info("成功响应: {}", result);
            return ResponseEntity.ok(result);

        } catch (Exception e) {
            logger.error("聊天处理失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("response", "智能对话暂时不可用");

            logger.info("错误响应: {}", errorResponse);
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 智能编排接口 - 支持MCP工具调用
     */
    @PostMapping("/intelligent")
    public ResponseEntity<Map<String, Object>> intelligentOrchestrate(
            @RequestBody Map<String, Object> request) {

        logger.info("收到智能编排请求: {}", request);

        String message = (String) request.get("message");
        String context = (String) request.get("context");

        try {
            // 获取可用的MCP工具
            Map<String, Object> mcpStatus = aiOrchestratorService.getMCPStatus();
            List<String> availableTools = (List<String>) mcpStatus.get("available_tools");

            logger.info("可用MCP工具: {}", availableTools);

            // 构建智能编排提示词，包含MCP工具信息
            String intelligentPrompt = buildIntelligentPrompt(message, context, availableTools);
            logger.info("智能编排提示词: {}", intelligentPrompt);

            // 调用带MCP工具的LLM编排
            String llmResponse = aiOrchestratorService.orchestrateWithMCP(intelligentPrompt, availableTools);
            logger.info("智能编排响应: {}", llmResponse);

            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("response", llmResponse);
            result.put("tools_used", availableTools);
            result.put("mcp_status", mcpStatus);
            result.put("timestamp", System.currentTimeMillis());

            logger.info("智能编排成功: {}", result);
            return ResponseEntity.ok(result);

        } catch (Exception e) {
            logger.error("智能编排失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("response", "智能编排暂时不可用");
            errorResponse.put("fallback_used", true);

            // 回退到普通LLM调用
            try {
                String fallbackPrompt = buildChatPrompt(message, context, "");
                String fallbackResponse = aiOrchestratorService.orchestrateByUrl("", fallbackPrompt);
                errorResponse.put("fallback_response", fallbackResponse);
            } catch (Exception fallbackEx) {
                logger.error("回退调用也失败", fallbackEx);
                errorResponse.put("fallback_response", "所有LLM服务不可用");
            }

            logger.info("智能编排错误响应: {}", errorResponse);
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 构建智能编排提示词
     */
    private String buildIntelligentPrompt(String message, String context, List<String> availableTools) {
        StringBuilder prompt = new StringBuilder();

        prompt.append("你是一个专业的AI智能助手，能够理解用户意图并使用各种工具来完成任务。\n\n");

        prompt.append("用户请求: ").append(message).append("\n");
        if (context != null && !context.isEmpty()) {
            prompt.append("上下文: ").append(context).append("\n");
        }

        prompt.append("\n可用工具:\n");
        for (String tool : availableTools) {
            prompt.append("- ").append(tool).append("\n");
        }

        prompt.append("\n工具说明:\n");
        prompt.append("- news: 获取最新新闻资讯\n");
        prompt.append("- weather: 查询天气信息\n");
        prompt.append("- email: 发送邮件\n");
        prompt.append("- computer_control: 控制电脑操作\n");
        prompt.append("- filesystem: 文件系统操作\n");
        prompt.append("- system_health: 系统健康检查\n");
        prompt.append("- voice_control: 语音控制\n");
        prompt.append("- social_media: 社交媒体操作\n");
        prompt.append("- deepseek_llm: 深度思考和推理\n");

        prompt.append("\n请分析用户的请求，如果需要使用工具，请明确说明使用哪个工具以及具体参数。");
        prompt.append("如果不需要工具，请直接回答用户问题。");
        prompt.append("请用中文回答，内容要详细、有用、有条理。");

        return prompt.toString();
    }

    /**
     * 构建手势分析提示词
     */
    private String buildGestureAnalysisPrompt(String basePrompt, String gestureCode,
                                              Double confidence, String context) {
        StringBuilder promptBuilder = new StringBuilder();

        promptBuilder.append("你是一个专业的人类行为和手势分析专家。\n\n");
        promptBuilder.append(basePrompt).append("\n\n");

        if (gestureCode != null) {
            promptBuilder.append("手势代码: ").append(gestureCode.toUpperCase()).append("\n");
        }

        if (confidence != null) {
            promptBuilder.append("识别置信度: ").append(String.format("%.2f", confidence)).append("\n");
        }

        if (context != null && !context.trim().isEmpty()) {
            promptBuilder.append("上下文: ").append(context).append("\n");
        }

        promptBuilder.append("\n请提供专业、友好、有建设性的分析。");

        return promptBuilder.toString();
    }

    /**
     * 构建语音命令分析提示词
     */
    private String buildVoiceCommandPrompt(String command, String context) {
        StringBuilder promptBuilder = new StringBuilder();

        promptBuilder.append("你是一个智能语音助手分析专家。\n\n");
        promptBuilder.append("用户语音命令: ").append(command).append("\n");

        if (context != null && !context.trim().isEmpty()) {
            promptBuilder.append("上下文: ").append(context).append("\n");
        }

        promptBuilder.append("\n请分析这个语音命令的意图，并提供适当的回应。");
        promptBuilder.append("如果这是控制命令，请确认并反馈执行结果。");
        promptBuilder.append("如果是查询或对话，请给出专业、友好的回答。");

        return promptBuilder.toString();
    }

    /**
     * 构建对话提示词
     */
    private String buildChatPrompt(String message, String context, String history) {
        StringBuilder promptBuilder = new StringBuilder();

        promptBuilder.append("你是YOLO-LLM平台的智能助手，专门帮助用户进行手势控制和语音交互。\n\n");

        if (history != null && !history.trim().isEmpty()) {
            promptBuilder.append("对话历史:\n").append(history).append("\n\n");
        }

        promptBuilder.append("当前用户消息: ").append(message).append("\n");

        if (context != null && !context.trim().isEmpty()) {
            promptBuilder.append("上下文: ").append(context).append("\n");
        }

        promptBuilder.append("\n请给出专业、友好、有帮助的回应。");

        return promptBuilder.toString();
    }

    /**
     * 解析手势分析响应
     */
    private Map<String, Object> parseGestureAnalysisResponse(String response) {
        Map<String, Object> analysis = new HashMap<>();

        // 简单的关键词提取（实际应用中可能需要更复杂的NLP处理）
        String[] lines = response.split("\n");

        for (String line : lines) {
            line = line.trim();

            if (line.contains("意图") || line.contains("目的")) {
                analysis.put("intent", line);
            } else if (line.contains("情感") || line.contains("情绪")) {
                analysis.put("emotion", line);
            } else if (line.contains("社交") || line.contains("含义")) {
                analysis.put("social_meaning", line);
            } else if (line.contains("建议") || line.contains("可以")) {
                String existing = (String) analysis.getOrDefault("suggestions", "");
                analysis.put("suggestions", existing + (existing.isEmpty() ? "" : "\n") + line);
            }
        }

        // 如果没有提取到特定信息，使用完整响应
        if (analysis.isEmpty()) {
            analysis.put("full_analysis", response);
        }

        return analysis;
    }
}