import os
import github
from law_assistant import run_law_assistant # 아까 만든 AI 엔진 호출

def main():
    # GitHub 토큰 및 환경 변수 가져오기
    token = os.environ.get("GITHUB_TOKEN")
    issue_number = int(os.environ.get("ISSUE_NUMBER"))
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    
    g = github.Github(token)
    repo = g.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)
    
    # 사용자의 질문 추출
    user_query = issue.body if issue.body else issue.title
    print(f"질문 수신: {user_query}")
    
    # AI 엔진 구동 (PDF 기반 답변 생성)
    try:
        answer = run_law_assistant(user_query)
        # 이슈에 댓글 달기
        issue.create_comment(f"### 🤖 개보위 결정문 분석 답변\n\n{answer}")
        print("답변 완료!")
    except Exception as e:
        issue.create_comment(f"❌ 에러 발생: {str(e)}")

if __name__ == "__main__":
    main()
