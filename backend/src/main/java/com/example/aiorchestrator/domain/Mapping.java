package com.example.aiorchestrator.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "mappings")
public class Mapping {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "user_id")
    private User user; // 可为 null → 所有用户

    @ManyToOne
    @JoinColumn(name = "application_id")
    private ApplicationEntity application; // 可为 null → 所有应用

    @ManyToOne(optional = false)
    @JoinColumn(name = "gesture_id")
    private Gesture gesture;

    @ManyToOne(optional = false)
    @JoinColumn(name = "action_id")
    private ActionEntity action;

    private Integer priority = 0;

    private Boolean enabled = Boolean.TRUE;

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

    public Integer getPriority() { return priority; }
    public void setPriority(Integer priority) { this.priority = priority; }

    public Boolean getEnabled() { return enabled; }
    public void setEnabled(Boolean enabled) { this.enabled = enabled; }
}


