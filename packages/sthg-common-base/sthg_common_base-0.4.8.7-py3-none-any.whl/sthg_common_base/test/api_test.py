import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
# 导入原始路由和注册函数（假设 register_* 函数在 common 模块）
from sthg_common_base.utils.log_util import  register_log_middleware, Logger
from sthg_common_base.response.exception import register_exception_handlers

# 创建测试专用的 FastAPI 实例（关键改动）
def create_test_app():
    app = FastAPI()
    #app.include_router(router)  # 注入原始路由
    logger = Logger()  # 初始化日志器
    register_exception_handlers(app)  # 注册异常处理器
    register_log_middleware(app)  # 注册日志中间件
    return app

class TestFastAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()  # 每次测试创建新实例
        self.client = TestClient(self.app)  # 使用新实例的客户端

    # ---------------------------
    # 原有测试方法保持不变（示例保留两个做演示）
    # ---------------------------
    def test_get_object_test(self):
        response = self.client.get("/get_Object_test")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["code"], 200)
        self.assertEqual(data["msg"], "操作成功")

    def test_custom_exception(self):
        response = self.client.get("/test_expection")
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data["code"], 403)
        self.assertEqual(data["msg"], "拒绝访问")

    # ---------------------------
    # 异步测试方法需调整（关键改动）
    # ---------------------------
    @pytest.mark.asyncio
    async def test_async_endpoints(self):
        # 使用 async_client 替代 client（FastAPI TestClient 同步客户端不兼容异步）
        async with TestClient(self.app) as async_client:
            # 测试异步获取对象
            response = await async_client.get("/get_Object_test_ansyc")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["code"], 200)

            # 测试异步异常场景
            response = await async_client.get("/get_exception_test2_ansyc")
            self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main()
