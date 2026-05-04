import os
import requests
from bs4 import BeautifulSoup
import time

def download_decisions(limit=10):
    base_url = "https://www.pipc.go.kr/np/cop/bbs/selectBoardList.do?bbsId=BS074"
    download_prefix = "https://www.pipc.go.kr"
    save_dir = "./docs"
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    # 현재 docs 폴더에 있는 파일 목록 확인 (중복 방지)
    existing_files = os.listdir(save_dir)
    downloaded_count = 0

    # 게시판 첫 페이지 접속
    res = requests.get(base_url, headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    # 게시글 목록 찾기 (보안뉴스 때와 유사하게 구조 파악 필요)
    # 위원회 사이트 구조에 맞춰 tr 또는 td 선택자를 조정합니다.
    rows = soup.select('table.board_list tbody tr')

    for row in rows:
        if downloaded_count >= limit:
            break

        # 파일 다운로드 링크 찾기
        link_elem = row.select_one('a[href*="fileDown"]')
        if not link_elem: continue

        title = row.select_one('td.subject').get_text(strip=True).replace("/", "_")
        file_url = download_prefix + link_elem['href']
        file_name = f"{title}.pdf"

        # 이미 있으면 건너뜀
        if file_name in existing_files:
            continue

        # 다운로드 실행
        print(f"다운로드 중: {file_name}")
        file_res = requests.get(file_url, headers=headers)
        with open(os.path.join(save_dir, file_name), 'wb') as f:
            f.write(file_res.content)
        
        downloaded_count += 1
        time.sleep(2) # 사이트 부하 방지를 위한 매너 타임

    print(f"총 {downloaded_count}개의 새로운 결정문을 가져왔습니다.")

if __name__ == "__main__":
    download_decisions(limit=10)
