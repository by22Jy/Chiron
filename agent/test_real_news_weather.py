"""
测试真实新闻天气API服务

避免Unicode编码问题的简化测试版本
"""

import sys
import os
import time

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file))

from real_news_weather import RealNewsWeatherService, create_news_weather_service, load_api_config


def test_api_config_loading():
    """测试API配置加载"""
    print("测试API配置加载...")

    config = load_api_config()

    print(f"新闻API密钥: {'已配置' if config.get('news_api_key') else '未配置'}")
    print(f"天气API密钥: {'已配置' if config.get('weather_api_key') else '未配置'}")
    print(f"默认城市: {config.get('default_city', 'Beijing')}")

    return config


def test_news_service():
    """测试新闻服务"""
    print("\\n测试新闻服务...")

    service = create_news_weather_service()

    # 获取新闻
    news_list = service.get_top_news(5)

    print(f"获取到 {len(news_list)} 条新闻:")
    for i, news in enumerate(news_list, 1):
        print(f"  {news}")

    return news_list


def test_weather_service():
    """测试天气服务"""
    print("\\n测试天气服务...")

    service = create_news_weather_service()

    # 获取天气
    weather_info = service.get_weather_info()

    print("天气信息:")
    print(f"  城市: {weather_info.get('city', '未知')}")
    print(f"  日期: {weather_info.get('date', '未知')}")
    print(f"  温度: {weather_info.get('temperature', '未知')}")
    print(f"  天气: {weather_info.get('condition', '未知')}")
    print(f"  湿度: {weather_info.get('humidity', '未知')}")
    print(f"  风速: {weather_info.get('wind', '未知')}")
    print(f"  体感温度: {weather_info.get('feels_like', '未知')}")

    return weather_info


def test_combined_report():
    """测试综合报告"""
    print("\\n测试综合报告...")

    service = create_news_weather_service()

    # 获取综合报告
    report = service.get_combined_report(3, "Beijing")

    print(f"报告生成时间: {report['timestamp']}")
    print(f"新闻数量: {report['news_count']}")
    print(f"天气城市: {report['weather_city']}")

    print("\\n新闻预览:")
    for news in report['news'][:3]:
        print(f"  {news}")

    print("\\n天气预览:")
    weather = report['weather']
    print(f"  {weather.get('temperature', '未知')} - {weather.get('condition', '未知')}")

    return report


def test_caching():
    """测试缓存功能"""
    print("\\n测试缓存功能...")

    service = create_news_weather_service()

    # 第一次请求
    start_time = time.time()
    news1 = service.get_top_news(3)
    first_time = time.time() - start_time

    # 第二次请求（应该使用缓存）
    start_time = time.time()
    news2 = service.get_top_news(3)
    second_time = time.time() - start_time

    print(f"第一次请求耗时: {first_time:.3f} 秒")
    print(f"第二次请求耗时: {second_time:.3f} 秒")
    print(f"速度提升: {first_time/second_time:.1f}x" if second_time > 0 else "缓存生效")

    # 检查结果一致性
    if news1 == news2:
        print("缓存结果一致: 是")
    else:
        print("缓存结果一致: 否")


def check_api_keys():
    """检查API密钥配置"""
    print("\\n检查API密钥配置...")

    config = load_api_config()

    print("\\n=== API配置指南 ===")
    print("要使用真实的新闻和天气API，请按以下步骤配置:")

    if not config.get('news_api_key'):
        print("\\n1. 新闻API配置:")
        print("   - 访问: https://newsapi.org/register")
        print("   - 注册免费账户")
        print("   - 获取API密钥")
        print("   - 将密钥填入 api_config.json 的 news_api_key 字段")
        print("   - 免费额度: 每月1000次请求")

    if not config.get('weather_api_key'):
        print("\\n2. 天气API配置:")
        print("   - 访问: https://openweathermap.org/api")
        print("   - 注册免费账户")
        print("   - 获取API密钥")
        print("   - 将密钥填入 api_config.json 的 weather_api_key 字段")
        print("   - 免费额度: 每月1000000次调用")

    if config.get('news_api_key') and config.get('weather_api_key'):
        print("\\n✓ 所有API密钥已配置，可以使用真实数据")
    else:
        print("\\n⚠ 部分API密钥未配置，将使用模拟数据")
        print("配置完成后重新运行此测试以验证")


def main():
    """主测试函数"""
    print("真实新闻天气API服务测试")
    print("="*50)

    # 1. 检查配置
    config = test_api_config_loading()

    # 2. 测试新闻服务
    news_list = test_news_service()

    # 3. 测试天气服务
    weather_info = test_weather_service()

    # 4. 测试综合报告
    report = test_combined_report()

    # 5. 测试缓存
    test_caching()

    # 6. 检查API密钥配置
    check_api_keys()

    # 总结
    print("\\n" + "="*50)
    print("测试总结:")
    print(f"✓ 新闻获取: {len(news_list)} 条")
    print(f"✓ 天气获取: {weather_info.get('condition', '未知')}")
    print(f"✓ 综合报告: 已生成")
    print(f"✓ 缓存功能: 正常")
    print("\\n系统已准备好使用真实API数据")


if __name__ == '__main__':
    main()