"""
验证码处理模块 - 提供简洁易用的验证码识别服务

## 引入方式
```python
from zx_rpa.captcha import CaptchaSolver

# 创建专用验证码客户端（配置一次，多次使用）
tujian = CaptchaSolver.tujian(username='user', password='pass')
chaojiying = CaptchaSolver.chaojiying(username='user', password='pass', soft_id='123')

# 简洁的识别调用
result1 = tujian.recognize('image_data', type_id=1)
result2 = chaojiying.recognize('image_data', type_id=1001)

# 查询余额
balance1 = tujian.check_balance()
balance2 = chaojiying.check_balance()
```

## 模块结构
- captcha_solver.py - 对外接口，工厂类
- tujian_client.py - 图鉴客户端实现
- chaojiying_client.py - 超级鹰客户端实现

## 对外方法
### CaptchaSolver（验证码解决器工厂类）
#### 工厂方法
- tujian(username, password) -> TujianClient - 创建图鉴客户端
- chaojiying(username, password, soft_id="1") -> ChaojieyingClient - 创建超级鹰客户端

### 专用客户端类
#### TujianClient
- recognize(image, type_id=1) -> str - 图鉴识别
- check_balance() -> dict - 查询图鉴余额
- get_supported_types() -> dict - 获取支持的验证码类型

#### ChaojieyingClient
- recognize(image, type_id=1001) -> str - 超级鹰识别
- check_balance() -> dict - 查询超级鹰余额
- get_supported_types() -> list - 获取支持的验证码类型

### 图片处理功能（两个客户端都支持）
- process_image(image) -> str - 本地或网络url图片格式转换为base64
- validate_image(image) -> bool - 验证图片格式
- base64_to_image(base64_data, output_path) -> bool - 将base64转换为本地图片


"""

from .captcha_solver import CaptchaSolver

__all__ = ['CaptchaSolver']
