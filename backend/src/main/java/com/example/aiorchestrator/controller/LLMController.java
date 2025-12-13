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

    @Autowired
    private com.example.aiorchestrator.util.DataFormatStandardizer dataStandardizer;

    /**
     * 手势意图分析
     */
    @PostMapping("/gesture-analysis")
    public ResponseEntity<Map<String, Object>> analyzeGesture(
            @RequestBody Map<String, Object> request) {

        try {
            // 验证请求格式
            Map<String, Object> validation = dataStandardizer.validateRequestFormat(request);
            if (!(Boolean) validation.get("valid")) {
                Map<String, Object> errorResponse = dataStandardizer.standardizeErrorResponse(
                    new IllegalArgumentException("请求格式无效: " + validation.get("errors")),
                    "请求格式验证失败"
                );
                return ResponseEntity.status(400).body(errorResponse);
            }

            String prompt = (String) request.get("prompt");
            String gestureCode = (String) request.get("gesture_code");
            Double confidence = (Double) request.get("confidence");
            String context = (String) request.get("context");

            // 标准化枚举值
            if (gestureCode != null) {
                gestureCode = dataStandardizer.standardizeEnumValue(gestureCode, "gesture_name");
            }

            // 构建完整的分析提示词
            String fullPrompt = buildGestureAnalysisPrompt(prompt, gestureCode, confidence, context);

            // 调用LLM进行分析
            String llmResponse = aiOrchestratorService.orchestrateByUrl("", fullPrompt);

            // 解析LLM响应
            Map<String, Object> response = parseGestureAnalysisResponse(llmResponse);

            // 构建旧格式响应（保持向后兼容）
            Map<String, Object> oldFormatResponse = new HashMap<>();
            oldFormatResponse.put("success", true);
            oldFormatResponse.put("response", llmResponse);
            oldFormatResponse.put("analysis", response);
            oldFormatResponse.put("gesture_code", gestureCode);
            oldFormatResponse.put("timestamp", System.currentTimeMillis());

            // 标准化为新格式
            Map<String, Object> standardResponse = dataStandardizer.standardizeResponse(
                oldFormatResponse,
                "success",
                "手势分析完成"
            );

            return ResponseEntity.ok(standardResponse);

        } catch (Exception e) {
            logger.error("手势分析失败", e);
            Map<String, Object> errorResponse = dataStandardizer.standardizeErrorResponse(
                e,
                "手势分析暂时不可用，请稍后重试"
            );
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * 语音命令分析
     */
    @PostMapping("/voice-command")
    public ResponseEntity<Map<String, Object>> analyzeVoiceCommand(
            @RequestBody Map<String, Object> request) {

        try {
            // 验证请求格式
            Map<String, Object> validation = dataStandardizer.validateRequestFormat(request);
            if (!(Boolean) validation.get("valid")) {
                Map<String, Object> errorResponse = dataStandardizer.standardizeErrorResponse(
                    new IllegalArgumentException("请求格式无效: " + validation.get("errors")),
                    "请求格式验证失败"
                );
                return ResponseEntity.status(400).body(errorResponse);
            }

            String command = (String) request.get("command");
            String context = (String) request.get("context");

            logger.info("收到语音命令: {}, 上下文: {}", command, context);

            // 使用智能编排服务，包含MCP工具支持
            List<String> requiredTools = List.of("news", "weather", "deepseek_llm", "task_management");
            String response = aiOrchestratorService.orchestrateWithMCP(command, requiredTools);

            // 构建旧格式响应（保持向后兼容）
            Map<String, Object> oldFormatResponse = new HashMap<>();
            oldFormatResponse.put("success", true);
            oldFormatResponse.put("response", response);
            oldFormatResponse.put("command", command);
            oldFormatResponse.put("timestamp", System.currentTimeMillis());

            // 标准化为新格式
            Map<String, Object> standardResponse = dataStandardizer.standardizeResponse(
                oldFormatResponse,
                "success",
                "语音命令分析完成"
            );

            logger.info("语音命令分析完成，响应: {}", response);

            return ResponseEntity.ok(standardResponse);

        } catch (Exception e) {
            logger.error("语音命令分析失败", e);
            Map<String, Object> errorResponse = dataStandardizer.standardizeErrorResponse(
                e,
                "语音命令分析失败，请稍后重试"
            );

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

        String message;
        String context;

        // 处理新的结构化用户意图数据
        if (request.containsKey("user_intent")) {
            Map<String, Object> userIntent = (Map<String, Object>) request.get("user_intent");
            message = (String) userIntent.get("user_input");
            context = (String) userIntent.get("context");

            // 添加系统信息到上下文
            Map<String, Object> systemInfo = (Map<String, Object>) userIntent.get("system_info");
            if (systemInfo != null) {
                context += String.format(" [系统信息: CPU=%s, 内存=%.1fGB, 平台=%s]",
                    systemInfo.get("cpu_count"),
                    ((Number) systemInfo.get("memory_total")).longValue() / (1024.0 * 1024 * 1024),
                    systemInfo.get("platform"));
            }

            // 添加已安装应用信息
            List<String> installedApps = (List<String>) userIntent.get("installed_apps");
            if (installedApps != null && !installedApps.isEmpty()) {
                context += " [已安装应用: " + String.join(", ", installedApps.subList(0, Math.min(10, installedApps.size()))) + "]";
            }

            logger.info("解析用户意图: {}, 增强上下文: {}", message, context);
        } else {
            // 兼容旧的message格式
            message = (String) request.get("message");
            context = (String) request.get("context");
        }

        try {
            // 获取可用的MCP工具
            Map<String, Object> mcpStatus = aiOrchestratorService.getMCPStatus();
            List<String> availableTools = (List<String>) mcpStatus.get("available_tools");

            logger.info("可用MCP工具: {}", availableTools);

            // 构建智能编排提示词，包含MCP工具信息和电脑控制指令
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

        // 系统指令 - 电脑控制智能分析
        prompt.append("你是一个专业的电脑控制AI智能助手，能够理解自然语言命令并生成精确的电脑操作指令。\n\n");

        prompt.append("你的任务是分析用户的自然语言请求，并返回JSON格式的电脑操作指令。\n\n");

        prompt.append("支持的 action_type 类型:\n");
        prompt.append("- open_app: 打开应用程序\n");
        prompt.append("- system_control: 系统控制（音量、亮度、关机等）\n");
        prompt.append("- file_operation: 文件操作（打开文件夹、文件管理等）\n");
        prompt.append("- web_search: 网页搜索\n");
        prompt.append("- custom_command: 自定义命令\n\n");

        prompt.append("响应格式要求:\n");
        prompt.append("必须返回严格的JSON格式，包含以下字段：\n");
        prompt.append("{\n");
        prompt.append("  \"action_type\": \"操作类型\",\n");
        prompt.append("  \"command\": \"具体要执行的命令\",\n");
        prompt.append("  \"description\": \"操作描述\",\n");
        prompt.append("  \"confidence\": 0.95,\n");
        prompt.append("  \"safety_level\": \"safe\",\n");
        prompt.append("  \"alternatives\": [\"备选方案1\", \"备选方案2\"]\n");
        prompt.append("}\n\n");

        prompt.append("安全级别说明:\n");
        prompt.append("- safe: 安全操作，可以直接执行\n");
        prompt.append("- warning: 需要注意的操作，建议确认\n");
        prompt.append("- dangerous: 危险操作，必须用户确认\n\n");

        prompt.append("用户请求: ").append(message).append("\n");
        if (context != null && !context.isEmpty()) {
            prompt.append("上下文: ").append(context).append("\n");
        }

        prompt.append("\n可用MCP工具:\n");
        for (String tool : availableTools) {
            prompt.append("- ").append(tool).append("\n");
        }

        prompt.append("\n分析说明:\n");
        prompt.append("1. 仔细分析用户意图，选择最合适的 action_type\n");
        prompt.append("2. 生成具体可执行的 command\n");
        prompt.append("3. 提供清晰的中文 description\n");
        prompt.append("4. 设置合理的 confidence (0.0-1.0)\n");
        prompt.append("5. 评估 safety_level\n");
        prompt.append("6. 如有其他可行方案，提供 alternatives\n\n");

        prompt.append("请返回JSON格式的电脑操作指令:");

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