"""
逛逛平台自动化操作

from zx_rpa.apis import guangguang
talent_tab = guangguang.talent_tab(tab)

## 单操作模块

## 内部组合的模块

"""

from .talent_tab import TalentTab
from .common_tab import CommonTab
from .content_publish_tab import ContentPublishTab

def common_tab(tab):
    """创建通用业务操作实例

    Args:
        tab: DrissionPage的tab对象

    Returns:
        CommonTab: 通用业务操作实例
    """
    return CommonTab(tab)

def talent_tab(tab):
    """创建达人管理页面操作实例

    Args:
        tab: DrissionPage的tab对象

    Returns:
        TalentTab: 达人管理页面操作实例
    """
    return TalentTab(tab)

def content_publish_tab(tab):
    """创建内容发布页面操作实例

    Args:
        tab: DrissionPage的tab对象

    Returns:
        ContentPublishTab: 内容发布页面操作实例
    """
    return ContentPublishTab(tab)


__all__ = ['common_tab', 'talent_tab', 'content_publish_tab']
