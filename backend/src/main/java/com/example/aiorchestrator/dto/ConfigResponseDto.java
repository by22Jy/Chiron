package com.example.aiorchestrator.dto;

import java.util.List;

public class ConfigResponseDto {
    private String username;
    private String application;
    private String osType;
    private List<GestureConfigDto> mappings;

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

    public String getOsType() {
        return osType;
    }

    public void setOsType(String osType) {
        this.osType = osType;
    }

    public List<GestureConfigDto> getMappings() {
        return mappings;
    }

    public void setMappings(List<GestureConfigDto> mappings) {
        this.mappings = mappings;
    }
}


