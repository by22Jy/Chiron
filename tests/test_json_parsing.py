#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON解析器测试套件 - Task 5.1
测试各种格式错误的JSON解析情况
"""

import pytest
import json
import sys
import os

# 添加agent目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agent'))

from utils.json_parser import JSONResponseParser


class TestJSONResponseParser:
    """JSON响应解析器测试"""

    @pytest.fixture
    def parser(self):
        """JSON解析器实例"""
        return JSONResponseParser()

    def test_parse_valid_json_response(self, parser):
        """测试解析有效JSON响应"""
        valid_response = '''{
            "action": "open_app",
            "command": "notepad.exe",
            "confidence": 0.9,
            "description": "打开记事本"
        }'''

        result = parser.parse_response(valid_response)

        assert result is not None
        assert result["action"] == "open_app"
        assert result["command"] == "notepad.exe"
        assert result["confidence"] == 0.9
        assert "parsing_strategy" in result
        assert result["parsing_strategy"] == "standard"

    def test_parse_malformed_json_with_extra_characters(self, parser):
        """测试带有额外字符的错误JSON"""
        malformed_response = '''Here's my response: {
            "action": "open_app",
            "command": "chrome.exe",
            "confidence": 0.85
        } End of response.'''

        result = parser.parse_response(malformed_response)

        assert result is not None
        assert result["action"] == "open_app"
        assert result["command"] == "chrome.exe"
        assert "parsing_strategy" in result

    def test_parse_incomplete_json_missing_closing_brace(self, parser):
        """测试缺少结束括号的不完整JSON"""
        incomplete_response = '''{
            "action": "system_control",
            "command": "volume_up",
            "confidence": 0.95,
            "description": "调高音量"
        '''

        result = parser.parse_response(incomplete_response)

        # 应该能够解析部分数据
        assert result is not None
        assert "action" in result or "command" in result
        assert "parsing_strategy" in result

    def test_parse_response_with_unescaped_quotes(self, parser):
        """测试包含未转义引号的JSON"""
        problematic_response = '''{
            "action": "open_app",
            "command": "notepad.exe",
            "description": "打开记事本"用于"编辑文本"
        }'''

        result = parser.parse_response(problematic_response)

        # 应该能够通过宽松解析策略处理
        assert result is not None
        assert result.get("action") == "open_app"

    def test_parse_completely_invalid_json(self, parser):
        """测试完全无效的JSON"""
        invalid_response = "This is not JSON at all, just plain text"

        result = parser.parse_response(invalid_response)

        # 应该返回降级的结果
        assert result is not None
        assert "action" in result  # 应该有默认动作
        assert "parsing_strategy" in result
        assert result["parsing_strategy"] == "manual_reconstruction"

    def test_parse_empty_response(self, parser):
        """测试空响应"""
        empty_response = ""

        result = parser.parse_response(empty_response)

        assert result is not None
        assert "action" in result
        assert result["parsing_strategy"] == "manual_reconstruction"

    def test_parse_response_with_trailing_comma(self, parser):
        """测试带有尾随逗号的JSON"""
        trailing_comma_response = '''{
            "action": "open_app",
            "command": "calc.exe",
            "confidence": 0.8,
        }'''

        result = parser.parse_response(trailing_comma_response)

        assert result is not None
        assert result["action"] == "open_app"
        assert result["command"] == "calc.exe"

    def test_parse_validation_required_fields(self, parser):
        """测试必需字段验证"""
        missing_required_response = '''{
            "some_field": "some_value",
            "other_field": 123
        }'''

        result = parser.parse_response(missing_required_response)

        # 应该验证必需字段并提供默认值
        assert result is not None
        assert "action" in result  # 应该有默认action
        assert "confidence" in result  # 应该有默认confidence

    def test_logging_error_details(self, parser):
        """测试错误日志记录"""
        invalid_response = '''{"action": open_app "no closing brace'''

        # 这应该记录错误详情
        result = parser.parse_response(invalid_response)

        assert result is not None
        # 检查是否有错误统计
        assert hasattr(parser, 'error_stats')

    def test_performance_multiple_parsing_attempts(self, parser):
        """测试多次解析尝试的性能"""
        problematic_responses = [
            '{"action": "valid", "command": "test"}',
            '{"invalid json here',
            'not json at all',
            '{"partial": "data"',
            '',
        ]

        import time
        start_time = time.time()

        for response in problematic_responses:
            result = parser.parse_response(response)
            assert result is not None

        end_time = time.time()

        # 解析应该很快完成（每个< 10ms）
        assert (end_time - start_time) < 0.05  # 50ms for all responses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])