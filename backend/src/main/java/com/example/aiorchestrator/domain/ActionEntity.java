package com.example.aiorchestrator.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

@TableName("actions")
public class ActionEntity {
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    @TableField("os_type")
    private String osType; // windows / macos / linux / any

    @TableField("action_type")
    private String type; // hotkey, keypress, mousemove, webhook

    @TableField("action_value")
    private String value; // 如 "ctrl+-"、"command+option+left"

    private String description;

    @TableField("payload_json")
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


