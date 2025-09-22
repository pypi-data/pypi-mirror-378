"""
验证码解决器
提供简洁易用的验证码识别接口
"""

from loguru import logger
from .tujian_client import TujianClient
from .chaojiying_client import ChaojieyingClient


class CaptchaSolver:
    """验证码解决器工厂类"""

    @classmethod
    def tujian(cls, username: str, password: str) -> TujianClient:
        """
        创建图鉴验证码客户端

        Args:
            username (str): 图鉴平台的用户名，用于登录认证
            password (str): 图鉴平台的密码，用于登录认证

        Returns:
            TujianClient: 配置好的图鉴客户端实例，可直接调用识别方法

        Example:
            >>> solver = CaptchaSolver.tujian("your_username", "your_password")
            >>> result = solver.recognize("base64_image_data", type_id=1)
            >>> print(result)
            '1234'
        """
        logger.debug("创建图鉴验证码客户端")
        return TujianClient(username, password)

    @classmethod
    def chaojiying(cls, username: str, password: str, soft_id: str = "1") -> ChaojieyingClient:
        """
        创建超级鹰验证码客户端

        Args:
            username (str): 超级鹰平台的用户名，用于登录认证
            password (str): 超级鹰平台的密码，用于登录认证
            soft_id (str, optional): 软件ID，用于标识调用来源，默认为"1". Defaults to "1".

        Returns:
            ChaojieyingClient: 配置好的超级鹰客户端实例，可直接调用识别方法

        Example:
            >>> solver = CaptchaSolver.chaojiying("your_username", "your_password", "123")
            >>> result = solver.recognize("base64_image_data", type_id=1001)
            >>> print(result)
            'ABCD'
        """
        logger.debug("创建超级鹰验证码客户端")
        return ChaojieyingClient(username, password, soft_id)
