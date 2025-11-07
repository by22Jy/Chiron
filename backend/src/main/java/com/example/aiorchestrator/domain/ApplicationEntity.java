package com.example.aiorchestrator.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "applications")
public class ApplicationEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false)
    private String appName; // 如 chrome.exe

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getAppName() { return appName; }
    public void setAppName(String appName) { this.appName = appName; }
}


