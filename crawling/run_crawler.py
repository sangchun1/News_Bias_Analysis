from naver_news_crawler import NaverNewsCrawler
from datetime import datetime, timedelta
import sys

def main():
    # 크롤러 인스턴스 생성
    crawler = NaverNewsCrawler()
    
    try:
        # 사용자 입력 받기
        print("\n=== 네이버 뉴스 크롤러 ===")
        print("크롤링할 언론사와 날짜를 입력해주세요.")
        print("(날짜를 입력하지 않으면 어제 날짜부터 크롤링합니다)")
        print("=" * 30)
        
        # 언론사 이름 입력
        press_name = input("\n언론사 이름을 입력하세요: ")
        
        # 시작 날짜 입력
        start_date = input("시작 날짜를 입력하세요 (YYYY-MM-DD, 생략 가능): ").strip()
        if not start_date:
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
        # 종료 날짜는 오늘로 설정
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n크롤링 설정:")
        print(f"- 언론사: {press_name}")
        print(f"- 기간: {start_date} ~ {end_date}")
        
        # 크롤링 실행
        crawler.crawl_press_news(press_name, start_date, end_date)
        
    except KeyboardInterrupt:
        print("\n크롤링이 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        # 브라우저 종료
        crawler.close()

if __name__ == "__main__":
    main() 