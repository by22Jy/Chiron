package com.example.aiorchestrator.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "mappings")
public class Mapping {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(optional = false) private User user;
    @ManyToOne(optional = false) private ApplicationEntity application;
    @ManyToOne(optional = false) private Gesture gesture;
    @ManyToOne(optional = false) private ActionEntity action;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }
    public ApplicationEntity getApplication() { return application; }
    public void setApplication(ApplicationEntity application) { this.application = application; }
    public Gesture getGesture() { return gesture; }
    public void setGesture(Gesture gesture) { this.gesture = gesture; }
    public ActionEntity getAction() { return action; }
    public void setAction(ActionEntity action) { this.action = action; }
}


