package com.example.aiorchestrator.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.example.aiorchestrator.domain.ApplicationEntity;
import com.example.aiorchestrator.domain.LogEntry;
import com.example.aiorchestrator.domain.User;
import com.example.aiorchestrator.dto.LogRequest;
import com.example.aiorchestrator.mapper.ApplicationMapper;
import com.example.aiorchestrator.mapper.LogMapper;
import com.example.aiorchestrator.mapper.UserMapper;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;

@Service
public class LogService {

    private final LogMapper logMapper;
    private final UserMapper userMapper;
    private final ApplicationMapper applicationMapper;

    public LogService(LogMapper logMapper,
                      UserMapper userMapper,
                      ApplicationMapper applicationMapper) {
        this.logMapper = logMapper;
        this.userMapper = userMapper;
        this.applicationMapper = applicationMapper;
    }

    public Long recordLog(LogRequest request) {
        LogEntry entry = new LogEntry();
        entry.setUserId(resolveUserId(request.getUsername()));
        entry.setApplicationId(resolveApplicationId(request.getApplication()));
        entry.setGestureCode(request.getGestureCode());
        entry.setActionType(request.getActionType());
        entry.setActionValue(request.getActionValue());
        entry.setStatus(StringUtils.hasText(request.getStatus()) ? request.getStatus() : "success");
        entry.setMessage(request.getMessage());
        entry.setSourceAgent(request.getSourceAgent());
        entry.setCreatedAt(LocalDateTime.now());
        logMapper.insert(entry);
        return entry.getId();
    }

    private Long resolveUserId(String username) {
        if (!StringUtils.hasText(username)) {
            return null;
        }
        User user = userMapper.selectOne(new LambdaQueryWrapper<User>()
                .eq(User::getUsername, username)
                .last("LIMIT 1"));
        return user != null ? user.getId() : null;
    }

    private Long resolveApplicationId(String applicationCode) {
        if (!StringUtils.hasText(applicationCode)) {
            return null;
        }
        ApplicationEntity app = applicationMapper.selectOne(new LambdaQueryWrapper<ApplicationEntity>()
                .eq(ApplicationEntity::getCode, applicationCode)
                .last("LIMIT 1"));
        return app != null ? app.getId() : null;
    }
}


