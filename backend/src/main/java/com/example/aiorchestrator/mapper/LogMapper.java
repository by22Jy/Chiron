package com.example.aiorchestrator.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.aiorchestrator.domain.LogEntry;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface LogMapper extends BaseMapper<LogEntry> {
}


