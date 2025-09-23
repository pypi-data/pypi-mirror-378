import requests
from bs4 import BeautifulSoup
from log import log
from typing import Generator, Optional

class OpenEuler():
    def __init__(self):
        pass

    def get_openEuler_everything_pkgs(
            self, os_version: str, os_arch: str
    ) -> Generator[str, None, None]:
        """
        从 openEuler everything 源页面获取指定版本、架构的所有软件包列表，以迭代方式返回。

        Args:
            os_version: openEuler 版本号（如 "24.03-LTS-SP2"）
            os_arch: 系统架构（如 "x86_64", "aarch64"）

        Yields:
            str: 软件包名称（如 "a2ps-4.14-36.oe2403.x86_64.rpm"）

        Raises:
            requests.exceptions.RequestException: 网络请求失败（如超时、404、500 等）
            ValueError: 页面解析失败（未找到任何 .rpm 包）
        """
        # 基础 URL 模板（openEuler everything 源固定路径）
        base_url_template = "https://dl-cdn.openeuler.openatom.cn/openEuler-{os_version}/everything/{os_arch}/Packages/"
        # 请求超时时间（避免长期阻塞）
        timeout = 15
        # 请求头（模拟浏览器，避免部分服务器拦截）
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        # 1. 构造目标页面 URL
        target_url = base_url_template.format(
            os_version=os_version, os_arch=os_arch
        )
        try:
            # 2. 发送 GET 请求获取页面内容（允许重定向，部分 CDN 可能跳转）
            response = requests.get(
                url=target_url,
                headers=headers,
                timeout=timeout,
                allow_redirects=True
            )
            # 检查响应状态码（非 200 视为请求失败）
            response.raise_for_status()
            html_content = response.text

        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"获取页面失败！URL: {target_url}, 错误: {str(e)}"
            ) from e

        # 3. 解析 HTML 提取 .rpm 包链接
        soup = BeautifulSoup(html_content, "html.parser")  # 使用标准 HTML 解析器（无需额外依赖）
        # 页面中软件包以 <a> 标签存在，href 属性为包名，且文本与 href 一致
        pkg_links = soup.find_all("a", href=lambda href: href and href.endswith(".rpm"))

        if not pkg_links:
            raise ValueError(
                f"页面解析失败！URL: {target_url}, 未找到任何 .rpm 格式的软件包"
            )

        # 4. 迭代返回软件包名称（通过 yield 实现生成器）
        for link in pkg_links:
            pkg_name = link.get("href")  # 从 href 属性获取包名（避免文本空格问题）
            if pkg_name:  # 双重校验（防止空链接）
                yield pkg_name

if __name__ == "__main__":
    # 初始化获取器
    oe = OpenEuler()
    # 示例：获取 openEuler 24.03-LTS-SP2 x86_64 架构的所有包（迭代打印前 10 个）
    pkg_generator = oe.get_openEuler_everything_pkgs(
        os_version="24.03-LTS-SP2",
        os_arch="x86_64"
    )
    count=0
    for pkg in pkg_generator:
        count+=1
        print(pkg)
    print("共获取到 %d 个软件包" % count)

