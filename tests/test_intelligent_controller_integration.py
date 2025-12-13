#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能控制器集成测试 - 验证JSON解析器集成
"""

import pytest
import sys
import os

# 添加agent目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agent'))

from intelligent_controller import IntelligentController


class TestIntelligentControllerIntegration:
    """智能控制器集成测试"""

    @pytest.fixture
    def controller(self):
        """智能控制器实例"""
        return IntelligentController()

    def test_parse_valid_llm_response_integration(self, controller):
        """测试解析有效的LLM响应集成"""
        valid_response = '''{
            "action": "open_app",
            "command": "notepad.exe",
            "confidence": 0.9,
            "description": "打开记事本应用程序"
        }'''

        result = controller._parse_llm_response(valid_response)

        assert result is not None
        assert result.action_type == "open_app"
        assert result.command == "notepad.exe"
        assert result.confidence == 0.9
        assert result.safety_level == "safe"

    def test_parse_malformed_response_with_parser(self, controller):
        """测试解析格式错误的响应使用新解析器"""
        malformed_response = '''Here's my analysis: {
            "action": "system_control",
            "command": "volume_up",
            "confidence": 0.85
        } The user wants to increase volume.'''

        result = controller._parse_llm_response(malformed_response)

        # 应该能够解析部分数据
        assert result is not None
        assert result.action_type == "system_control"
        assert result.command == "volume_up"
        assert result.confidence == 0.85

    def test_parse_completely_invalid_response(self, controller):
        """测试完全无效的响应处理"""
        invalid_response = "This is not JSON at all, just plain text response"

        result = controller._parse_llm_response(invalid_response)

        # 应该返回None，因为action会是"unknown"
        assert result is None

    def test_parse_empty_response(self, controller):
        """测试空响应处理"""
        result = controller._parse_llm_response("")

        assert result is None

    def test_parser_statistics_tracking(self, controller):
        """测试解析统计信息跟踪"""
        # 进行多次解析
        test_responses = [
            '{"action": "open_app", "command": "calc.exe"}',
            'malformed json with {"action": "test"',
            'completely invalid response'
        ]

        for response in test_responses:
            controller._parse_llm_response(response)

        # 检查统计信息
        stats = controller.json_parser.get_error_statistics()
        assert stats["total_attempts"] >= 3
        assert "success_rate" in stats
        assert stats["success_rate"] > 0  # 至少有一个成功的解析

    def test_action_type_mapping(self, controller):
        """测试动作类型映射"""
        test_cases = [
            ("open_app", "open_app"),
            ("system_control", "system_control"),
            ("unknown", "unknown"),
            ("invalid_action", "unknown"),
            ("OPEN_APP", "open_app"),  # 大写
        ]

        for input_action, expected_output in test_cases:
            result = controller._map_action_type(input_action)
            assert result == expected_output

    def test_safety_level_determination(self, controller):
        """测试安全级别确定"""
        # 测试安全级别
        safe_data = {"command": "open notepad", "confidence": 0.8}
        assert controller._determine_safety_level(safe_data) == "safe"

        # 测试警告级别 - 低置信度
        warning_data = {"command": "open file", "confidence": 0.3}
        assert controller._determine_safety_level(warning_data) == "warning"

        # 测试危险级别
        dangerous_data = {"command": "delete important_file.txt"}
        assert controller._determine_safety_level(dangerous_data) == "dangerous"

        # 测试警告级别 - 系统关键词
        system_data = {"command": "modify registry"}
        assert controller._determine_safety_level(system_data) == "warning"

    def test_error_handling_with_malformed_response(self, controller):
        """测试错误处理和异常捕获"""
        # 创建会导致异常的响应（例如编码问题）
        problematic_response = '{"action": "test\x00invalid", "command": "test"}'

        # 应该能够处理异常而不崩溃
        result = controller._parse_llm_response(problematic_response)
        # 应该返回None或默认处理结果，而不是抛出异常
        assert True  # 测试到达这里说明没有崩溃

    def test_confidence_calculation(self, controller):
        """测试置信度计算和响应质量评估"""
        high_confidence_response = '{"action": "open_app", "command": "chrome.exe", "confidence": 0.95}'
        result = controller._parse_llm_response(high_confidence_response)

        assert result is not None
        assert result.confidence == 0.95

        # 验证响应质量评估
        assert result.safety_level == "safe"  # 高置信度应该是安全的

    def test_backwards_compatibility(self, controller):
        """测试向后兼容性 - 确保旧的方法调用不会崩溃"""
        # 测试旧的_try_parse_json方法（现在应该委托给新解析器）
        legacy_result = controller._try_parse_json('{"action": "test"}')

        # 由于旧方法现在委托给新解析器，结果应该是有效的
        assert legacy_result is not None
        assert "action" in legacy_result

        # 测试旧的_fix_common_json_issues方法
        fixed_result = controller._fix_common_json_issues('test response')

        # 应该返回原始字符串（新方法中没有实际逻辑）
        assert fixed_result == 'test response'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])