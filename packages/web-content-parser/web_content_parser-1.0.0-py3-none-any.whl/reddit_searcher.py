import requests
import json
import time
from typing import List, Dict, Optional, Union
from bs4 import BeautifulSoup
import re


class RedditSearcher:
    """Reddit搜索和解析类"""

    def __init__(self, brightdata_api_key: str):
        """
        初始化RedditSearcher

        Args:
            brightdata_api_key: BrightData API密钥
        """
        self.api_key = brightdata_api_key
        self.base_url = "https://api.brightdata.com/request"

    def parse_subreddits(self, html_content: str) -> Dict[str, Union[List[Dict], str, int]]:
        """
        解析HTML内容，提取subreddit信息

        Args:
            html_content: HTML字符串

        Returns:
            包含subreddits列表、下一页URL和总数的字典
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            subreddits = []
            next_page_url = None

            # 查找下一页URL
            faceplate_partial = soup.select_one('faceplate-partial[loading="lazy"][src]')
            if faceplate_partial:
                src = faceplate_partial.get('src')
                if src:
                    # 解码HTML实体并转换为完整URL
                    decoded_src = src.replace('&amp;', '&')
                    next_page_url = f"https://www.reddit.com{decoded_src}" if decoded_src.startswith('/') else decoded_src

            # 查找所有search-telemetry-tracker元素
            trackers = soup.select('search-telemetry-tracker[data-faceplate-tracking-context*="subreddit"]')

            for tracker in trackers:
                try:
                    subreddit_info = {
                        'id': '',
                        'name': '',
                        'nsfw': False,
                        'quarantined': False
                    }

                    # 解析tracking context获取基本信息
                    tracking_context = tracker.get('data-faceplate-tracking-context')
                    if tracking_context:
                        context_data = json.loads(tracking_context.replace('&quot;', '"'))
                        if 'subreddit' in context_data:
                            subreddit_info.update({
                                'id': context_data['subreddit'].get('id', ''),
                                'name': context_data['subreddit'].get('name', ''),
                                'nsfw': context_data['subreddit'].get('nsfw', False),
                                'quarantined': context_data['subreddit'].get('quarantined', False)
                            })

                    # 查找URL
                    link = tracker.select_one('a[href^="/r/"]')
                    if link:
                        subreddit_info['url'] = link.get('href')

                    # 查找图标
                    avatar = tracker.select_one('[rpl][avatar] img, img')
                    if avatar:
                        subreddit_info['iconUrl'] = avatar.get('src')

                    # 查找描述文本
                    desc_element = tracker.select_one('[data-testid="search-subreddit-desc-text"]')
                    if desc_element and desc_element.get_text(strip=True):
                        # 清理描述文本
                        description = re.sub(r'\s+', ' ', desc_element.get_text(strip=True))
                        subreddit_info['description'] = description

                    # 查找成员数和在线数
                    faceplate_numbers = tracker.select('faceplate-number[number]')
                    for element in faceplate_numbers:
                        try:
                            number = int(element.get('number', 0))
                            parent = element.parent
                            if parent:
                                parent_text = parent.get_text().lower()
                                if 'member' in parent_text or 'subscriber' in parent_text:
                                    subreddit_info['members'] = number
                                elif 'online' in parent_text or 'active' in parent_text:
                                    subreddit_info['online'] = number
                        except (ValueError, TypeError):
                            continue

                    # 备用方法：查找带有number属性的其他元素
                    if 'members' not in subreddit_info and 'online' not in subreddit_info:
                        number_elements = tracker.select('[number]')
                        for element in number_elements:
                            try:
                                number = int(element.get('number', 0))
                                parent = element.parent
                                if parent:
                                    context_text = parent.get_text().lower()
                                    if 'member' in context_text or 'subscriber' in context_text:
                                        subreddit_info['members'] = number
                                    elif 'online' in context_text or 'active' in context_text:
                                        subreddit_info['online'] = number
                            except (ValueError, TypeError):
                                continue

                    # 备用方法：解析文本中的数字
                    if 'members' not in subreddit_info and 'online' not in subreddit_info:
                        stats_selectors = [
                            '[data-testid="subreddit-subscribers"]',
                            '[data-testid="subreddit-members"]',
                            '.text-12',
                            '.subscribers'
                        ]

                        for selector in stats_selectors:
                            stats_elements = tracker.select(selector)
                            for element in stats_elements:
                                text = element.get_text(strip=True)

                                # 匹配成员数
                                member_match = re.search(r'(\d+\.?\d*)\s*([kmb])?\s*(members|subscribers)', text, re.I)
                                if member_match:
                                    num = float(member_match.group(1))
                                    unit = member_match.group(2)
                                    if unit:
                                        unit = unit.lower()
                                        if unit == 'k':
                                            num *= 1000
                                        elif unit == 'm':
                                            num *= 1000000
                                        elif unit == 'b':
                                            num *= 1000000000
                                    subreddit_info['members'] = int(num)

                                # 匹配在线数
                                online_match = re.search(r'(\d+\.?\d*)\s*([kmb])?\s*(online|active)', text, re.I)
                                if online_match:
                                    num = float(online_match.group(1))
                                    unit = online_match.group(2)
                                    if unit:
                                        unit = unit.lower()
                                        if unit == 'k':
                                            num *= 1000
                                        elif unit == 'm':
                                            num *= 1000000
                                        elif unit == 'b':
                                            num *= 1000000000
                                    subreddit_info['online'] = int(num)

                    # 确保有基本的名称
                    if not subreddit_info.get('name') and subreddit_info.get('url'):
                        url_match = re.search(r'/r/([^/]+)', subreddit_info['url'])
                        if url_match:
                            subreddit_info['name'] = url_match.group(1)

                    # 如果至少有名称或URL，则添加到结果中
                    if subreddit_info.get('name') or subreddit_info.get('url'):
                        subreddits.append(subreddit_info)

                except Exception as e:
                    print(f"Error parsing subreddit item: {e}")
                    continue

            # 去重
            unique_subreddits = []
            seen = set()

            for sub in subreddits:
                key = sub.get('name') or sub.get('url')
                if key and key not in seen:
                    seen.add(key)
                    unique_subreddits.append(sub)

            return {
                'subreddits': unique_subreddits,
                'nextPageUrl': next_page_url,
                'total': len(unique_subreddits)
            }

        except Exception as e:
            print(f"Error parsing subreddits: {e}")
            raise

    def search(self, q: str, type_: str = "communities", pages: int = 1) -> Dict[str, Union[List[Dict], int, List[float]]]:
        """
        搜索Reddit subreddits

        Args:
            q: 搜索关键词
            type_: 搜索类型，默认为"communities"
            pages: 请求页数，默认为1，最大10

        Returns:
            包含搜索结果、统计信息和请求耗时的字典
        """
        if not q:
            raise ValueError("Parameter q is required")

        if pages < 1 or pages > 10:
            raise ValueError("Pages parameter must be between 1 and 10")

        try:
            all_subreddits = []
            current_url = f"https://www.reddit.com/search/?q={requests.utils.quote(q)}&type={requests.utils.quote(type_)}"
            total_requests = 0
            request_durations = []  # 记录每次请求耗时（秒）

            for page in range(1, pages + 1):
                if not current_url:
                    break

                # 记录请求开始时间
                request_start_time = time.time()

                try:
                    response = requests.post(
                        self.base_url,
                        headers={
                            'Authorization': f'Bearer {self.api_key}',
                            'Content-Type': 'application/json'
                        },
                        json={
                            'method': 'GET',
                            'zone': 'web_unlocker1',
                            'url': current_url,
                            'format': 'raw',
                            'data_format': 'html',
                            'country': 'us'
                        },
                        timeout=30
                    )

                    total_requests += 1

                    # 记录请求结束时间并计算耗时
                    request_end_time = time.time()
                    duration = request_end_time - request_start_time
                    request_durations.append(round(duration, 3))

                    if not response.ok:
                        raise requests.RequestException(f"BrightData API request failed with status {response.status_code}")

                    # 直接获取HTML文本
                    html_content = response.text

                    if not html_content or html_content.strip() == '':
                        print(f"No HTML content found for page {page}")
                        break

                    # 解析HTML内容
                    parse_result = self.parse_subreddits(html_content)

                    # 去重合并到总结果中
                    for subreddit in parse_result['subreddits']:
                        exists = any(
                            existing.get('id') == subreddit.get('id') or
                            (existing.get('name') == subreddit.get('name') and
                             existing.get('url') == subreddit.get('url'))
                            for existing in all_subreddits
                        )
                        if not exists:
                            all_subreddits.append(subreddit)

                    # 更新下一页URL
                    current_url = parse_result['nextPageUrl']

                    # 如果没有下一页URL，停止请求
                    if not current_url:
                        print(f"No more pages available after page {page}")
                        break

                except requests.RequestException as e:
                    print(f"Error on page {page}: {e}")
                    break
                except Exception as e:
                    print(f"Error parsing page {page}: {e}")
                    break

            return {
                'subreddits': all_subreddits,
                'total': len(all_subreddits),
                'pagesRequested': pages,
                'pagesActuallyFetched': total_requests,
                'requestDurations': request_durations,  # 每次请求耗时数组
                'query': q,
                'type': type_
            }

        except Exception as e:
            print(f"Error calling BrightData API: {e}")
            raise


# 使用示例
if __name__ == "__main__":
    # 初始化搜索器
    searcher = RedditSearcher("key")

    try:
        # 搜索subreddits
        result = searcher.search("nextjs", "communities", 3)

        print(f"Found {result['total']} subreddits")
        print(f"Request durations: {result['requestDurations']} seconds")
        print(f"Pages fetched: {result['pagesActuallyFetched']}")

        # 显示前3个结果
        for i, subreddit in enumerate(result['subreddits'][:3]):
            print(f"\n{i+1}. r/{subreddit.get('name', 'Unknown')}")
            print(f"   URL: {subreddit.get('url', 'N/A')}")
            print(f"   Members: {subreddit.get('members', 'N/A')}")
            print(f"   Online: {subreddit.get('online', 'N/A')}")
            print(f"   Description: {subreddit.get('description', 'N/A')[:100]}...")

    except Exception as e:
        print(f"Search failed: {e}")
