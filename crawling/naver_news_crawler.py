from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, timedelta
import re
import os
import json

class NaverNewsCrawler:
    def __init__(self):
        # Chrome 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 브라우저 창 숨기기
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--log-level=3')  # 로그 레벨을 최소화
        chrome_options.add_argument('--silent')  # 로그 출력 억제
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])  # 로그 스위치 비활성화
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 웹드라이버 설정
        service = Service()
        self.driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        self.wait = WebDriverWait(self.driver, 20)
        
    def find_press_link(self, press_name):
        """언론사 이름으로 링크 찾기"""
        try:
            # 언론사 ID 매핑
            press_ids = {
                # 신문사
                '한겨레': '028',
                '조선일보': '023',
                '중앙일보': '025',
                '동아일보': '020',
                '경향신문': '032',
                '한국일보': '469',
                '서울신문': '081',
                '세계일보': '022',
                '문화일보': '021',
                '국민일보': '005',
                '매일신문': '088',
                '부산일보': '082',
                '전북일보': '087',
                '전주일보': '086',
                '강원일보': '085',
                '대구일보': '084',
                '광주일보': '083',
                '제주일보': '089',
                '경남일보': '090',
                '경북일보': '091',
                
                # 방송사
                'KBS': '056',
                'MBC': '214',
                'SBS': '055',
                'YTN': '052',
                '채널A': '277',
                'TV조선': '448',
                'MBN': '057',
                '연합뉴스TV': '422',
                'CBS': '079',
                'BBS': '078',
                'TBS': '077',
                'OBS': '353',
                'G1': '076',
                'KNN': '075',
                'TJB': '074',
                'JTV': '073',
                'KBC': '072',
                'JIBS': '071',
                'KBSN': '070',
                'KBS WORLD': '069',
                
                # 통신사
                '연합뉴스': '001',
                '뉴시스': '003',
                '뉴스1': '421',
                '뉴스타운': '006',
                '아시아경제': '277',
                '매일경제': '009',
                '한국경제': '015',
                '파이낸셜뉴스': '014',
                '서울경제': '011',
                '헤럴드경제': '016',
                '이데일리': '018',
                '머니투데이': '008',
                '아시아투데이': '007',
                '디지털타임스': '029',
                '전자신문': '030',
                'ZDNet Korea': '092',
                '테크홀릭': '093',
                'IT조선': '094',
                'IT동아': '095',
                'IT월드': '096'
            }
            
            if press_name in press_ids:
                press_id = press_ids[press_name]
                return f"https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid={press_id}"
            
            # ID가 없는 경우 기존 방식으로 검색
            self.driver.get("https://news.naver.com/main/officeList.naver")
            time.sleep(2)
            
            # 언론사 링크 찾기
            press_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='mode=LPOD']")
            for link in press_links:
                if press_name in link.text:
                    return link.get_attribute('href')
            
            return None
            
        except Exception as e:
            print(f"언론사 링크 찾기 실패: {e}")
            return None
        
    def is_politics_news(self):
        """현재 페이지가 정치 뉴스인지 확인"""
        try:
            # URL에서 정치 섹션 확인
            current_url = self.driver.current_url
            if 'sid1=100' in current_url:  # 정치 섹션 ID
                return True
                
            # 카테고리 확인
            try:
                category = self.driver.find_element(By.CSS_SELECTOR, "a.category_link").text
                return "정치" in category
            except:
                pass
                
            # 본문 내용에서 정치 관련 키워드 확인
            content = self.driver.find_element(By.CSS_SELECTOR, "div#newsct_article").text
            politics_keywords = ['정치', '대통령', '국회', '여야', '여당', '야당', '장관', '총리']
            return any(keyword in content for keyword in politics_keywords)
            
        except:
            return False
            
    def get_news_content(self):
        """뉴스 기사 내용 가져오기"""
        try:
            # 기본 정보 추출
            title = self.driver.find_element(By.CSS_SELECTOR, "h2.media_end_head_headline, h3.tit_view").text
            content = self.driver.find_element(By.CSS_SELECTOR, "div#newsct_article, div#articeBody").text
            
            # 작성일시와 수정일시
            date_elements = self.driver.find_elements(By.CSS_SELECTOR, "span.media_end_head_info_datestamp_time, span.date")
            created_date = date_elements[0].text if len(date_elements) > 0 else None
            modified_date = date_elements[1].text if len(date_elements) > 1 else None
            
            # 기자 정보
            try:
                journalist = self.driver.find_element(By.CSS_SELECTOR, "em.media_end_head_journalist_name, span.writer").text
            except:
                journalist = None
            
            # 이미지 URL 추출
            try:
                image_url = self.driver.find_element(By.CSS_SELECTOR, "img.end_photo_org, img.news_end_photo").get_attribute("src")
            except:
                image_url = None
            
            # 댓글 수 추출
            try:
                comment_count = self.driver.find_element(By.CSS_SELECTOR, "a.media_end_head_cmtcount_button, a.cmt_count").text
                comment_count = int(re.sub(r'[^0-9]', '', comment_count))
            except:
                comment_count = 0
            
            # 관련 기사 추출
            related_articles = []
            try:
                related_items = self.driver.find_elements(By.CSS_SELECTOR, "li.media_end_linked_item, li.related_item")
                for item in related_items:
                    try:
                        related_title = item.find_element(By.CSS_SELECTOR, "a.media_end_linked_item_inner, a.related_tit").text
                        related_url = item.find_element(By.CSS_SELECTOR, "a.media_end_linked_item_inner, a.related_tit").get_attribute("href")
                        related_articles.append({
                            'title': related_title,
                            'url': related_url
                        })
                    except:
                        continue
            except:
                pass
            
            return {
                'title': title,
                'content': content,
                'created_date': created_date,
                'modified_date': modified_date,
                'journalist': journalist,
                'image_url': image_url,
                'comment_count': comment_count,
                'related_articles': related_articles
            }
        except Exception as e:
            print(f"Error extracting news content: {e}")
            return None
            
    def crawl_press_news(self, press_name, start_date=None, end_date=None):
        """
        특정 언론사의 정치 뉴스를 크롤링하는 함수
        
        Args:
            press_name (str): 언론사 이름
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
        """
        # 언론사 링크 찾기
        press_url = self.find_press_link(press_name)
        if not press_url:
            print(f"언론사 '{press_name}'를 찾을 수 없습니다.")
            return
            
        # 정치 섹션으로 이동
        politics_url = press_url + "&sid1=100"  # 정치 섹션 ID 추가
        self.driver.get(politics_url)
        time.sleep(3)
        
        news_data = []
        page = 1
        
        while True:
            try:
                # 뉴스 목록 대기
                news_items = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.type06_headline li, ul.type06 li"))
                )
                
                # 현재 페이지의 뉴스 데이터 수집
                for item in news_items:
                    try:
                        # 뉴스 링크 찾기
                        news_link = item.find_element(By.CSS_SELECTOR, "dt a")
                        news_url = news_link.get_attribute("href")
                        
                        # 새 탭에서 뉴스 열기
                        self.driver.execute_script(f"window.open('{news_url}', '_blank');")
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        time.sleep(2)
                        
                        # 정치 뉴스인지 확인
                        if self.is_politics_news():
                            news_info = self.get_news_content()
                            if news_info:
                                news_info['press'] = press_name
                                news_info['url'] = news_url
                                news_data.append(news_info)
                                print(f"[{len(news_data)}] {news_info['title']}")
                        
                        # 탭 닫고 원래 탭으로 돌아가기
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        
                    except Exception as e:
                        # 탭이 열려있다면 닫기
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                        continue
                
                # 다음 페이지 버튼 확인
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "a.btn_next, a.next")
                    if "disabled" in next_button.get_attribute("class"):
                        break
                    next_button.click()
                    time.sleep(3)
                    page += 1
                    print(f"\n=== {page}페이지 크롤링 중... ===")
                except NoSuchElementException:
                    break
                    
            except TimeoutException:
                print("페이지 로딩 시간 초과. 현재까지 수집된 데이터를 저장합니다.")
                break
                
        # DataFrame 생성 및 저장
        if news_data:
            # 관련 기사 정보를 별도의 컬럼으로 분리
            for news in news_data:
                if 'related_articles' in news:
                    related_titles = [article['title'] for article in news['related_articles']]
                    related_urls = [article['url'] for article in news['related_articles']]
                    news['related_titles'] = '|'.join(related_titles)
                    news['related_urls'] = '|'.join(related_urls)
                    del news['related_articles']
            
            df = pd.DataFrame(news_data)
            
            # 컬럼 순서 지정
            columns = [
                'title', 'content', 'press', 'url', 'created_date', 'modified_date',
                'journalist', 'image_url', 'comment_count', 'related_titles', 'related_urls'
            ]
            df = df[columns]
            
            # data 디렉토리가 없으면 생성
            os.makedirs('data', exist_ok=True)
            
            # 파일명에 날짜 포함
            filename = f"data/{press_name}_politics_news_{start_date}_to_{end_date}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n크롤링 완료: {len(news_data)}개의 정치 뉴스가 {filename}에 저장되었습니다.")
        else:
            print("\n수집된 정치 뉴스가 없습니다.")
        
    def close(self):
        """브라우저 종료"""
        self.driver.quit()

if __name__ == "__main__":
    # 크롤러 인스턴스 생성
    crawler = NaverNewsCrawler()
    
    # 언론사 이름 입력 받기
    press_name = input("크롤링할 언론사 이름을 입력하세요: ")
    
    try:
        # 크롤링 실행
        crawler.crawl_press_news(press_name)
    finally:
        # 브라우저 종료
        crawler.close() 