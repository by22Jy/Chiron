package com.example.aiorchestrator.mapper;

import com.example.aiorchestrator.dto.ConfigMappingRow;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface ConfigMapper {

    @Select({
            "<script>",
            "SELECT",
            "  g.code AS gesture_code,",
            "  g.name AS gesture_name,",
            "  g.gesture_type AS gesture_type,",
            "  act.action_type AS action_type,",
            "  act.action_value AS action_value,",
            "  act.os_type AS os_type,",
            "  act.description AS action_description,",
            "  act.payload_json AS action_payload_json,",
            "  m.priority AS priority",
            "FROM mappings m",
            "JOIN gestures g ON m.gesture_id = g.id",
            "JOIN actions act ON m.action_id = act.id",
            "LEFT JOIN users u ON m.user_id = u.id",
            "LEFT JOIN applications app ON m.application_id = app.id",
            "WHERE m.enabled = 1",
            "<if test='username != null and username != \"\"'>",
            "  AND (m.user_id IS NULL OR u.username = #{username})",
            "</if>",
            "<if test='applicationCode != null and applicationCode != \"\"'>",
            "  AND (m.application_id IS NULL OR app.code = #{applicationCode})",
            "</if>",
            "<if test='osType != null and osType != \"\"'>",
            "  AND (act.os_type = #{osType} OR act.os_type = 'any')",
            "</if>",
            "ORDER BY m.priority DESC,",
            "  CASE",
            "    WHEN act.os_type = #{osType} THEN 0",
            "    WHEN act.os_type = 'any' THEN 1",
            "    ELSE 2",
            "  END,",
            "  act.id",
            "</script>"
    })
    List<ConfigMappingRow> selectConfigMappings(@Param("username") String username,
                                                @Param("applicationCode") String applicationCode,
                                                @Param("osType") String osType);
}


