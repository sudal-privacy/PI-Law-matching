import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests

def download_decisions(limit=10):
    save_dir = "./docs"
    if not os.path.exists(save_dir): os.makedirs(save_dir)

    # 1. 크롬 브라우저 설정 (창이 안 뜨는 headless 모드)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # 2. 게시판 접속
        print("게시판 접속 중...")
        driver.get("https://www.pipc.go.kr/np/cop/bbs/selectBoardList.do?bbsId=BS074")
        time.sleep(5) # 충분히 대기

        # 3. 게시글 찾기
        links = driver.find_elements("css selector", "td.subject a")
        downloaded = 0
        
        # 상세 페이지 링크 미리 수집
        detail_urls = [link.get_attribute('href') for link in links[:20]]

        for url in detail_urls:
            if downloaded >= limit: break
            
            driver.get(url)
            time.sleep(3)
            
            # 4. 파일 다운로드 버튼 클릭 시도 또는 URL 추출
            try:
                file_link = driver.find_element("xpath", "//a[contains(@href, 'fileDown.do')]")
                file_url = file_link.get_attribute('href')
                file_name = driver.find_element("css selector", "div.file_list li a").text.strip()
                
                if file_name in os.listdir(save_dir):
                    print(f"이미 존재: {file_name}")
                    continue

                print(f"다운로드 시작: {file_name}")
                # 세션 유지를 위해 브라우저 쿠키를 가지고 다운로드
                cookies = driver.get_cookies()
                s = requests.Session()
                for cookie in cookies:
                    s.cookies.set(cookie['name'], cookie['value'])
                
                res = s.get(file_url)
                with open(os.path.join(save_dir, file_name), 'wb') as f:
                    f.write(res.content)
                
                downloaded += 1
            except:
                continue

    finally:
        driver.quit()

if __name__ == "__main__":
    download_decisions(limit=10)
