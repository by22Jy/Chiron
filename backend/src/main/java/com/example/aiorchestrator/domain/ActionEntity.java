package com.example.aiorchestrator.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "actions")
public class ActionEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false)
    private String type; // hotkey, keypress, mousemove, custom
    @Column(nullable = false)
    private String value; // 如 "ctrl+-"、"left"

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    public String getValue() { return value; }
    public void setValue(String value) { this.value = value; }
}


