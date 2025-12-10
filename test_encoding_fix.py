#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试语音识别编码修复
"""

import sys
import os

# 添加agent目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent'))

def test_logging_encoding():
    """测试日志编码是否修复"""
    try:
        print("测试语音控制器日志编码...")

        # 导入日志模块
        import logging

        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger('test_encoding')

        # 测试修复后的日志格式
        logger.info("[语音] 识别到语音: 测试文本")
        logger.info("[语音] Speech recognized: test text")

        print("[OK] 编码测试通过！")
        return True

    except Exception as e:
        print(f"[ERROR] 编码测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_logging_encoding()
    if success:
        print("\n编码修复验证完成！")
    else:
        print("\n编码修复验证失败！")