# Eye Health Guide — Streamlit

기존 Eye Health Guide의 설문, 규칙 기반 위험도 계산, OpenAI 개인화 안내, 오늘의 quote, Supabase 결과 저장 기능을 하나의 Streamlit 앱으로 구성한 프로젝트입니다.

> 교육 및 인식 개선 목적으로만 사용합니다. 이 앱은 질병을 진단하거나 치료하지 않으며 전문적인 의료 조언과 종합 안과 검진을 대체하지 않습니다.

## 파일 구조

```text
eye-health-streamlit/
├─ app.py
├─ requirements.txt
├─ .gitignore
└─ README.md
```

## 1. 준비 사항

- Python 3.10 이상
- OpenAI API key
- 선택 사항: Supabase 프로젝트

Supabase를 사용하려면 다음 테이블이 필요합니다.

```sql
create table survey_responses (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz default now(),
  responses jsonb not null,
  risk jsonb not null,
  advice text,
  device_id text
);
```

## 2. 로컬 설치

Windows PowerShell에서 프로젝트 폴더로 이동한 뒤 실행합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

macOS 또는 Linux에서는 가상환경을 다음과 같이 활성화합니다.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. 비밀키 설정

비밀키를 `app.py`에 직접 입력하거나 GitHub에 올리지 마세요.

프로젝트 폴더 안에 `.streamlit/secrets.toml`을 만들고 다음 형식으로 입력합니다.

```toml
OPENAI_API_KEY = "새로-발급한-OpenAI-API-key"
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "새로-발급한-Supabase-service-role-key"
```

- `OPENAI_API_KEY`가 없으면 위험도는 계산되지만 개인화 안내 대신 임시 안내문이 표시됩니다.
- Supabase 설정 두 개가 없으면 앱은 결과를 저장하지 않고 계속 작동합니다.
- `.streamlit/secrets.toml`은 `.gitignore`에 포함되어 있습니다.
- 이전에 문서나 코드에 노출한 키가 있다면 해당 키를 폐기하고 새 키를 발급하세요.

환경변수를 직접 설정하는 방식도 지원합니다.

```text
OPENAI_API_KEY
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
```

## 4. 실행

```powershell
streamlit run app.py
```

브라우저가 자동으로 열리지 않으면 다음 주소에 접속합니다.

```text
http://localhost:8501
```

## 5. 사용 흐름

1. 소개 화면에서 `Start Survey` 선택
2. 설문 응답
3. `Submit & Get My Sheet` 선택
4. 규칙 기반 위험 수준, 점수 기여 항목, quote, 개인화 안내 확인
5. `Start Over`로 초기화

## 6. Streamlit Community Cloud 배포

1. 이 폴더를 GitHub 저장소에 업로드합니다.
2. [Streamlit Community Cloud](https://share.streamlit.io/)에서 저장소를 연결합니다.
3. 실행 파일을 `app.py`로 지정합니다.
4. 앱 설정의 Secrets에 로컬 `secrets.toml`과 같은 값을 입력합니다.
5. Deploy를 실행합니다.

GitHub에 올리기 전 반드시 아래 명령으로 비밀 파일이 제외되었는지 확인합니다.

```bash
git status
git check-ignore .streamlit/secrets.toml
```

## 참고

Expo 기반 네이티브 푸시 알림과 예약 발송 스크립트는 이 단일 Streamlit 웹앱에 포함하지 않았습니다. 앱을 열었을 때 결과와 오늘의 quote를 표시하는 기능은 포함되어 있습니다.
