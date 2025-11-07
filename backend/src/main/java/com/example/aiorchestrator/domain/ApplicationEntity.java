package com.example.aiorchestrator.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

@TableName("applications")
public class ApplicationEntity {
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    @TableField(value = "code")
    private String code; // 如 chrome.exe

    @TableField(value = "name")
    private String name; // 展示名称

    private String description;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
}


