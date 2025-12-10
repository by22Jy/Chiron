package com.example.aiorchestrator.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.example.aiorchestrator.domain.ApplicationEntity;
import com.example.aiorchestrator.domain.LogEntry;
import com.example.aiorchestrator.domain.User;
import com.example.aiorchestrator.dto.LogRequest;
import com.example.aiorchestrator.mapper.ApplicationMapper;
import com.example.aiorchestrator.mapper.LogMapper;
import com.example.aiorchestrator.mapper.UserMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;

@Service
public class LogService {

    private static final Logger logger = LoggerFactory.getLogger(LogService.class);

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
        try {
            logger.info("记录日志: gestureCode={}, actionType={}",
                       request.getGestureCode(), request.getActionType());

            LogEntry entry = new LogEntry();

            // 安全处理用户ID解析
            try {
                entry.setUserId(resolveUserId(request.getUsername()));
            } catch (Exception e) {
                logger.warn("解析用户ID失败，使用null: {}", e.getMessage());
                entry.setUserId(null);
            }

            // 安全处理应用ID解析
            try {
                entry.setApplicationId(resolveApplicationId(request.getApplication()));
            } catch (Exception e) {
                logger.warn("解析应用ID失败，使用null: {}", e.getMessage());
                entry.setApplicationId(null);
            }

            entry.setGestureCode(request.getGestureCode());
            entry.setActionType(request.getActionType());
            entry.setActionValue(request.getActionValue());
            entry.setStatus(StringUtils.hasText(request.getStatus()) ? request.getStatus() : "success");
            entry.setMessage(request.getMessage());
            entry.setSourceAgent(request.getSourceAgent());
            entry.setCreatedAt(LocalDateTime.now());

            logMapper.insert(entry);
            logger.info("日志记录成功，ID={}", entry.getId());
            return entry.getId();

        } catch (Exception e) {
            logger.error("记录日志时发生错误: {}", e.getMessage(), e);
            throw new RuntimeException("日志记录失败: " + e.getMessage(), e);
        }
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


