"""
光合内容发布页面元素定位
https://mcn.guanghe.taobao.com/page/unify/ContentPublish
"""

import re
from loguru import logger
from time import sleep



class GuangheContentPublishElements:
    """光合内容发布页面元素操作"""

    def __init__(self, tab):
        """初始化内容发布页面元素操作
        
        Args:
            tab: DrissionPage的页面标签对象
        """
        self.tab = tab
        logger.debug("初始化光合内容发布页面元素操作")

        self.upload_video_button_ele = self.tab.ele("t:span@@class=upload-button@@tx():上传视频")
    
    # 上传视频按钮
    def get_upload_video_button(self):
        """获取上传视频按钮"""
        return self.upload_video_button_ele

    def upload_video(self, file_path):
        """上传视频，等待内容显示
        
        Args:
            file_path (str): 视频文件路径
        """
        logger.debug("上传视频: {}", file_path)
        self.upload_video_button_ele.click.to_upload(file_path)
        self.tab.wait.eles_loaded("t:div@@class:publish-guanghe__video-show--container", timeout=30)
        sleep(1)

    # 等待封面加载完毕
    def wait_cover_loaded(self):
        """等待封面加载完毕"""
        self.tab.wait.eles_loaded("封面生成中", timeout=10)
        if self.tab.wait.ele_displayed("封面生成中"):
            logger.debug("封面生成完成")
            sleep(1)

    def input_video_title(self, title):
        """视频描述 输入视频标题"""
        self.tab.ele("t:div@@class:publish-content__title-input--inputWrap").ele("t:input").input(title, clear=True)

    def input_video_description(self, description=None, tags=None):
        """视频描述 输入视频描述，标签暂时不对

        Args:
            description (str): 视频描述
            tags (list): 标签列表
        """
        input_ele = self.tab.ele("t:div@@class=rich-text-content")
        if description:
            input_ele.input(description+"\n\n", clear=True)
        if tags:
            for tag in tags:
                self.tab.ele("t:div@@data-autolog-container=richText-footer-operation-add-hashtag").click()  # 点击添加标签按钮
                sleep(0.5)
                input_ele.input(tag, by_js=False)  # 输入标签名
                sleep(0.5)
                input_ele.input(" ", by_js=False)  # 输入空格，触发标签选择器
                sleep(0.5)
                input_ele.input(" ", by_js=False)  # 输入空格，触发标签选择器

    def join_topic_activity(self, topic: str):
        """参与话题活动, 第一个搜索结果"""
        self.tab.ele("t:div@@class:publish-content__topic-v2--select").click()
        if self.tab.wait.eles_loaded("t:div@@class=next-dialog-body"):
            f_ele = self.tab.ele("t:div@@class=next-dialog-body")
            f_ele.ele("t:input").input(topic, clear=True)
            f_ele.ele("t:span@@text()=搜索").click()
            if self.tab.wait.eles_loaded("t:div@@class:publish-content__topic-v2--topic-info"):
                sleep(0.5)
                self.tab.ele("t:div@@class:publish-content__topic-v2--topic-info").click()
                self.tab.ele("t:span@@text()=确认提交").click()

    # 关联商品
    def associate_product_id(self, product_id: str):
        """关联商品 指定id 添加商品"""
        self.tab.ele("t:div@@class:publish-content__item-v2--item-trigger-text@@text()=添加商品").click()
        return self._associate_selection_product(product_id)

    # 关联推荐商品
    def associate_recommend_product(self):
        """关联推荐商品 佣金最高"""
        if self.tab.wait.eles_loaded("已为您推荐综合收益最高的商品，可点击后直接挂品", timeout=60):
            self.tab.ele("t:div@@class:publish-content__item-v2--item-trigger-text@@text()=添加商品").click()
            if self.tab.wait.eles_loaded("推荐商品", timeout=5):
                self.tab.ele("推荐商品").click()
                sleep(1)

                f_eles = self.tab.ele("t:div@class=next-tabs-tabpane active").ele("t:div@@class:publish-content__item-v2--content").eles("t:div@class:publish-content__item-v2--item-desc")
                # 存储所有商品信息
                products = []
                for f_ele in f_eles:
                    url = f_ele.ele("t:a@@class:publish-content__item-v2--item-itemUrl").link
                    text = f_ele.text
                    result = parse_product_info(text)
                    result['url'] = url  # 添加URL到结果中
                    products.append(result)

                # 选择佣金最高的商品
                best_product = max(products, key=lambda x: x['commission'])
                logger.debug(f"\n选择佣金最高的商品:")
                logger.debug(f"标题: {best_product['title']}")
                logger.debug(f"佣金: {best_product['commission']}")
                logger.debug(f"URL: {best_product['url']}")
                product_id = extract_product_id_from_url(best_product['url'])
                logger.debug(f"商品ID: {product_id}")
                return self._associate_selection_product(product_id)  # 关联选品车商品
            else:
                logger.debug("没有找到推荐商品")
                self.tab.ele("t:span@@text()=取消",timeout=3).click()
                return False
        else:
            logger.debug("没有加载出推荐商品")
            return False

    # 内容来源声明
    def declare_content_source(self, source: str):
        """内容来源声明
        
        Args:
            source (str): 来源类型
                - 内容由AI生成
                - 虚拟演绎，仅供娱乐
                - 自主拍摄
                - 引用转载
        """
        self.tab.ele(f"t:span@@text()={source}").click()

    def _associate_selection_product(self, product_id: str):
        """关联选品车商品"""
        if self.tab.wait.eles_loaded("选品车", timeout=5):
            self.tab.ele("选品车").click()
            self.tab.ele("t:input@@role=searchbox").input(product_id, clear=True)
            sleep(0.5)
            self.tab.ele("t:i@@class:next-icon next-icon-search").click()
            if self.tab.wait.eles_loaded("数据加载中，请耐心等待哦~", timeout=3):
                if self.tab.wait.ele_displayed("数据加载中，请耐心等待哦~"):
                    if not self.tab.wait.eles_loaded(f"没有找到与", timeout=1):
                        self.tab.ele("t:div@class=next-tabs-tabpane active").ele("t:div@@class=next-loading next-loading-inline").ele("t:div@@class:publish-content__item-v2--item").click()
                        sleep(0.5)
                        self.tab.ele("t:span@@text()=确定",timeout=3).click()
                        return True
                    else:
                        logger.debug("没有找到与{}相关的商品", product_id)
                        self.tab.ele("t:span@@text()=取消",timeout=3).click()
                        return False
                else:
                    logger.debug("没有找到与{}相关的商品", product_id)
                    self.tab.ele("t:span@@text()=取消",timeout=3).click()
                    return False
            else:
                logger.debug("加载异常", product_id)
                self.tab.ele("t:span@@text()=取消",timeout=3).click()
                return False
        else:
            logger.debug("没有找到选品车")
            self.tab.ele("t:span@@text()=取消",timeout=3).click()
            return False

def parse_product_info(text: str) -> dict:
    """解析商品参数信息

    Args:
        text (str): 商品信息文本，包含标题、价格、佣金率、佣金、店铺、销量等信息

    Returns:
        dict: 包含以下字段的字典
            - title: 商品标题 (str)
            - price: 价格 (float) - 纯数字，无货币符号
            - commission_rate: 佣金率 (float) - 纯数字，无百分号
            - commission: 佣金 (float) - 纯数字，无货币符号和单位
            - shop: 店铺名称 (str)
            - sales: 销量 (int) - 纯数字，已转换万、千等单位

    Example:
        >>> text = '''雅漾清透水润防晒乳50mlSPF50+小金刚敏感肌水润清爽防晒霜隔离
        ... ¥99.00
        ... 预估佣金率 0.6%
        ... 约赚 ¥0.6/件
        ... 万宁官方旗舰店
        ... 已售37'''
        >>> result = parse_product_info(text)
        >>> print(result)
        {'title': '雅漾清透水润防晒乳50mlSPF50+小金刚敏感肌水润清爽防晒霜隔离',
         'price': 99.0, 'commission_rate': 0.6, 'commission': 0.6,
         'shop': '万宁官方旗舰店', 'sales': 37}
    """
    if not text or not text.strip():
        return {
            'title': '',
            'price': 0.0,
            'commission_rate': 0.0,
            'commission': 0.0,
            'shop': '',
            'sales': 0
        }

    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

    result = {
        'title': '',
        'price': 0.0,
        'commission_rate': 0.0,
        'commission': 0.0,
        'shop': '',
        'sales': 0
    }

    # 正则表达式模式
    price_pattern = r'^¥(\d+\.?\d*)$'  # 价格：¥99.00，提取数字
    commission_rate_pattern = r'^预估佣金率\s+(\d+\.?\d*)%$'  # 佣金率：预估佣金率 0.6%，提取数字
    commission_pattern = r'^约赚\s+¥(\d+\.?\d*)/件$'  # 约赚：约赚 ¥0.6/件，提取数字
    sales_pattern = r'^已售(.+)$'  # 销量：已售37, 已售1000+, 已售3万+
    shop_pattern = r'.*(旗舰店|专营店|专卖店|官方店|天猫超市|店).*'  # 店铺：包含店铺关键词

    title_candidates = []  # 可能的标题候选

    def parse_sales_number(sales_text):
        """解析销量数字"""
        if not sales_text:
            return 0

        # 移除"已售"前缀
        sales_text = sales_text.replace('已售', '').strip()

        # 处理万、千等单位
        if '万' in sales_text:
            # 提取万前面的数字
            match = re.search(r'(\d+\.?\d*)万', sales_text)
            if match:
                return int(float(match.group(1)) * 10000)
        elif '千' in sales_text:
            # 提取千前面的数字
            match = re.search(r'(\d+\.?\d*)千', sales_text)
            if match:
                return int(float(match.group(1)) * 1000)
        else:
            # 提取纯数字（可能带+号）
            match = re.search(r'(\d+)', sales_text)
            if match:
                return int(match.group(1))

        return 0

    for line in lines:
        # 匹配价格
        price_match = re.match(price_pattern, line)
        if price_match:
            result['price'] = float(price_match.group(1))
            continue

        # 匹配佣金率
        commission_rate_match = re.match(commission_rate_pattern, line)
        if commission_rate_match:
            result['commission_rate'] = float(commission_rate_match.group(1))
            continue

        # 匹配约赚
        commission_match = re.match(commission_pattern, line)
        if commission_match:
            result['commission'] = float(commission_match.group(1))
            continue

        # 匹配销量
        sales_match = re.match(sales_pattern, line)
        if sales_match:
            result['sales'] = parse_sales_number(line)
            continue

        # 匹配店铺
        if re.match(shop_pattern, line):
            result['shop'] = line
            continue

        # 如果不匹配以上任何模式，可能是标题或其他信息
        # 排除一些明显不是标题的行（如推广者信息等）
        if not any(keyword in line for keyword in ['传媒', '文化', '科技', '网络', '广告']):
            title_candidates.append(line)

    # 选择标题：通常是第一个候选，或者最长的候选（商品名称通常较长）
    if title_candidates:
        # 优先选择第一个候选作为标题
        result['title'] = title_candidates[0]
        # 如果有多个候选，选择最长的作为标题（商品名称通常比较详细）
        if len(title_candidates) > 1:
            result['title'] = max(title_candidates, key=len)

    return result


def extract_product_id_from_url(url: str) -> str:
    """从商品URL中提取商品ID

    Args:
        url (str): 淘宝商品URL，如 https://item.taobao.com/item.htm?id=520720076936

    Returns:
        str: 商品ID，如 '520720076936'，如果提取失败返回空字符串

    Example:
        >>> url = "https://item.taobao.com/item.htm?id=520720076936"
        >>> product_id = extract_product_id_from_url(url)
        >>> print(product_id)
        520720076936

        >>> url = "https://detail.tmall.com/item.htm?id=123456789&spm=a220m.1000858.1000725.1.abc"
        >>> product_id = extract_product_id_from_url(url)
        >>> print(product_id)
        123456789
    """
    if not url or not isinstance(url, str):
        return ''

    # 使用正则表达式匹配 id= 后面的数字
    import re
    match = re.search(r'[?&]id=(\d+)', url)
    if match:
        return match.group(1)

    return ''


if __name__ == '__main__':
    text = '''【下拉领淘金币更优惠】Avene雅漾清爽倍护便携防晒乳SPF50+ 30ml
        ¥159.00
        预估佣金率 0.6%
        约赚 ¥1.0/件
        天猫超市
        已售1000+'''
    result = parse_product_info(text)
    print(result)
