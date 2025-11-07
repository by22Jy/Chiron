package com.example.aiorchestrator.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "gestures")
public class Gesture {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String code; // 如 swipe_left, pinch_close

    private String name;

    private String description;

    @Column(name = "gesture_type")
    private String type; // static / dynamic / pose

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
}


