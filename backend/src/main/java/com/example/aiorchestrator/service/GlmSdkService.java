package com.example.aiorchestrator.service;

import ai.z.openapi.ZhipuAiClient;
import ai.z.openapi.service.model.*;
import ai.z.openapi.core.Constants;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.function.Consumer;

/**
 * GLM 官方 SDK 服务
 * 提供类型安全和高性能的 GLM API 集成
 */
@Service
public class GlmSdkService {

    private static final Logger logger = LoggerFactory.getLogger(GlmSdkService.class);

    @Value("${ai.llm.glm.api-key}")
    private String apiKey;

    @Value("${ai.llm.glm.model}")
    private String model;

    private ZhipuAiClient client;

    /**
     * 初始化 GLM 客户端
     */
    private ZhipuAiClient getClient() {
        if (client == null) {
            logger.info("初始化GLM客户端，Model: {}", model);
            logger.info("API Key: {}", apiKey != null ? apiKey.substring(0, Math.min(10, apiKey.length())) + "***" : "null");

            client = ZhipuAiClient.builder()
                    .apiKey(apiKey)
                    .build();
        }
        return client;
    }

    /**
     * 基础对话功能
     */
    public String chat(String message) {
        logger.info("开始GLM SDK对话，Message: {}", message);

        try {
            ZhipuAiClient client = getClient();

            // 构建对话请求
            ChatCompletionCreateParams request = ChatCompletionCreateParams.builder()
                    .model(model)
                    .messages(Arrays.asList(
                            ChatMessage.builder()
                                    .role(ChatMessageRole.USER.value())
                                    .content(message)
                                    .build()
                    ))
                    .temperature(0.7f)
                    .maxTokens(4000)
                    .build();

            logger.info("发送GLM SDK请求: {}", request);

            // 发送请求
            ChatCompletionResponse response = client.chat().createChatCompletion(request);

            logger.info("GLM SDK响应状态: {}", response.isSuccess());
            if (!response.isSuccess()) {
                logger.error("GLM SDK错误: {}", response.getMsg());
                return "GLM SDK错误: " + response.getMsg();
            }

            // 解析响应
            String reply = response.getData().getChoices().get(0).getMessage().getContent().toString();
            logger.info("GLM SDK回复成功: {}", reply);

            return reply;

        } catch (Exception e) {
            logger.error("GLM SDK调用失败", e);
            return "GLM SDK调用失败: " + e.getMessage();
        }
    }

    /**
     * 多轮对话
     */
    public String chatWithHistory(String message, List<Map<String, String>> conversationHistory) {
        logger.info("开始GLM SDK多轮对话，当前消息: {}", message);
        logger.info("对话历史长度: {}", conversationHistory != null ? conversationHistory.size() : 0);

        try {
            ZhipuAiClient client = getClient();

            // 构建消息列表
            List<ChatMessage> messages = new ArrayList<>();

            // 添加系统消息
            messages.add(ChatMessage.builder()
                    .role(ChatMessageRole.SYSTEM.value())
                    .content("你是YOLO-LLM平台的智能助手，专门帮助用户进行手势控制和语音交互。")
                    .build());

            // 添加历史消息
            if (conversationHistory != null) {
                for (Map<String, String> historyMsg : conversationHistory) {
                    String role = historyMsg.get("role");
                    String content = historyMsg.get("content");

                    if (role != null && content != null) {
                        messages.add(ChatMessage.builder()
                                .role(role)
                                .content(content)
                                .build());
                    }
                }
            }

            // 添加当前用户消息
            messages.add(ChatMessage.builder()
                    .role(ChatMessageRole.USER.value())
                    .content(message)
                    .build());

            // 构建请求
            ChatCompletionCreateParams request = ChatCompletionCreateParams.builder()
                    .model(model)
                    .messages(messages)
                    .temperature(0.7f)
                    .maxTokens(4000)
                    .build();

            logger.info("发送GLM SDK多轮对话请求，消息数量: {}", messages.size());

            // 发送请求
            ChatCompletionResponse response = client.chat().createChatCompletion(request);

            logger.info("GLM SDK多轮对话响应状态: {}", response.isSuccess());
            if (!response.isSuccess()) {
                logger.error("GLM SDK多轮对话错误: {}", response.getMsg());
                return "GLM SDK多轮对话错误: " + response.getMsg();
            }

            // 解析响应
            String reply = response.getData().getChoices().get(0).getMessage().getContent().toString();
            logger.info("GLM SDK多轮对话回复成功: {}", reply);

            return reply;

        } catch (Exception e) {
            logger.error("GLM SDK多轮对话调用失败", e);
            return "GLM SDK多轮对话调用失败: " + e.getMessage();
        }
    }

    /**
     * 流式对话（异步）- 暂时简化实现
     * TODO: 后续可以升级SDK版本支持完整的流式功能
     */
    public void streamingChat(String message,
                             Consumer<ChatCompletionResponse> onMessage,
                             Consumer<Throwable> onError,
                             Runnable onComplete) {
        logger.info("开始GLM SDK流式对话，Message: {}", message);

        try {
            // 目前简化为同步调用，后续升级SDK版本后支持真正的流式
            String response = chat(message);

            // 模拟流式响应（临时方案）
            ChatCompletionResponse mockResponse = new ChatCompletionResponse();
            mockResponse.setSuccess(true);

            onMessage.accept(mockResponse);
            onComplete.run();

        } catch (Exception e) {
            logger.error("GLM SDK流式对话调用失败", e);
            onError.accept(e);
        }
    }

    /**
     * 手势意图分析
     */
    public String analyzeGesture(String gestureCode, Double confidence, String context, String basePrompt) {
        logger.info("开始GLM SDK手势分析，Gesture: {}, Confidence: {}", gestureCode, confidence);

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

        return chat(promptBuilder.toString());
    }

    /**
     * 语音命令分析
     */
    public String analyzeVoiceCommand(String command, String context) {
        logger.info("开始GLM SDK语音命令分析，Command: {}", command);

        StringBuilder promptBuilder = new StringBuilder();
        promptBuilder.append("你是一个智能语音助手分析专家。\n\n");
        promptBuilder.append("用户语音命令: ").append(command).append("\n");

        if (context != null && !context.trim().isEmpty()) {
            promptBuilder.append("上下文: ").append(context).append("\n");
        }

        promptBuilder.append("\n请分析这个语音命令的意图，并提供适当的回应。");
        promptBuilder.append("如果这是控制命令，请确认并反馈执行结果。");
        promptBuilder.append("如果是查询或对话，请给出专业、友好的回答。");

        return chat(promptBuilder.toString());
    }

    /**
     * 智能对话助手
     */
    public String intelligentChat(String message, String context, String conversationHistory) {
        logger.info("开始GLM SDK智能对话，Message: {}", message);

        StringBuilder promptBuilder = new StringBuilder();
        promptBuilder.append("你是YOLO-LLM平台的智能助手，专门帮助用户进行手势控制和语音交互。\n\n");

        if (conversationHistory != null && !conversationHistory.trim().isEmpty()) {
            promptBuilder.append("对话历史:\n").append(conversationHistory).append("\n\n");
        }

        promptBuilder.append("当前用户消息: ").append(message).append("\n");

        if (context != null && !context.trim().isEmpty()) {
            promptBuilder.append("上下文: ").append(context).append("\n");
        }

        promptBuilder.append("\n请给出专业、友好、有帮助的回应。");

        return chat(promptBuilder.toString());
    }
}