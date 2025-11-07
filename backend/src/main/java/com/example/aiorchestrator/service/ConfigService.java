package com.example.aiorchestrator.service;

import com.example.aiorchestrator.dto.ActionConfigDto;
import com.example.aiorchestrator.dto.ConfigMappingRow;
import com.example.aiorchestrator.dto.ConfigResponseDto;
import com.example.aiorchestrator.dto.GestureConfigDto;
import com.example.aiorchestrator.mapper.ConfigMapper;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class ConfigService {

    private final ConfigMapper configMapper;

    public ConfigService(ConfigMapper configMapper) {
        this.configMapper = configMapper;
    }

    public ConfigResponseDto fetchConfig(String username, String applicationCode, String osType) {
        String normalizedOs = StringUtils.hasText(osType) ? osType.toLowerCase() : "any";

        List<ConfigMappingRow> rows = configMapper.selectConfigMappings(
                StringUtils.hasText(username) ? username : null,
                StringUtils.hasText(applicationCode) ? applicationCode : null,
                normalizedOs
        );

        Map<String, GestureConfigDto> gestureMap = new LinkedHashMap<>();
        for (ConfigMappingRow row : rows) {
            gestureMap.computeIfAbsent(row.getGestureCode(), code -> {
                GestureConfigDto gesture = new GestureConfigDto();
                gesture.setCode(code);
                gesture.setName(row.getGestureName());
                gesture.setType(row.getGestureType());
                return gesture;
            });

            GestureConfigDto gesture = gestureMap.get(row.getGestureCode());
            if (gesture.getAction() == null) {
                ActionConfigDto action = new ActionConfigDto();
                action.setType(row.getActionType());
                action.setValue(row.getActionValue());
                action.setOsType(row.getOsType());
                action.setDescription(row.getActionDescription());
                action.setPayloadJson(row.getActionPayloadJson());
                gesture.setAction(action);
            }
        }

        ConfigResponseDto response = new ConfigResponseDto();
        response.setUsername(username);
        response.setApplication(applicationCode);
        response.setOsType(normalizedOs);
        response.setMappings(new ArrayList<>(gestureMap.values()));
        return response;
    }
}


