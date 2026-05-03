# envto – .env 파일 관리 CLI

**envto**는 프로젝트 디렉터리 안에 있는 `.env` 파일을 SQLite3 데이터베이스에 저장하고, 필요할 때 쉽게 복원하거나 확인할 수 있게 해 주는 아주 작은 CLI 도구입니다.  
Python 3.14 이상과 **uv** 패키지 매니저, 그리고 `fzf`(터미널 fuzzy finder)만 있으면 동작합니다.

---

## 📦 개요
| 기능 | 설명 |
|------|------|
| **save** | 지정 디렉터리(또는 현재 작업 디렉터리)의 `.env` 를 DB에 저장합니다. ID는 `<부모디렉터리명>.env` 로 자동 생성됩니다. |
| **load** | 저장된 레코드 중 하나를 `fzf` 로 선택하고, 현재 디렉터리에 `.env` 로 복원합니다. 기존 파일이 있으면 `.{YYYYMMDDHHMMSS}-env` 형태로 백업합니다. |
| **view** | 저장된 레코드 중 하나를 `fzf` 로 선택하고, 터미널에 내용과 메타 정보를 출력합니다. |

데이터베이스는 `~/.local/share/envto/envto.db`에 위치하며, 테이블 스키마는 아래와 같습니다.

```sql
CREATE TABLE IF NOT EXISTS envs (
    id TEXT PRIMARY KEY,      -- <parent‑dir>.env
    path TEXT NOT NULL,      -- .env 파일이 있던 절대 경로
    env TEXT NOT NULL,       -- 파일 전체 텍스트
    update_dt TEXT NOT NULL  -- UTC ISO‑8601 타임스탬프
);
-- Composite index for faster look‑ups by id + path
CREATE INDEX IF NOT EXISTS idx_envs_id_path ON envs (id, path);
```

---

## 🛠️ 설치·설정
### 1️⃣ uv 설치 (한 번만 수행)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS / Linux
# Windows PowerShell:
# iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex
```

### 2️⃣ 프로젝트 루트에서 가상 환경 만들기
```bash
cd /path/to/envto               # <--- 현재 레포지터리 루트
uv venv .venv                  # .venv 디렉터리 생성
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate      # Windows PowerShell
```

### 3️⃣ 의존 패키지 설치 (editable mode)
```bash
uv pip install -e .
```
`pyproject.toml`에 정의된 `typer>=0.25.1`이 설치됩니다.

### 4️⃣ 콘솔 스크립트 확인 (설치 후 자동 생성)
```bash
which envto   # ~/.local/bin/envto (또는 venv 내부 bin 디렉터리)
envto --help  # Typer 기반 헬프가 출력됩니다.
```
> **fzf** 가 설치돼 있지 않다면 `brew install fzf` (macOS) 혹은 `sudo apt-get install fzf` (Ubuntu) 로 미리 설치해 주세요.

---

## 🚀 사용 예시
### 1️⃣ 현재 디렉터리 `.env` 저장
```bash
envto save          # .env 가 있으면 DB에 저장
```

### 2️⃣ 지정 디렉터리 `.env` 저장
```bash
envto save -p /my/project
```

### 3️⃣ 저장된 파일 조회·로드
```bash
# 레코드 선택 후 현재 폴더에 .env 쓰기 (백업 자동)
envto load

# 레코드 선택 후 내용만 확인
envto view
```
출력 예시 (`envto view`):
```
# ID   : myapp.env
# Path : /Users/me/projects/myapp
# ==============================================================
DB_HOST=postgres
DB_PORT=5432
SECRET_KEY=super‑secret
```

---

## 📄 프로젝트 구조
```
envto/
├─ src/
│  └─ envto/
│     ├─ __init__.py
│     ├─ cli.py          # Typer 기반 CLI (위에서 설명한 서브‑커맨드)
│     └─ db.py           # SQLite3 래퍼
├─ pyproject.toml        # 패키지 메타데이터·uv 설정
├─ README.md             # 현재 문서
└─ uv.lock               # uv lock 파일 (재현 가능)
```

---

## 🧩 확장 아이디어
* **delete** ‑ 레코드 삭제
* **export‑json** ‑ 모든 레코드를 JSON 파일로 내보내기
* **search** ‑ 키워드 기반 레코드 검색
* **auto‑backup** ‑ `.env` 파일을 저장할 때 이전 버전을 자동으로 보관

이러한 기능은 `src/envto/cli.py`에 새로운 `@app.command()` 를 추가하고 `db.py`에 적절한 쿼리를 구현하면 바로 사용할 수 있습니다.

---

## 📜 라이선스
MIT License – 자유롭게 사용·수정·배포 가능합니다.

---

## 🙋‍♂️ 문의·기여
버그 리포트, 기능 제안, 풀 리퀘스트는 언제든 환영합니다.

```bash
# 개발 환경 재현 (다른 머신에서)
uv sync   # pyproject.toml·uv.lock 기반 설치
```
