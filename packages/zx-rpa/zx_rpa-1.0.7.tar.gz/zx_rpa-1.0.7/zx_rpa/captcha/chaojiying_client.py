"""
超级鹰验证码客户端
专注于超级鹰平台的验证码识别服务
"""

from loguru import logger
from typing import Dict, Any, List
from .image_processor import ImageProcessor
from .providers.chaojiying_provider import ChaojieyingProvider


class ChaojieyingClient:
    """超级鹰验证码客户端"""

    def __init__(self, username: str, password: str, soft_id: str = "1"):
        """
        初始化超级鹰客户端

        Args:
            username: 超级鹰用户名
            password: 超级鹰密码
            soft_id: 软件ID
        """
        logger.debug("初始化超级鹰验证码客户端，用户: {}", username)
        
        if not username or not password:
            logger.error("超级鹰用户名和密码不能为空")
            raise ValueError("超级鹰用户名和密码不能为空")

        self.username = username
        self.password = password
        self.soft_id = soft_id
        self._image_processor = ImageProcessor()
        self._provider = ChaojieyingProvider(username, password, soft_id)

    def recognize(self, image: str, type_id: int = 1001) -> str:
        """
        识别验证码

        Args:
            image: 图片数据（base64编码/文件路径/URL）
            type_id: 验证码类型ID（超级鹰默认1001）

        Returns:
            str: 识别结果
        """
        logger.debug("超级鹰识别验证码，类型: {}", type_id)

        try:
            # 处理图片格式
            processed_image = self._image_processor.process_image(image)
            return self._provider.recognize(processed_image, type_id)
        except Exception as e:
            logger.error("超级鹰验证码识别失败: {}", str(e))
            raise

    def check_balance(self) -> Dict[str, Any]:
        """
        查询账户余额

        Returns:
            Dict: 账户信息
        """
        logger.debug("查询超级鹰账户余额")

        try:
            return self._provider.check_balance()
        except Exception as e:
            logger.error("查询超级鹰余额失败: {}", str(e))
            raise

    def get_supported_types(self) -> List[Dict[str, Any]]:
        """
        获取支持的验证码类型

        Returns:
            List: 支持的验证码类型列表
        """
        logger.debug("获取超级鹰支持的验证码类型")
        return self._provider.get_supported_types()

    # ==================== 图片处理功能 ====================

    def process_image(self, image: str) -> str:
        """
        图片格式转换为base64

        Args:
            image: 图片来源（base64编码/文件路径/URL）

        Returns:
            str: base64编码的图片数据
        """
        logger.debug("处理图片格式转换")
        return self._image_processor.process_image(image)

    def validate_image(self, image: str) -> bool:
        """
        验证图片格式

        Args:
            image: 图片来源

        Returns:
            bool: 是否为有效图片
        """
        logger.debug("验证图片格式")
        return self._image_processor.validate_image(image)

    def base64_to_image(self, base64_data: str, output_path: str) -> bool:
        """
        将base64数据转换为本地图片文件

        Args:
            base64_data: base64编码的图片数据
            output_path: 输出文件路径

        Returns:
            bool: 转换是否成功
        """
        logger.debug("将base64转换为本地图片")
        return self._image_processor.base64_to_image(base64_data, output_path)
