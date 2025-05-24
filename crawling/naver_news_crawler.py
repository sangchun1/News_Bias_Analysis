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
import requests

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
        chrome_options.add_argument('--disable-software-rasterizer')  # WebGL 경고 억제
        chrome_options.add_argument('--disable-webgl')  # WebGL 비활성화
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])  # 로그 스위치 비활성화
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-extensions')  # 확장 프로그램 비활성화
        chrome_options.add_argument('--disable-popup-blocking')  # 팝업 차단 비활성화
        chrome_options.add_argument('--disable-infobars')  # 정보 표시줄 비활성화
        chrome_options.add_argument('--disable-notifications')  # 알림 비활성화
        chrome_options.add_argument('--disable-gpu-sandbox')  # GPU 샌드박스 비활성화
        chrome_options.add_argument('--no-first-run')  # 첫 실행 설정 건너뛰기
        chrome_options.add_argument('--no-default-browser-check')  # 기본 브라우저 확인 건너뛰기
        
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
                
            # 모바일 URL을 데스크톱 URL로 변환
            if 'n.news.naver.com/mnews' in current_url:
                article_id = current_url.split('/')[-1]
                oid = article_id.split('_')[0]
                aid = article_id.split('_')[1]
                desktop_url = f"https://news.naver.com/main/read.naver?mode=LSD&mid=sec&oid={oid}&aid={aid}"
                self.driver.get(desktop_url)
                time.sleep(2)
                
            # 카테고리 확인
            try:
                category = self.driver.find_element(By.CSS_SELECTOR, "a.category_link, a.media_end_head_category_link").text
                return "정치" in category
            except:
                pass
            
            # 제목이나 내용에서 정치 관련 키워드 확인
            try:
                title = self.driver.find_element(By.CSS_SELECTOR, "h2.media_end_head_headline, h3.tit_view").text
                content = self.driver.find_element(By.CSS_SELECTOR, "div#newsct_article, div#articeBody").text
                
                politics_keywords = ['정치', '대통령', '여야', '국회', '장관', '총리', '정부', '청와대', '여당', '야당']
                for keyword in politics_keywords:
                    if keyword in title or keyword in content:
                        return True
            except:
                pass
            
        except:
            return False
            
        return False
            
    def get_news_content(self):
        """뉴스 기사 내용 가져오기"""
        try:
            # 모바일 URL을 데스크톱 URL로 변환
            current_url = self.driver.current_url
            if 'n.news.naver.com/mnews' in current_url:
                # URL에서 oid와 aid 추출
                parts = current_url.split('/')
                oid = parts[-2]  # 028
                aid = parts[-1]  # 0002747473
                desktop_url = f"https://news.naver.com/main/read.naver?mode=LSD&mid=sec&oid={oid}&aid={aid}"
                # print(f"데스크톱 URL로 변환: {desktop_url}")
                self.driver.get(desktop_url)
                time.sleep(1)  # 2초에서 1초로 감소

            # 기본 정보 추출 - 명시적 대기 추가
            title = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h2.media_end_head_headline, h3.tit_view"))
            ).text

            # 본문 내용 추출 - 여러 선택자 시도
            content = None
            for selector in ["div#newsct_article", "div#articeBody", "div#articleBodyContents"]:
                try:
                    content = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    ).text
                    if content:
                        break
                except:
                    continue

            if not content:
                # print("본문 내용을 찾을 수 없습니다.")
                return None
            
            # 작성일시와 수정일시
            try:
                date_elements = self.driver.find_elements(By.CSS_SELECTOR, "span.media_end_head_info_datestamp_time, span.date, span.media_end_head_info_datestamp")
                # print(f"찾은 날짜 요소 수: {len(date_elements)}")
                created_date = date_elements[0].text if len(date_elements) > 0 else None
                modified_date = date_elements[1].text if len(date_elements) > 1 else None
            except Exception as e:
                # print(f"날짜 정보 추출 중 에러: {str(e)}")
                created_date = None
                modified_date = None
            
            # 기자 정보
            try:
                journalist = self.driver.find_element(By.CSS_SELECTOR, "em.media_end_head_journalist_name, span.writer, span.media_end_head_journalist").text
            except Exception as e:
                # print(f"기자 정보 추출 중 에러: {str(e)}")
                journalist = None
            
            # 댓글 수 추출
            try:
                comment_count = self.driver.find_element(By.CSS_SELECTOR, "a.media_end_head_cmtcount_button, a.cmt_count, span.media_end_head_cmtcount").text
                comment_count = int(re.sub(r'[^0-9]', '', comment_count))
            except Exception as e:
                # print(f"댓글 수 추출 중 에러: {str(e)}")
                comment_count = 0
            
            # 관련 기사 추출
            related_articles = []
            try:
                related_items = self.driver.find_elements(By.CSS_SELECTOR, "li.media_end_linked_item, li.related_item, div.media_end_head_related_news li")
                # print(f"찾은 관련 기사 수: {len(related_items)}")
                for item in related_items:
                    try:
                        related_title = item.find_element(By.CSS_SELECTOR, "a.media_end_linked_item_inner, a.related_tit, a").text
                        related_url = item.find_element(By.CSS_SELECTOR, "a.media_end_linked_item_inner, a.related_tit, a").get_attribute("href")
                        related_articles.append({
                            'title': related_title,
                            'url': related_url
                        })
                    except Exception as e:
                        # print(f"관련 기사 항목 처리 중 에러: {str(e)}")
                        continue
            except Exception as e:
                # print(f"관련 기사 추출 중 에러: {str(e)}")
                pass
            
            return {
                'title': title,
                'content': content,
                'created_date': created_date,
                'modified_date': modified_date,
                'journalist': journalist,
                'comment_count': comment_count,
                'related_articles': related_articles
            }
        except Exception as e:
            print(f"Error extracting news content: {str(e)}")
            print(f"현재 URL: {self.driver.current_url}")
            return None
            
    def crawl_press_news(self, press_name, start_date=None, end_date=None):
        """
        특정 언론사의 정치 뉴스를 크롤링하는 함수
        
        Args:
            press_name (str): 언론사 이름
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
        """
        # 날짜 형식 검증
        try:
            if start_date:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            print("날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.")
            return

        # 언론사 링크 찾기
        press_url = self.find_press_link(press_name)
        if not press_url:
            print(f"언론사 '{press_name}'를 찾을 수 없습니다.")
            return
            
        # 정치 섹션으로 이동
        politics_url = press_url + "&sid1=100"  # 정치 섹션 ID 추가
        self.driver.get(politics_url)
        # print(f"{press_name} 뉴스 페이지를 여는 중입니다...")
        time.sleep(1)  # 3초에서 1초로 감소
        
        news_data = []
        page_count = 1
        previous_date = None
        current_date = datetime.now()  # 초기 날짜 설정
        print("=" * 30)
        print(f"현재 페이지 날짜: {current_date.strftime('%Y-%m-%d')}")
        print("=" * 30)
        
        while True:
            try:
                # 시작 날짜와 비교 (같은 날짜도 포함)
                if start_date and current_date < start_datetime:
                    print(f"현재 날짜({current_date.strftime('%Y-%m-%d')})가 시작 날짜({start_date})보다 이전입니다. 크롤링을 종료합니다.")
                    break
                
                # 뉴스 목록 대기
                news_items = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.type06_headline li, ul.type06 li"))
                )
                
                print("-" * 30)
                print(f"현재 페이지: {page_count}")
                print(f"현재 페이지에서 {len(news_items)}개의 뉴스 항목을 찾았습니다.")
                print("-" * 30)
                
                # 현재 페이지의 뉴스 데이터 수집
                for item in news_items:
                    try:
                        # 뉴스 링크와 제목 찾기
                        news_link = item.find_element(By.CSS_SELECTOR, "dt:not(.photo) a")
                        title = news_link.text.strip()
                        news_url = news_link.get_attribute("href")
                        
                        if not title or not news_url:
                            # print("제목 또는 링크가 비어있어 건너뜁니다.")
                            continue
                            
                        # print(f"뉴스 제목: {title}")
                        # print(f"뉴스 링크: {news_url}")
                        
                        # 새 탭에서 뉴스 열기
                        self.driver.execute_script(f"window.open('{news_url}', '_blank');")
                        time.sleep(0.5)  # 2초에서 0.5초로 감소
                        
                        # 새 탭으로 전환
                        if len(self.driver.window_handles) <= 1:
                            # print("새 탭이 열리지 않았습니다.")
                            continue
                            
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        # print(f"새 탭으로 전환됨. 현재 URL: {self.driver.current_url}")
                        
                        # 페이지 로딩 대기
                        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                        
                        # 뉴스 내용 가져오기
                        news_info = self.get_news_content()
                        if news_info:
                            news_info['press'] = press_name
                            news_info['url'] = news_url
                            news_data.append(news_info)
                            print(f"[{len(news_data)}] {news_info['title']}")  # 진행 상황 표시는 유지
                        else:
                            print("뉴스 내용을 가져오지 못했습니다.")
                            pass
                            
                    except Exception as e:
                        if "invalid session id" in str(e):
                            print("브라우저 세션이 종료되었습니다. 재연결을 시도합니다...")
                            self.reconnect_browser()
                            # 현재 페이지부터 다시 시작
                            return self.crawl_press_news(press_name, start_date, end_date)
                        else:
                            print(f"에러 발생: {str(e)}")
                    finally:
                        # 탭이 열려있다면 닫기
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                
                # 다음 페이지 버튼 확인
                try:
                    # 다음 페이지 링크 찾기
                    next_page_link = self.driver.find_element(By.CSS_SELECTOR, f"div.paging a[href*='page={page_count + 1}']")
                    if next_page_link:
                        next_page_link.click()
                        time.sleep(1)  # 3초에서 1초로 감소
                        page_count += 1
                        # print(f"다음 페이지로 이동합니다...")
                    else:
                        print("다음 페이지가 없습니다.")
                        # 다음 날짜로 이동
                        current_url = self.driver.current_url
                        if 'date=' in current_url:
                            current_date_str = current_date.strftime('%Y%m%d')
                            next_date = current_date - timedelta(days=1)
                            next_date_str = next_date.strftime('%Y%m%d')
                            next_url = current_url.replace(f'date={current_date_str}', f'date={next_date_str}')
                            self.driver.get(next_url)
                            time.sleep(1)  # 3초에서 1초로 감소
                            page_count = 1
                            previous_date = current_date
                            current_date = next_date
                            print("=" * 30)
                            print(f"현재 페이지 날짜: {current_date.strftime('%Y-%m-%d')}")
                            print("=" * 30)
                        else:
                            # date 파라미터가 없는 경우 직접 추가
                            next_date = current_date - timedelta(days=1)
                            next_date_str = next_date.strftime('%Y%m%d')
                            if '?' in current_url:
                                next_url = f"{current_url}&date={next_date_str}"
                            else:
                                next_url = f"{current_url}?date={next_date_str}"
                            self.driver.get(next_url)
                            time.sleep(1)  # 3초에서 1초로 감소
                            page_count = 1
                            previous_date = current_date
                            current_date = next_date
                            print("=" * 30)
                            print(f"현재 페이지 날짜: {current_date.strftime('%Y-%m-%d')}")
                            print("=" * 30)
                except NoSuchElementException:
                    print("다음 페이지를 찾을 수 없습니다.")
                    # 다음 날짜로 이동
                    current_url = self.driver.current_url
                    if 'date=' in current_url:
                        current_date_str = current_date.strftime('%Y%m%d')
                        next_date = current_date - timedelta(days=1)
                        next_date_str = next_date.strftime('%Y%m%d')
                        next_url = current_url.replace(f'date={current_date_str}', f'date={next_date_str}')
                        self.driver.get(next_url)
                        time.sleep(1)  # 3초에서 1초로 감소
                        page_count = 1
                        previous_date = current_date
                        current_date = next_date
                        print("=" * 30)
                        print(f"현재 페이지 날짜: {current_date.strftime('%Y-%m-%d')}")
                        print("=" * 30)
                    else:
                        # date 파라미터가 없는 경우 직접 추가
                        next_date = current_date - timedelta(days=1)
                        next_date_str = next_date.strftime('%Y%m%d')
                        if '?' in current_url:
                            next_url = f"{current_url}&date={next_date_str}"
                        else:
                            next_url = f"{current_url}?date={next_date_str}"
                        self.driver.get(next_url)
                        time.sleep(1)  # 3초에서 1초로 감소
                        page_count = 1
                        previous_date = current_date
                        current_date = next_date
                        print("=" * 30)
                        print(f"현재 페이지 날짜: {current_date.strftime('%Y-%m-%d')}")
                        print("=" * 30)
                    
            except TimeoutException:
                print("페이지 로딩 시간 초과. 현재까지 수집된 데이터를 저장합니다.")
                break
                
        # DataFrame 생성 및 저장
        try:
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
                    'journalist', 'comment_count', 'related_titles', 'related_urls'
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
        except Exception as e:
            print(f"\n데이터 저장 중 오류 발생: {str(e)}")
            # 임시 파일로 저장 시도
            try:
                temp_filename = f"data/{press_name}_politics_news_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(temp_filename, index=False, encoding='utf-8-sig')
                print(f"임시 파일로 저장 완료: {temp_filename}")
            except Exception as e2:
                print(f"임시 파일 저장도 실패: {str(e2)}")
        
    def close(self):
        """브라우저 종료"""
        self.driver.quit() 
        
    def reconnect_browser(self):
        """브라우저 재연결"""
        try:
            self.driver.quit()
        except:
            pass
        self.__init__() 
        