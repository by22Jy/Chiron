package com.example.aiorchestrator.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.stereotype.Service;
import org.springframework.util.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.util.UriUtils;

import java.nio.charset.StandardCharsets;
import java.util.*;

@Service
public class AiOrchestratorService {

    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${ai.yolo.url-detect-file}") private String yoloDetectFileUrl;
    @Value("${ai.yolo.url-detect-url}")  private String yoloDetectUrlUrl;

    @Value("${ai.llm.provider}") private String provider;
    @Value("${ai.llm.kimi.api-url}") private String kimiUrl;
    @Value("${ai.llm.kimi.api-key}") private String kimiKey;
    @Value("${ai.llm.kimi.model}")  private String kimiModel;

    @Value("${ai.llm.qwen.api-url}") private String qwenUrl;
    @Value("${ai.llm.qwen.api-key}") private String qwenKey;
    @Value("${ai.llm.qwen.model}")  private String qwenModel;

    public String orchestrate(MultipartFile image, String question) {
        List<String> objects = callYoloWithFile(image);
        String prompt = buildPrompt(objects, question);
        return callLlm(prompt);
    }

    public String orchestrateByUrl(String imageUrl, String question) {
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
        } else {
            return callOpenAICompat(qwenUrl, qwenKey, qwenModel, prompt);
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

    @SuppressWarnings("unchecked")
    private String parseOpenAIStyle(Map body) {
        try {
            var choices = (List<Map<String, Object>>) body.get("choices");
            if (choices == null || choices.isEmpty()) return "LLM无结果";
            var msg = (Map<String, Object>) choices.get(0).get("message");
            return msg.getOrDefault("content", "").toString();
        } catch (Exception e) { return "解析失败: " + e.getMessage(); }
    }
}


