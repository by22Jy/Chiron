package com.example.aiorchestrator.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "actions")
public class ActionEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "os_type", nullable = false)
    private String osType; // windows / macos / linux / any

    @Column(name = "action_type", nullable = false)
    private String type; // hotkey, keypress, mousemove, webhook

    @Column(name = "action_value", nullable = false)
    private String value; // 如 "ctrl+-"、"command+option+left"

    private String description;

    @Column(name = "payload_json")
    private String payloadJson; // 可选 JSON（宏脚本等）

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getOsType() { return osType; }
    public void setOsType(String osType) { this.osType = osType; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public String getValue() { return value; }
    public void setValue(String value) { this.value = value; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getPayloadJson() { return payloadJson; }
    public void setPayloadJson(String payloadJson) { this.payloadJson = payloadJson; }
}


