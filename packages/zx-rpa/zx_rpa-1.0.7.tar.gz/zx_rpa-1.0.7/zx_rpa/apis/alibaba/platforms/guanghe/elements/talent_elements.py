"""
淘宝光合平台 - 达人管理页面元素操作
https://mcn.guanghe.taobao.com/page/talent
"""

from loguru import logger

import time

class GuangheTalentElements:
    """光合达人管理页面元素操作"""

    def __init__(self, tab):
        """初始化达人管理页面元素操作
        
        Args:
            tab: DrissionPage的页面标签对象
        """
        self.tab = tab
        logger.debug("初始化光合达人管理页面元素操作")

    # 点击侧边菜单栏 达人管理
    def click_talent_menu(self):
        """点击侧边菜单栏 - 达人管理"""
        self.common.click_talent_menu()

    # 点击顶部 已绑定达人
    def click_bound_talent(self):
        """点击顶部 - 已绑定达人"""
        logger.debug("点击顶部 - 已绑定达人")
        self.tab.ele("t:div@@class=next-tabs-tab-inner@@text():已绑定").click()

    # 搜索达人 昵称或逛逛号
    def search_talent(self, keyword):
        """搜索达人 - 逛逛号"""
        logger.debug("搜索达人: {}", keyword)
        self.tab.ele("t:input@@placeholder=请输入创作者昵称/逛逛号进行搜索").input(keyword, clear=True)
        time.sleep(0.5)
        self.tab.ele("t:button@@text()=搜索").click()
        time.sleep(1)
        if self.tab.wait.eles_loaded(f"t:div@@text()=逛逛号：{keyword}"):
            time.sleep(1)
            name_ele = self.tab.ele("t:span@@class:name--")
            level_ele = self.tab.ele("t:td@@data-next-table-col=1")
            publish_ele = self.tab.ele("t:span@@text()=发布")
            manage_works_ele = self.tab.ele("t:span@@text()=作品管理")
            unbind_ele = self.tab.ele("t:span@@text()=解绑")
            return {"name": name_ele.text, "level": level_ele.text, "publish_ele": publish_ele, "manage_works_ele": manage_works_ele, "unbind_ele": unbind_ele}
        return False

    # 点击发布 发视频（独立发布，批量发布） 发图文
    def click_individual_publish(self, publish_ele, publish_type="独立发布"):
        """点击进入发布 - 发视频（独立发布，批量发布） 发图文
            
        Args:
            publish_ele (Element): 发布元素
            publish_type (str): 发布类型，独立发布、批量发布、发图文
        """
        publish_ele.click()
        if publish_type == "独立发布":
            self.tab.ele("t:div@@class=publish-menu-item-container@@text()=发视频").click()
            self.tab.ele("t:div@@class=publish-menu-item-container@@text()=独立发布").click()
        elif publish_type == "批量发布":
            self.tab.ele("t:div@@class=publish-menu-item-container@@text()=发视频").click()
            self.tab.ele("t:div@@class=publish-menu-item-container@@text()=批量发布").click()
        elif publish_type == "发图文":
            self.tab.ele("t:div@@class=publish-menu-item-container@@text()=发图文").click()
        