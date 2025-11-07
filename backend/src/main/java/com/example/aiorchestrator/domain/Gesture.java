package com.example.aiorchestrator.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "gestures")
public class Gesture {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false, unique = true)
    private String code; // 如 swipe_left, pinch_close

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }
}


