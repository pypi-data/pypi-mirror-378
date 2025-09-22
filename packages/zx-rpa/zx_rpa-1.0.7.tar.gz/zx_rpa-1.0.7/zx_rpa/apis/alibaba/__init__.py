"""
阿里平台自动化操作封装

## 基本导入使用
```python
from zx_rpa.apis.alibaba import AlibabaManager
from DrissionPage import ChromiumPage

# 初始化页面
page = ChromiumPage()
tab = page.new_tab()

# 创建管理器
manager = AlibabaManager()
```

## 获取客户端（不需要传tab）
```python
# 1. 获取平台客户端
guanghe = manager.get_guanghe_client()     # 光合平台
guang = manager.get_guang_client()         # 逛逛平台（同光合）
```

## 使用方式（使用时传入tab）
```python
# 方式1：页面组合操作（推荐）
login_tab = guanghe.login_tab(tab)         # 传入tab获取页面操作对象
success, msg = login_tab.login_with_password("user", "pass")

dashboard_tab = guanghe.dashboard_tab(tab) # 可以传入不同的tab
overview = dashboard_tab.get_overview_data()

# 方式2：单元素操作（精细控制）
login_ele = guanghe.login_ele(tab)         # 传入tab获取元素操作对象
login_ele.input_username("username")

dashboard_ele = guanghe.dashboard_ele(tab)
dashboard_ele.click_menu_item("数据分析")

# 方式3：通用元素操作
common_ele = guanghe.common_ele(tab)
common_ele.scroll_to_bottom()

# 方式4：直接使用通用登录验证
auth = manager.get_auth_client(tab)        # 通用登录验证
auth.input_username("username")
auth.input_password("password")
auth.click_login_button()
if auth.wait_login_success():
    print("登录成功")
```

## 核心优势
- 🔄 **灵活的tab管理**：不同页面可以使用不同的tab
- 🎯 **按需创建**：只在使用时创建页面/元素操作对象
- 🏷️ **双名称支持**：光合/逛逛随意使用
- 📦 **统一管理**：所有客户端通过AlibabaManager获取

## 对外方法
- 获取光合客户端：get_guanghe_client()
- 获取逛逛客户端：get_guang_client()（光合平台别名）
- 获取通用登录验证客户端：get_auth_client(tab)
"""

from .manager import AlibabaManager

__all__ = ['AlibabaManager']
