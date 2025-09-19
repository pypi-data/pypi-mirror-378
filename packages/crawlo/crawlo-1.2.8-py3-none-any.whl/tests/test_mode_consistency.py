#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模式一致性提示
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from crawlo.crawler import CrawlerProcess
from crawlo.spider import Spider
from crawlo import Request


class TestSpider(Spider):
    name = "test_mode_spider"
    
    def start_requests(self):
        yield Request("https://httpbin.org/get")
    
    def parse(self, response):
        yield {"url": response.url, "status": response.status}


async def test_mode_consistency():
    """测试模式一致性提示"""
    print("🔍 测试模式一致性提示...")
    
    try:
        # 创建爬虫进程
        process = CrawlerProcess()
        
        # 添加爬虫
        await process.crawl(TestSpider)
        
        print("✅ 模式一致性测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 设置日志级别
    import logging
    logging.basicConfig(level=logging.INFO)
    
    asyncio.run(test_mode_consistency())