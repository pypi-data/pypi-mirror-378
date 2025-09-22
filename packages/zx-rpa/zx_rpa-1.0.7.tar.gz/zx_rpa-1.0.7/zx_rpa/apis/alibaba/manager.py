"""
阿里平台管理器 - 统一入口
"""

from loguru import logger
from .platforms.guanghe.client import GuangheClient
from .common.auth import AlibabaAuth


class AlibabaManager:
    """阿里平台管理器 - 工厂类模式"""
    
    def __init__(self):
        logger.debug("初始化阿里平台管理器")
    
    def get_auth_client(self, tab):
        """获取阿里平台通用登录验证客户端

        Args:
            tab: DrissionPage的页面标签对象（必需）

        Returns:
            AlibabaAuth: 通用登录验证客户端实例
        """
        logger.debug("创建阿里平台通用登录验证客户端")
        return AlibabaAuth(tab)
    
    def get_guanghe_client(self):
        """获取光合客户端

        Returns:
            GuangheClient: 光合客户端实例
        """
        logger.debug("创建光合客户端")
        return GuangheClient()

    def get_guang_client(self):
        """获取逛逛客户端（光合平台的别名）

        Returns:
            GuangheClient: 光合客户端实例
        """
        logger.debug("创建逛逛客户端（光合平台）")
        return GuangheClient()

    
    # TODO: 后续添加其他平台
    # def get_taobao_client(self):
    #     return TaobaoClient()
    #
    # def get_qianniu_client(self):
    #     return QianniuClient()
