import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(
    page_title="SQL 교육자료 | 주택금융",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .section-header {
        font-size: 1.7rem; font-weight: 800; color: #1a1a2e;
        border-bottom: 3px solid #1565C0;
        padding-bottom: 0.4rem; margin-bottom: 1.2rem;
    }
    .tip-box {
        background: #E3F2FD; border-left: 4px solid #1565C0;
        padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.6rem 0;
    }
    .warn-box {
        background: #FFF8E1; border-left: 4px solid #F9A825;
        padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.6rem 0;
    }
    .good-box {
        background: #E8F5E9; border-left: 4px solid #2E7D32;
        padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.6rem 0;
    }
    .syntax-box {
        background: #F3E5F5; border-left: 4px solid #6A1B9A;
        padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.6rem 0;
        font-family: monospace; font-size: 0.92rem; line-height: 1.7;
    }
    .quiz-box {
        background: #FFF3E0; border: 2px dashed #FB8C00;
        padding: 1rem 1.2rem; border-radius: 10px; margin: 0.8rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# DB 초기화
# ══════════════════════════════════════════════════════════════
@st.cache_resource
def get_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.executescript("""
        CREATE TABLE regions (
            region_id   INTEGER PRIMARY KEY,
            region_name TEXT NOT NULL,
            region_type TEXT
        );
        CREATE TABLE loan_guarantee (
            guarantee_id     INTEGER PRIMARY KEY,
            guarantee_no     TEXT NOT NULL,
            base_year        INTEGER NOT NULL,
            region_id        INTEGER,
            product_type     TEXT,
            supply_count     INTEGER,
            guarantee_amount REAL,
            FOREIGN KEY (region_id) REFERENCES regions(region_id)
        );
        CREATE TABLE housing_pension (
            pension_id      INTEGER PRIMARY KEY,
            base_year       INTEGER NOT NULL,
            region_id       INTEGER,
            join_count      INTEGER,
            pension_payment REAL,
            avg_house_price REAL,
            FOREIGN KEY (region_id) REFERENCES regions(region_id)
        );

        INSERT INTO regions VALUES
            (1,'서울','수도권'),(2,'경기','수도권'),(3,'인천','수도권'),
            (4,'부산','지방'),(5,'대구','지방'),(6,'광주','지방'),
            (7,'대전','지방'),(8,'강원','지방');

        INSERT INTO loan_guarantee VALUES
            (1,'G-2020-0001',2020,1,'전세',12400,1850.5),
            (2,'G-2020-0002',2020,1,'구입',8200,3120.0),
            (3,'G-2020-0003',2020,1,'중도금',5100,2340.0),
            (4,'G-2020-0004',2020,2,'전세',18700,2100.0),
            (5,'G-2020-0005',2020,2,'구입',11500,4200.0),
            (6,'G-2020-0006',2020,3,'전세',5800,980.0),
            (7,'G-2020-0007',2020,4,'전세',4200,540.0),
            (8,'G-2020-0008',2020,4,'구입',2900,870.0),
            (9,'G-2021-0001',2021,1,'전세',13200,2050.0),
            (10,'G-2021-0002',2021,1,'구입',9100,3560.0),
            (11,'G-2021-0003',2021,1,'전세대출',22000,4100.0),
            (12,'G-2021-0004',2021,2,'전세',20100,2450.0),
            (13,'G-2021-0005',2021,2,'구입',13200,5100.0),
            (14,'G-2021-0006',2021,3,'전세',6400,1100.0),
            (15,'G-2021-0007',2021,5,'전세',3100,420.0),
            (16,'G-2021-0008',2021,6,'구입',1800,510.0),
            (17,'G-2022-0001',2022,1,'전세',11800,1920.0),
            (18,'G-2022-0002',2022,1,'구입',8600,3300.0),
            (19,'G-2022-0003',2022,1,'전세대출',25000,4800.0),
            (20,'G-2022-0004',2022,2,'전세',19200,2280.0),
            (21,'G-2022-0005',2022,2,'중도금',8400,3100.0),
            (22,'G-2022-0006',2022,4,'전세',4500,580.0),
            (23,'G-2022-0007',2022,7,'전세',2100,310.0),
            (24,'G-2022-0008',2022,8,'구입',980,220.0),
            (25,'G-2023-0001',2023,1,'전세',10500,1750.0),
            (26,'G-2023-0002',2023,1,'구입',7800,3050.0),
            (27,'G-2023-0003',2023,1,'전세대출',27500,5200.0),
            (28,'G-2023-0004',2023,2,'전세',17900,2100.0),
            (29,'G-2023-0005',2023,2,'구입',12100,4800.0),
            (30,'G-2023-0006',2023,3,'전세',5200,920.0),
            (31,'G-2023-0007',2023,5,'구입',2400,680.0),
            (32,'G-2023-0008',2023,6,'전세',1900,280.0);

        INSERT INTO housing_pension VALUES
            (1,2020,1,18200,9840.0,4.2),(2,2020,2,12400,5210.0,3.1),
            (3,2020,3,4100,1580.0,2.4),(4,2020,4,5800,1940.0,2.1),
            (5,2020,5,3200,980.0,1.9),(6,2020,6,2100,620.0,1.7),
            (7,2021,1,21500,12100.0,4.5),(8,2021,2,15100,6540.0,3.4),
            (9,2021,3,5200,2010.0,2.6),(10,2021,4,6700,2340.0,2.2),
            (11,2021,5,3800,1180.0,2.0),(12,2021,7,2900,890.0,1.8),
            (13,2022,1,24100,14200.0,4.8),(14,2022,2,17800,7900.0,3.7),
            (15,2022,3,6100,2480.0,2.8),(16,2022,4,7500,2710.0,2.3),
            (17,2022,6,2500,760.0,1.8),(18,2022,8,1200,350.0,1.5),
            (19,2023,1,26800,16500.0,5.1),(20,2023,2,19500,9100.0,3.9),
            (21,2023,3,6900,2850.0,3.0),(22,2023,4,8200,3020.0,2.5),
            (23,2023,5,4500,1420.0,2.1),(24,2023,7,3100,980.0,1.9);
    """)
    conn.commit()
    return conn


def run_sql(conn, sql):
    try:
        df = pd.read_sql_query(sql, conn)
        return df, None
    except Exception as e:
        return None, str(e)


def show_result(conn, sql, key):
    if st.button("▶ 실행", key=key):
        df, err = run_sql(conn, sql)
        if err:
            st.error(f"오류: {err}")
        else:
            st.success(f"✅ {len(df)}행 반환")
            st.dataframe(df, use_container_width=True, hide_index=True)


def practice_block(conn, question, answer_sql, key_prefix, hint=None):
    """문제 → 직접 입력 → 실행 → 정답 비교"""
    st.markdown(f'<div class="quiz-box">🎯 <b>실습 문제</b><br>{question}</div>',
                unsafe_allow_html=True)
    if hint:
        with st.expander("💡 힌트 보기"):
            st.info(hint)
    user_sql = st.text_area("SQL 직접 작성", height=120, key=f"{key_prefix}_input",
                             placeholder="여기에 SQL을 작성해보세요...")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("▶ 내 답안 실행", key=f"{key_prefix}_run", type="primary"):
            if user_sql.strip():
                df, err = run_sql(conn, user_sql)
                if err:
                    st.error(f"오류: {err}")
                else:
                    st.success(f"✅ {len(df)}행 반환")
                    st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning("SQL을 입력해주세요.")
    with col2:
        if st.button("📋 정답 보기", key=f"{key_prefix}_ans"):
            st.markdown('<div class="good-box">✅ <b>정답 쿼리</b></div>',
                        unsafe_allow_html=True)
            st.code(answer_sql, language="sql")
            df, err = run_sql(conn, answer_sql)
            if not err:
                st.caption(f"정답 결과 — {len(df)}행")
                st.dataframe(df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════════════════════════
SECTIONS = [
    "🏠 개요 & 학습 순서",
    "📖 SQL 기본 문법",
    "🛠️ 실습 환경 구축",
    "① SELECT — 데이터 조회",
    "② WHERE — 조건 필터",
    "③ LIKE — 패턴 검색",
    "④ ORDER BY — 정렬",
    "⑤ GROUP BY — 집계",
    "⑥ JOIN — 테이블 결합",
    "🚀 복합 쿼리 실전",
    "✏️ 자유 실습 & 연습과제",
]

with st.sidebar:
    st.title("🏠 SQL 교육자료")
    st.caption("주택금융 데이터로 배우는 ANSI SQL")
    st.divider()
    st.markdown("""
**📚 학습 단계**

STEP 1. 개요 & 기본 문법
STEP 2. 실습 환경 구축
STEP 3. SELECT → WHERE → LIKE
STEP 4. ORDER BY → GROUP BY → JOIN
STEP 5. 복합 쿼리 & 자유 실습
""")
    st.divider()
    section = st.radio("단원 선택", SECTIONS, label_visibility="collapsed")

conn = get_db()


# ══════════════════════════════════════════════════════════════
# 0. 개요
# ══════════════════════════════════════════════════════════════
if section == SECTIONS[0]:
    st.markdown('<div class="section-header">🏠 SQL 교육자료 — 주택금융 데이터로 배우는 ANSI SQL</div>',
                unsafe_allow_html=True)
    st.markdown("이 자료는 **주택금융 업무 데이터**(기준연도·보증번호·공급건수·연금지급액 등)를 예시로 SQL을 단계별로 익힙니다.")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
### 📋 학습 순서
| 단계 | 내용 |
|------|------|
| **STEP 1** | SQL이란? 기본 문법 구조 |
| **STEP 2** | 실습 환경 구축 & 데이터 확인 |
| **STEP 3** | SELECT / WHERE / LIKE |
| **STEP 4** | ORDER BY / GROUP BY / JOIN |
| **STEP 5** | 복합 쿼리 & 자유 실습 |
        """)
    with col2:
        st.markdown("""
### 🗂️ 실습 데이터
| 테이블 | 내용 |
|--------|------|
| `regions` | 지역 마스터 (8개 지역) |
| `loan_guarantee` | 주택보증 (보증번호·공급건수·보증금액) |
| `housing_pension` | 주택연금 (가입건수·연금지급액) |
        """)
    st.divider()
    st.markdown("### 🔑 핵심 SQL 키워드")
    kw_cols = st.columns(6)
    kw_data = [("SELECT","조회","#1565C0"),("WHERE","조건","#2E7D32"),
               ("LIKE","패턴","#6A1B9A"),("ORDER BY","정렬","#E65100"),
               ("GROUP BY","집계","#AD1457"),("JOIN","결합","#00695C")]
    for col, (kw, desc, color) in zip(kw_cols, kw_data):
        col.markdown(f"""<div style="background:{color};color:white;border-radius:10px;
            padding:18px 8px;text-align:center;">
            <div style="font-size:1rem;font-weight:700;">{kw}</div>
            <div style="font-size:0.8rem;opacity:0.9;">{desc}</div></div>""",
            unsafe_allow_html=True)
    st.divider()
    st.markdown("""<div class="tip-box">💡 <b>활용법</b> — 각 예제의 <b>▶ 실행</b> 버튼으로 결과를 확인하고,
    <b>🎯 실습 문제</b>에서 직접 SQL을 작성한 뒤 <b>📋 정답 보기</b>로 비교해보세요.</div>""",
    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 1. SQL 기본 문법
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[1]:
    st.markdown('<div class="section-header">📖 SQL 기본 문법</div>', unsafe_allow_html=True)

    st.markdown("## SQL이란?")
    st.markdown("""
**SQL(Structured Query Language)** 은 관계형 데이터베이스(RDBMS)에서 데이터를 **조회·삽입·수정·삭제**하기 위한 표준 언어입니다.

관계형 DB는 데이터를 **테이블(표)** 형태로 저장하고, 여러 테이블을 **관계(Relation)** 로 연결해 관리합니다.
SQL은 이 테이블들을 대상으로 원하는 데이터를 뽑아내는 질의(Query)를 작성하는 언어입니다.

- **표준화**: ANSI/ISO SQL 표준이 존재하며 Oracle·MySQL·PostgreSQL·SQLite 등 거의 모든 DB에서 동일하게 동작합니다.
- **선언적 언어**: "어떻게(HOW)"가 아닌 "무엇을(WHAT)" 원하는지 기술하면 DB 엔진이 최적의 방법으로 실행합니다.
    """)

    st.divider()
    st.markdown("## SQL 명령어 분류")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div style="background:#E3F2FD;border-radius:10px;padding:16px;">
        <b>📥 DML — 데이터 조작</b><br><small>Data Manipulation Language</small><br><br>
        • <code>SELECT</code> — 데이터 조회<br>
        • <code>INSERT</code> — 데이터 삽입<br>
        • <code>UPDATE</code> — 데이터 수정<br>
        • <code>DELETE</code> — 데이터 삭제<br><br>
        <small>⭐ 이 자료에서 집중적으로 다룹니다</small></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div style="background:#F3E5F5;border-radius:10px;padding:16px;">
        <b>🏗️ DDL — 데이터 정의</b><br><small>Data Definition Language</small><br><br>
        • <code>CREATE</code> — 테이블 생성<br>
        • <code>ALTER</code> — 구조 변경<br>
        • <code>DROP</code> — 테이블 삭제<br>
        • <code>TRUNCATE</code> — 전체 삭제</div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div style="background:#E8F5E9;border-radius:10px;padding:16px;">
        <b>🔐 DCL — 데이터 제어</b><br><small>Data Control Language</small><br><br>
        • <code>GRANT</code> — 권한 부여<br>
        • <code>REVOKE</code> — 권한 회수<br>
        • <code>COMMIT</code> — 트랜잭션 확정<br>
        • <code>ROLLBACK</code> — 트랜잭션 취소</div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("## SELECT 전체 문법 구조")
    st.code("""-- [ ] 안은 선택 요소 (생략 가능)
SELECT   [DISTINCT] 컬럼1, 컬럼2, 집계함수, ...   -- ⑥ 여섯 번째 실행
FROM     테이블명  [AS 별칭]                        -- ① 가장 먼저 실행
[JOIN    다른테이블  ON 조인조건]                    -- ②
[WHERE   행 필터 조건]                              -- ③ 집계 전 필터
[GROUP BY 그룹 기준 컬럼]                           -- ④
[HAVING  집계 결과 필터]                            -- ⑤ 집계 후 필터
[ORDER BY 정렬 컬럼  [ASC|DESC]]                   -- ⑦
[LIMIT   n];                                       -- ⑧""", language="sql")

    st.markdown("""<div class="warn-box">⚠️ <b>SQL 실행 순서는 작성 순서와 다릅니다!</b><br><br>
    작성 순서: SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY<br>
    실행 순서: FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY<br><br>
    이 차이가 중요한 이유: WHERE는 GROUP BY 이전에 실행되기 때문에,
    WHERE 절에서는 집계함수(SUM, AVG 등)를 사용할 수 없습니다.
    집계 결과를 필터링하려면 반드시 HAVING을 사용해야 합니다.</div>""",
    unsafe_allow_html=True)

    st.divider()
    st.markdown("## 주요 데이터 타입 & 핵심 개념")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
| 타입 | 설명 | 실습 예시 |
|------|------|-----------|
| `INTEGER` | 정수 | 공급건수, 기준연도 |
| `REAL` / `FLOAT` | 실수 | 보증금액, 연금지급액 |
| `TEXT` / `VARCHAR` | 문자열 | 보증번호, 지역명 |
| `DATE` | 날짜 | '2023-01-01' |
        """)
    with col2:
        st.markdown("""
| 개념 | 설명 |
|------|------|
| `NULL` | 값이 없음 (0·빈 문자열과 전혀 다름) |
| `PRIMARY KEY (PK)` | 각 행을 유일하게 식별하는 컬럼 |
| `FOREIGN KEY (FK)` | 다른 테이블의 PK를 참조하는 컬럼 |
| `AS (Alias)` | 컬럼·테이블에 읽기 쉬운 별칭 부여 |
| `DISTINCT` | 중복된 행 제거 |
        """)

    st.divider()
    st.markdown("## 연산자 & 집계함수")
    tab1, tab2, tab3 = st.tabs(["비교 연산자", "논리 연산자", "집계 함수"])
    with tab1:
        st.markdown("""
| 연산자 | 의미 | 예시 |
|--------|------|------|
| `=` | 같다 | `base_year = 2023` |
| `<>` 또는 `!=` | 다르다 | `product_type <> '전세'` |
| `>` / `<` | 크다 / 작다 | `supply_count > 10000` |
| `>=` / `<=` | 이상 / 이하 | `base_year >= 2022` |
| `BETWEEN a AND b` | a 이상 b 이하 (양 끝 포함) | `supply_count BETWEEN 5000 AND 15000` |
| `IN (...)` | 목록 중 하나 | `product_type IN ('전세','구입')` |
| `IS NULL` | 값이 NULL | `region_id IS NULL` |
| `IS NOT NULL` | NULL이 아님 | `pension_payment IS NOT NULL` |
        """)
    with tab2:
        st.markdown("""
| 연산자 | 의미 | 예시 |
|--------|------|------|
| `AND` | 두 조건 모두 참 | `base_year = 2023 AND supply_count > 5000` |
| `OR` | 둘 중 하나 참 | `product_type = '전세' OR product_type = '구입'` |
| `NOT` | 조건 부정 | `NOT product_type = '중도금'` |
| `LIKE` | 패턴 매칭 | `guarantee_no LIKE 'G-2023%'` |

**우선순위**: `NOT` > `AND` > `OR` — 괄호로 명시적으로 묶는 것을 권장합니다.
        """)
    with tab3:
        st.markdown("""
| 함수 | 설명 | NULL 처리 |
|------|------|-----------|
| `COUNT(*)` | 전체 행 수 | NULL 포함 |
| `COUNT(col)` | 특정 컬럼 행 수 | NULL 제외 |
| `SUM(col)` | 합계 | NULL 무시 |
| `AVG(col)` | 평균 | NULL 무시 |
| `MAX(col)` | 최댓값 | NULL 무시 |
| `MIN(col)` | 최솟값 | NULL 무시 |
| `ROUND(값, n)` | 소수점 n자리 반올림 | — |
        """)


# ══════════════════════════════════════════════════════════════
# 2. 실습 환경
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[2]:
    st.markdown('<div class="section-header">🛠️ 실습 환경 구축</div>', unsafe_allow_html=True)

    st.markdown("## Python + SQLite 실습 환경")
    st.markdown("Python 내장 모듈 `sqlite3`와 `pandas`를 사용합니다. 별도 DB 서버 없이 로컬에서 즉시 실행 가능합니다.")
    st.code("""import sqlite3
import pandas as pd

conn = sqlite3.connect(":memory:")   # 인메모리 DB (임시)
# conn = sqlite3.connect("housing.db") # 파일 DB (영구 저장)

def run(sql):
    \"\"\"SQL 실행 후 DataFrame 반환\"\"\"
    return pd.read_sql_query(sql, conn)""", language="python")

    st.divider()
    st.markdown("## 📐 테이블 관계 구조 (ERD)")
    st.code("""
  regions (지역 마스터)
  ┌────────────┬─────────────┬─────────────┐
  │ region_id  │ region_name │ region_type │
  │ PK INTEGER │ TEXT        │ TEXT        │
  └─────┬──────┴─────────────┴─────────────┘
        │ 1                          1
        │ N                          N
        ▼                            ▼
  loan_guarantee (주택보증)      housing_pension (주택연금)
  ┌──────────────────────┐      ┌──────────────────────┐
  │ guarantee_id   PK    │      │ pension_id   PK      │
  │ guarantee_no (보증번호)│      │ base_year  (기준연도) │
  │ base_year  (기준연도) │      │ region_id  FK        │
  │ region_id  FK ───────┘      │ join_count (가입건수)  │
  │ product_type (상품유형)│      │ pension_payment(지급액)│
  │ supply_count (공급건수)│      │ avg_house_price(평균가)│
  │ guarantee_amount(금액)│      └──────────────────────┘
  └──────────────────────┘
    """, language="text")

    st.divider()
    st.markdown("## 📋 실습 데이터 미리보기")
    tab1, tab2, tab3 = st.tabs(["regions", "loan_guarantee", "housing_pension"])
    with tab1:
        df, _ = run_sql(conn, "SELECT * FROM regions")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("8개 지역 | region_type: 수도권(서울·경기·인천) / 지방(부산·대구·광주·대전·강원)")
    with tab2:
        df, _ = run_sql(conn, "SELECT * FROM loan_guarantee ORDER BY base_year, region_id")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("32건 | 기준연도: 2020~2023 | 상품유형: 전세/구입/중도금/전세대출 | 금액 단위: 억원")
    with tab3:
        df, _ = run_sql(conn, "SELECT * FROM housing_pension ORDER BY base_year, region_id")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("24건 | 기준연도: 2020~2023 | 지급액·평균주택가격 단위: 억원")

    st.markdown("""<div class="good-box">✅ 환경 구축 완료! 이제 <b>① SELECT</b>부터 순서대로 실습을 시작하세요.</div>""",
    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 3. SELECT
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[3]:
    st.markdown('<div class="section-header">① SELECT — 데이터 조회</div>', unsafe_allow_html=True)

    st.markdown("""
`SELECT` 는 SQL의 핵심 명령으로, **테이블에서 원하는 데이터를 읽어오는** 구문입니다.
조회 결과는 항상 새로운 가상 테이블(Result Set) 형태로 반환됩니다.
모든 SQL 쿼리는 SELECT로 시작한다고 해도 과언이 아닙니다.
    """)
    st.markdown("""<div class="syntax-box">
SELECT  [DISTINCT]  컬럼1, 컬럼2, ...  &nbsp;← 조회할 컬럼 (* 는 전체 컬럼)<br>
FROM    테이블명;                       &nbsp;← 어떤 테이블에서 가져올지
</div>""", unsafe_allow_html=True)

    st.divider()
    exs = [
        ("예제 1 — 전체 컬럼 조회 (SELECT *)",
         "`*`는 모든 컬럼을 의미합니다. 테이블 구조를 처음 파악할 때 편리합니다.",
         "SELECT *\nFROM   loan_guarantee;",
         "warn", "⚠️ 실무에서는 <code>SELECT *</code> 대신 필요한 컬럼만 명시하세요. 불필요한 컬럼 전송이 줄어 성능이 향상됩니다."),
        ("예제 2 — 특정 컬럼만 조회",
         "보증번호·기준연도·상품유형·공급건수만 가져옵니다. 가독성과 성능이 모두 향상됩니다.",
         "SELECT guarantee_no, base_year, product_type, supply_count\nFROM   loan_guarantee;",
         None, None),
        ("예제 3 — 별칭(AS) + 산술 연산",
         "`AS`로 한글 별칭을 붙이고, 보증금액을 조 단위로 환산합니다. 별칭은 SELECT 결과 컬럼명에만 영향을 주며, WHERE 절에서는 사용할 수 없습니다.",
         "SELECT\n    guarantee_no            AS 보증번호,\n    base_year               AS 기준연도,\n    supply_count            AS 공급건수,\n    guarantee_amount        AS \"보증금액(억)\",\n    ROUND(guarantee_amount / 10000.0, 4) AS \"보증금액(조)\"\nFROM loan_guarantee;",
         "tip", "💡 별칭(AS)은 SELECT에서 정의되므로 같은 SELECT의 WHERE·HAVING에서는 쓸 수 없습니다. ORDER BY에서는 사용 가능합니다."),
        ("예제 4 — DISTINCT 중복 제거",
         "어떤 상품유형이 있는지 고유한 값만 조회합니다. DISTINCT는 SELECT 바로 뒤 한 번만 씁니다.",
         "SELECT DISTINCT product_type AS 상품유형\nFROM   loan_guarantee;",
         None, None),
        ("예제 5 — LIMIT으로 상위 N행만",
         "처음 5행만 빠르게 확인합니다. 대용량 테이블 탐색 시 필수 습관입니다.",
         "SELECT guarantee_no, base_year, supply_count\nFROM   loan_guarantee\nLIMIT  5;",
         "tip", "💡 Oracle은 <code>WHERE ROWNUM &lt;= 5</code>, SQL Server는 <code>SELECT TOP 5</code>를 사용합니다."),
    ]
    for title, desc, sql, box_type, box_msg in exs:
        with st.expander(title, expanded=True):
            st.caption(desc)
            if box_type == "warn":
                st.markdown(f'<div class="warn-box">{box_msg}</div>', unsafe_allow_html=True)
            elif box_type == "tip":
                st.markdown(f'<div class="tip-box">{box_msg}</div>', unsafe_allow_html=True)
            st.code(sql, language="sql")
            show_result(conn, sql, f"sel_{title}")

    st.divider()
    practice_block(conn,
        "loan_guarantee 에서 보증번호·기준연도·상품유형·보증금액(억)과 함께 보증금액을 10,000으로 나눈 조 단위 금액(소수점 3자리)을 조회하세요.",
        """SELECT
    guarantee_no                         AS 보증번호,
    base_year                            AS 기준연도,
    product_type                         AS 상품유형,
    guarantee_amount                     AS "보증금액(억)",
    ROUND(guarantee_amount / 10000.0, 3) AS "보증금액(조)"
FROM loan_guarantee;""",
        "p_select",
        hint="ROUND(값, 자릿수) 함수와 AS 별칭을 활용하세요.")


# ══════════════════════════════════════════════════════════════
# 4. WHERE
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[4]:
    st.markdown('<div class="section-header">② WHERE — 조건 필터</div>', unsafe_allow_html=True)

    st.markdown("""
`WHERE` 절은 FROM으로 불러온 전체 데이터 중 **조건을 만족하는 행(Row)만** 남기는 필터입니다.

SQL 실행 순서상 **GROUP BY 이전**에 동작하므로, 개별 행에 대한 조건만 쓸 수 있습니다.
집계함수(`SUM`, `AVG` 등)는 WHERE에서 사용 불가 — 집계 조건은 반드시 `HAVING`을 사용합니다.
    """)
    st.markdown("""<div class="syntax-box">
SELECT 컬럼 FROM 테이블<br>
WHERE  조건식;  &nbsp;← TRUE인 행만 결과에 포함
</div>""", unsafe_allow_html=True)

    st.divider()
    exs = [
        ("예제 1 — 단순 조건 (특정 연도)",
         "2023년 기준 보증 데이터만 조회합니다.",
         "SELECT guarantee_no, base_year, product_type, supply_count\nFROM   loan_guarantee\nWHERE  base_year = 2023;", None, None),
        ("예제 2 — 비교 연산자 (공급건수 1만 건 이상)",
         "공급건수가 10,000건 이상인 대규모 보증 건만 조회합니다.",
         "SELECT guarantee_no, base_year, supply_count, guarantee_amount\nFROM   loan_guarantee\nWHERE  supply_count >= 10000;", None, None),
        ("예제 3 — AND로 두 조건 동시 적용",
         "2023년이면서 공급건수 5,000건 이상인 건. AND는 두 조건 모두 참일 때만 포함합니다.",
         "SELECT guarantee_no, base_year, product_type, supply_count\nFROM   loan_guarantee\nWHERE  base_year = 2023\n  AND  supply_count >= 5000;", None, None),
        ("예제 4 — IN으로 목록 조건 간결하게",
         "전세 또는 구입 상품을 조회합니다. OR을 여러 번 쓰는 대신 IN을 쓰면 간결합니다.",
         "SELECT guarantee_no, product_type, supply_count\nFROM   loan_guarantee\nWHERE  product_type IN ('전세', '구입');",
         "tip", "💡 IN 목록이 길어지면 서브쿼리와 결합 가능: <code>WHERE region_id IN (SELECT region_id FROM regions WHERE region_type = '수도권')</code>"),
        ("예제 5 — BETWEEN 범위 조건",
         "2021~2022년 사이 데이터. BETWEEN a AND b 는 양 끝값(a, b) 포함입니다.",
         "SELECT guarantee_no, base_year, supply_count\nFROM   loan_guarantee\nWHERE  base_year BETWEEN 2021 AND 2022;",
         "tip", "💡 BETWEEN은 숫자뿐 아니라 날짜·문자열에도 사용 가능합니다."),
        ("예제 6 — IS NULL / IS NOT NULL",
         "NULL은 '값이 없는 상태'로 0이나 빈 문자열('')과 완전히 다릅니다.",
         "-- NULL인 행\nSELECT guarantee_no, region_id\nFROM   loan_guarantee\nWHERE  region_id IS NULL;\n\n-- NULL이 아닌 행\nSELECT guarantee_no, region_id\nFROM   loan_guarantee\nWHERE  region_id IS NOT NULL;",
         "warn", "⚠️ <code>= NULL</code>은 항상 FALSE를 반환합니다. NULL 비교는 반드시 <code>IS NULL</code>을 사용하세요."),
    ]
    for title, desc, sql, box_type, box_msg in exs:
        with st.expander(title, expanded=True):
            st.caption(desc)
            if box_type == "warn":
                st.markdown(f'<div class="warn-box">{box_msg}</div>', unsafe_allow_html=True)
            elif box_type == "tip":
                st.markdown(f'<div class="tip-box">{box_msg}</div>', unsafe_allow_html=True)
            st.code(sql, language="sql")
            show_result(conn, sql, f"wh_{title}")

    st.divider()
    practice_block(conn,
        "2022~2023년 중 상품유형이 '전세' 또는 '전세대출'이고 공급건수가 10,000건 이상인 건을 공급건수 내림차순으로 조회하세요.",
        """SELECT guarantee_no, base_year, product_type, supply_count
FROM   loan_guarantee
WHERE  base_year BETWEEN 2022 AND 2023
  AND  product_type IN ('전세', '전세대출')
  AND  supply_count >= 10000
ORDER BY supply_count DESC;""",
        "p_where",
        hint="BETWEEN, IN, >= 를 AND로 조합하고 ORDER BY를 추가하세요.")


# ══════════════════════════════════════════════════════════════
# 5. LIKE
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[5]:
    st.markdown('<div class="section-header">③ LIKE — 패턴 검색</div>', unsafe_allow_html=True)

    st.markdown("""
`LIKE` 는 문자열 컬럼에서 **특정 패턴**에 맞는 값을 검색합니다.
정확한 값을 모르거나, 값의 일부만 알 때 사용합니다.
두 가지 와일드카드 문자를 조합해 패턴을 정의합니다.
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="syntax-box">
WHERE 컬럼 LIKE '패턴'<br><br>
%  : 0개 이상의 임의 문자<br>
_  : 정확히 1개의 임의 문자
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
| 패턴 | 의미 | 보증번호 매칭 예 |
|------|------|------|
| `'G-2023%'` | G-2023으로 시작 | G-2023-0001 ✅ |
| `'%-0005'` | -0005로 끝남 | G-2021-0005 ✅ |
| `'%2022%'` | 2022 포함 | G-2022-0003 ✅ |
| `'G-____-%'` | G- + 4자리 + - | 모든 보증번호 ✅ |
        """)

    st.divider()
    exs = [
        ("예제 1 — 특정 연도 보증번호 검색 (앞부분 고정)",
         "보증번호가 'G-2023'으로 시작하는 건만 조회합니다. 앞이 고정된 패턴은 인덱스를 활용해 빠릅니다.",
         "SELECT guarantee_no, base_year, product_type, supply_count\nFROM   loan_guarantee\nWHERE  guarantee_no LIKE 'G-2023%';",
         "tip", "💡 인덱스 활용 가능: <code>LIKE '값%'</code> / 인덱스 미사용(Full Scan): <code>LIKE '%값%'</code>"),
        ("예제 2 — 특정 번호로 끝나는 검색",
         "일련번호가 0005로 끝나는 건을 모든 연도에서 찾습니다.",
         "SELECT guarantee_no, base_year, supply_count\nFROM   loan_guarantee\nWHERE  guarantee_no LIKE '%-0005';", None, None),
        ("예제 3 — 포함 검색 ('전세' 포함 상품유형)",
         "'전세' 문자가 포함된 상품(전세, 전세대출)을 모두 찾습니다.",
         "SELECT DISTINCT product_type\nFROM   loan_guarantee\nWHERE  product_type LIKE '%전세%';",
         "warn", "⚠️ <code>LIKE '%값%'</code> (앞에 %)는 Full Table Scan이 발생합니다. 대용량 테이블에서는 Full-Text Index 도입을 검토하세요."),
        ("예제 4 — _ 와일드카드 (글자 수 고정)",
         "'G-YYYY-NNNN' 형식인 보증번호를 검증합니다. _는 정확히 1글자입니다.",
         "SELECT guarantee_no\nFROM   loan_guarantee\nWHERE  guarantee_no LIKE 'G-____-____';", None, None),
    ]
    for title, desc, sql, box_type, box_msg in exs:
        with st.expander(title, expanded=True):
            st.caption(desc)
            if box_type == "warn":
                st.markdown(f'<div class="warn-box">{box_msg}</div>', unsafe_allow_html=True)
            elif box_type == "tip":
                st.markdown(f'<div class="tip-box">{box_msg}</div>', unsafe_allow_html=True)
            st.code(sql, language="sql")
            show_result(conn, sql, f"lk_{title}")

    st.divider()
    practice_block(conn,
        "'G-2021' 또는 'G-2022'로 시작하는 보증번호 중 공급건수가 5,000건 이상인 건을 공급건수 내림차순으로 조회하세요.",
        """SELECT guarantee_no, base_year, product_type, supply_count
FROM   loan_guarantee
WHERE  (guarantee_no LIKE 'G-2021%' OR guarantee_no LIKE 'G-2022%')
  AND  supply_count >= 5000
ORDER BY supply_count DESC;""",
        "p_like",
        hint="LIKE 조건 두 개를 OR로 묶고 괄호로 감싼 뒤 AND로 공급건수 조건을 추가하세요.")


# ══════════════════════════════════════════════════════════════
# 6. ORDER BY
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[6]:
    st.markdown('<div class="section-header">④ ORDER BY — 정렬</div>', unsafe_allow_html=True)

    st.markdown("""
`ORDER BY` 는 결과를 원하는 기준으로 **정렬**합니다.
SQL 실행 순서상 **가장 마지막**에 적용되므로, SELECT에서 정의한 별칭(AS)을 ORDER BY에서 사용할 수 있습니다.
정렬 기준을 여러 개 지정하면, 앞 기준이 같은 행들을 뒤 기준으로 추가 정렬합니다.
    """)
    st.markdown("""<div class="syntax-box">
SELECT 컬럼 FROM 테이블<br>
ORDER BY 컬럼1 [ASC|DESC], 컬럼2 [ASC|DESC];<br><br>
ASC  : 오름차순 — 숫자(작→큰), 문자(가→힣), 날짜(과거→최신). 기본값, 생략 가능<br>
DESC : 내림차순 — 숫자(큰→작), 문자(힣→가), 날짜(최신→과거)
</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="tip-box">💡 <b>NULL 정렬 동작</b>: SQLite는 NULL을 오름차순에서 가장 앞에, 내림차순에서 가장 뒤에 배치합니다.
NULL을 맨 마지막으로 보내려면 <code>ORDER BY 컬럼 IS NULL ASC, 컬럼 ASC</code> 패턴을 사용하세요.</div>""",
    unsafe_allow_html=True)

    st.divider()
    exs = [
        ("예제 1 — 공급건수 내림차순", "가장 많이 공급된 보증 건부터 정렬합니다.",
         "SELECT guarantee_no, base_year, product_type, supply_count\nFROM   loan_guarantee\nORDER BY supply_count DESC;"),
        ("예제 2 — 다중 정렬 (기준연도↑ + 보증금액↓)",
         "기준연도 오름차순으로 먼저 정렬하고, 같은 연도 내에서는 보증금액이 큰 순으로 정렬합니다.",
         "SELECT base_year, product_type, supply_count, guarantee_amount\nFROM   loan_guarantee\nORDER BY base_year ASC, guarantee_amount DESC;"),
        ("예제 3 — SELECT 별칭으로 정렬",
         "SELECT에서 정의한 별칭(총공급건수)을 ORDER BY에서 바로 사용할 수 있습니다.",
         "SELECT base_year AS 연도, SUM(supply_count) AS 총공급건수\nFROM   loan_guarantee\nGROUP BY base_year\nORDER BY 총공급건수 DESC;"),
        ("예제 4 — WHERE + ORDER BY 조합",
         "2023년 보증 데이터를 공급건수 높은 순으로 정렬합니다.",
         "SELECT guarantee_no, product_type, supply_count, guarantee_amount\nFROM   loan_guarantee\nWHERE  base_year = 2023\nORDER BY supply_count DESC;"),
    ]
    for title, desc, sql in exs:
        with st.expander(title, expanded=True):
            st.caption(desc)
            st.code(sql, language="sql")
            show_result(conn, sql, f"ord_{title}")

    st.divider()
    practice_block(conn,
        "housing_pension 에서 2022년 이후 데이터를 연금지급액 내림차순, 같은 지급액이면 가입건수 내림차순으로 정렬하세요.",
        """SELECT base_year, region_id, join_count, pension_payment
FROM   housing_pension
WHERE  base_year >= 2022
ORDER BY pension_payment DESC, join_count DESC;""",
        "p_order",
        hint="ORDER BY에 컬럼 두 개를 콤마로 구분해 작성하세요.")


# ══════════════════════════════════════════════════════════════
# 7. GROUP BY
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[7]:
    st.markdown('<div class="section-header">⑤ GROUP BY — 집계</div>', unsafe_allow_html=True)

    st.markdown("""
`GROUP BY` 는 특정 컬럼의 값이 같은 행들을 **하나의 그룹으로 묶고**, 각 그룹에 집계함수를 적용합니다.
예) 기준연도별 공급건수 합계, 상품유형별 평균 보증금액.

`HAVING` 은 GROUP BY로 만들어진 **그룹에 대해 조건을 필터링**합니다.
WHERE가 개별 행을 필터링하는 것과 달리, HAVING은 집계된 그룹을 필터링합니다.
    """)
    st.markdown("""<div class="syntax-box">
SELECT   그룹컬럼, 집계함수(컬럼)<br>
FROM     테이블<br>
[WHERE   집계 전 행 필터]    ← 먼저 적용됨<br>
GROUP BY 그룹컬럼<br>
[HAVING  집계 후 그룹 필터]  ← 나중에 적용됨<br>
[ORDER BY ...];
</div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**WHERE vs HAVING**")
        st.markdown("""
| 구분 | WHERE | HAVING |
|------|-------|--------|
| 적용 시점 | GROUP BY **이전** | GROUP BY **이후** |
| 필터 대상 | 개별 **행** | 집계된 **그룹** |
| 집계함수 | ❌ 사용 불가 | ✅ 사용 가능 |
        """)
    with col2:
        st.markdown("""<div class="warn-box">
⚠️ <b>GROUP BY 핵심 규칙</b><br><br>
SELECT에 있는 컬럼 중 집계함수로 감싸지 않은 컬럼은<br>
반드시 GROUP BY에도 포함해야 합니다.<br><br>
✅ 올바른 예:<br>
<code>SELECT base_year, product_type, COUNT(*)</code><br>
<code>GROUP BY base_year, product_type</code><br><br>
❌ 오류:<br>
<code>SELECT base_year, product_type, COUNT(*)</code><br>
<code>GROUP BY base_year</code>  ← product_type 누락!
</div>""", unsafe_allow_html=True)

    st.divider()
    exs = [
        ("예제 1 — 기준연도별 총 공급건수",
         "연도별로 전체 보증 공급건수와 보증금액 합계를 구합니다.",
         """SELECT
    base_year                       AS 기준연도,
    COUNT(*)                        AS 보증건수,
    SUM(supply_count)               AS 총공급건수,
    ROUND(SUM(guarantee_amount), 1) AS "총보증금액(억)"
FROM   loan_guarantee
GROUP BY base_year
ORDER BY base_year;"""),
        ("예제 2 — 상품유형별 통계",
         "상품별 평균·최대·최소 공급건수를 비교합니다.",
         """SELECT
    product_type                  AS 상품유형,
    COUNT(*)                      AS 데이터건수,
    ROUND(AVG(supply_count), 0)   AS 평균공급건수,
    MAX(supply_count)             AS 최대공급건수,
    MIN(supply_count)             AS 최소공급건수
FROM   loan_guarantee
GROUP BY product_type
ORDER BY 평균공급건수 DESC;"""),
        ("예제 3 — HAVING으로 집계 결과 필터",
         "평균 공급건수가 5,000건 이상인 상품유형만 조회합니다.",
         """SELECT
    product_type,
    ROUND(AVG(supply_count), 0) AS 평균공급건수
FROM   loan_guarantee
GROUP BY product_type
HAVING AVG(supply_count) >= 5000
ORDER BY 평균공급건수 DESC;"""),
        ("예제 4 — WHERE + GROUP BY + HAVING 조합",
         "2022년 이후 데이터 중, 지역별 연금지급액 합계가 2,000억 이상인 지역.",
         """SELECT
    region_id,
    SUM(join_count)               AS 총가입건수,
    ROUND(SUM(pension_payment),1) AS "총연금지급액(억)"
FROM   housing_pension
WHERE  base_year >= 2022
GROUP BY region_id
HAVING SUM(pension_payment) >= 2000
ORDER BY "총연금지급액(억)" DESC;"""),
    ]
    for title, desc, sql in exs:
        with st.expander(title, expanded=True):
            st.caption(desc)
            st.code(sql, language="sql")
            show_result(conn, sql, f"grp_{title}")

    st.divider()
    practice_block(conn,
        "2021~2023년 데이터에서 기준연도·상품유형별로 공급건수 합계를 구하고, 합계가 15,000건 이상인 경우만 내림차순으로 조회하세요.",
        """SELECT
    base_year         AS 기준연도,
    product_type      AS 상품유형,
    SUM(supply_count) AS 총공급건수
FROM   loan_guarantee
WHERE  base_year BETWEEN 2021 AND 2023
GROUP BY base_year, product_type
HAVING SUM(supply_count) >= 15000
ORDER BY 총공급건수 DESC;""",
        "p_group",
        hint="GROUP BY에 두 컬럼을 함께 쓰고 HAVING으로 합계를 필터하세요.")


# ══════════════════════════════════════════════════════════════
# 8. JOIN — 대폭 강화
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[8]:
    st.markdown('<div class="section-header">⑥ JOIN — 테이블 결합</div>', unsafe_allow_html=True)

    st.markdown("""
`JOIN` 은 **두 개 이상의 테이블을 공통 컬럼(키)을 기준으로 결합**해 하나의 결과로 만드는 연산입니다.

관계형 DB는 데이터를 목적별로 분리된 테이블에 저장합니다(정규화).
예를 들어 `loan_guarantee`에는 `region_id`(숫자)만 있고 지역명은 없습니다.
지역명을 함께 보려면 `regions` 테이블을 JOIN해야 합니다.

JOIN 없이 쿼리하면 숫자 코드만 보이고, JOIN을 통해 의미 있는 이름으로 바꿀 수 있습니다.
    """)
    st.markdown("""<div class="syntax-box">
SELECT  a.컬럼, b.컬럼<br>
FROM    테이블A  AS a<br>
[JOIN종류]  테이블B  AS b  ON  a.공통컬럼 = b.공통컬럼;<br><br>
⚠️ ON 조건을 빠뜨리면 카테시안 곱(모든 행의 조합)이 발생합니다!
</div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("## JOIN 종류별 동작 원리")

    tab_inner, tab_left, tab_right, tab_full = st.tabs(
        ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"])

    with tab_inner:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("#### 개념")
            st.markdown("두 테이블에서 **ON 조건이 일치하는 행만** 반환합니다. 한쪽에만 있는 데이터는 제외됩니다.")
            st.code("""
  loan_guarantee       regions
  ┌───────────────┐    ┌──────────────┐
  │ region_id = 1 │───▶│ region_id = 1│  ✅ 포함
  │ region_id = 2 │───▶│ region_id = 2│  ✅ 포함
  │ region_id = 9 │ ✗  │  (없음)      │  ❌ 제외
  └───────────────┘    └──────────────┘
  결과: region_id 1, 2만 포함
            """, language="text")
            st.markdown("**언제 사용**: 두 테이블 모두에 존재하는 데이터만 필요할 때")
        with col2:
            st.markdown("#### 예제")
            sql = """SELECT
    lg.guarantee_no  AS 보증번호,
    lg.base_year     AS 기준연도,
    r.region_name    AS 지역명,
    lg.product_type  AS 상품유형,
    lg.supply_count  AS 공급건수
FROM loan_guarantee lg
INNER JOIN regions r
    ON lg.region_id = r.region_id
ORDER BY lg.base_year, r.region_name;"""
            st.code(sql, language="sql")
            show_result(conn, sql, "join_inner")

    with tab_left:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("#### 개념")
            st.markdown("**왼쪽 테이블 전체** + 오른쪽에서 매칭되는 행. 오른쪽에 없으면 NULL로 채워집니다.")
            st.code("""
  regions (왼쪽)      loan_guarantee (오른쪽)
  ┌────────────┐      ┌──────────────┐
  │ region_id=1│ ───▶ │ 데이터 있음  │  ✅ 포함
  │ region_id=8│ ───▶ │ 데이터 없음  │  ✅ 포함(NULL)
  └────────────┘      └──────────────┘
  결과: 왼쪽(regions) 전체 유지
  매칭 없으면 loan_guarantee 컬럼 = NULL
            """, language="text")
            st.markdown("""**언제 사용**: 왼쪽 데이터는 모두 유지하면서 오른쪽 정보를 보충할 때
예) 보증 데이터가 없는 지역도 포함해서 전체 지역 현황 파악""")
        with col2:
            st.markdown("#### 예제")
            sql = """SELECT
    r.region_name    AS 지역명,
    r.region_type    AS 구분,
    lg.base_year     AS 기준연도,
    lg.supply_count  AS 공급건수
FROM regions r
LEFT JOIN loan_guarantee lg
    ON r.region_id = lg.region_id
ORDER BY r.region_name, lg.base_year;"""
            st.code(sql, language="sql")
            show_result(conn, sql, "join_left")

    with tab_right:
        st.markdown("#### 개념")
        st.markdown("**오른쪽 테이블 전체** + 왼쪽에서 매칭되는 행. SQLite는 RIGHT JOIN을 지원하지 않아 테이블 순서를 바꿔 LEFT JOIN으로 대체합니다.")
        st.code("""
  A (왼쪽)     B (오른쪽)
  ┌─────────┐   ┌──────────┐
  │ id = 1  │◀──│ id = 1   │  ✅ 포함
  │ (없음)  │ ✗─│ id = 9   │  ✅ 포함(A쪽 NULL)
  └─────────┘   └──────────┘
  결과: 오른쪽(B) 전체 유지
  매칭 없으면 A 컬럼 = NULL
        """, language="text")
        st.code("""-- RIGHT JOIN (SQLite 미지원 → 테이블 순서를 바꿔 LEFT JOIN으로 대체)
-- 원래 의도: loan_guarantee RIGHT JOIN regions
SELECT
    r.region_name    AS 지역명,
    lg.base_year     AS 기준연도,
    lg.supply_count  AS 공급건수
FROM regions r                  -- 원래 오른쪽 테이블을 왼쪽으로
LEFT JOIN loan_guarantee lg     -- 원래 왼쪽 테이블을 오른쪽으로
    ON r.region_id = lg.region_id;""", language="sql")

    with tab_full:
        st.markdown("#### 개념")
        st.markdown("**양쪽 테이블 전체**를 포함합니다. 어느 쪽에도 매칭이 없으면 NULL. SQLite는 UNION으로 구현합니다.")
        st.code("""
  A (왼쪽)     B (오른쪽)
  ┌─────────┐   ┌──────────┐
  │ id = 1  │◀─▶│ id = 1   │  ✅ 양쪽 포함
  │ id = 2  │   │ (없음)   │  ✅ A만 (B쪽 NULL)
  │ (없음)  │   │ id = 9   │  ✅ B만 (A쪽 NULL)
  └─────────┘   └──────────┘
        """, language="text")
        st.code("""-- FULL OUTER JOIN (SQLite 미지원 → UNION으로 구현)
SELECT r.region_name, lg.guarantee_no, lg.supply_count
FROM regions r
LEFT JOIN loan_guarantee lg ON r.region_id = lg.region_id

UNION

SELECT r.region_name, lg.guarantee_no, lg.supply_count
FROM loan_guarantee lg
LEFT JOIN regions r ON r.region_id = lg.region_id;""", language="sql")

    st.divider()
    st.markdown("## JOIN 종류 한눈에 비교")
    st.markdown("""
| JOIN 종류 | 왼쪽 테이블 | 오른쪽 테이블 | 매칭 없는 행 |
|-----------|------------|--------------|-------------|
| `INNER JOIN` | 매칭된 행만 | 매칭된 행만 | 제외 |
| `LEFT JOIN` | **전체** | 매칭된 행만 | 오른쪽 = NULL |
| `RIGHT JOIN` | 매칭된 행만 | **전체** | 왼쪽 = NULL |
| `FULL OUTER JOIN` | **전체** | **전체** | 상대방 = NULL |
    """)

    st.divider()
    st.markdown("## ON 조건 & 테이블 별칭")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="tip-box">
<b>ON 조건</b>: 두 테이블을 연결하는 조건식. 보통 한 테이블의 PK와 다른 테이블의 FK를 연결합니다.<br><br>
<code>FROM loan_guarantee lg</code><br>
<code>JOIN regions r  ON lg.region_id = r.region_id</code><br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↑ FK&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↑ PK<br><br>
복합 조건도 가능합니다:<br>
<code>ON lg.region_id = hp.region_id</code><br>
<code>AND lg.base_year = hp.base_year</code>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="tip-box">
<b>테이블 별칭(Alias)</b>: JOIN 시 테이블 이름이 길어지므로 별칭을 사용해 간결하게 작성하세요.<br><br>
<code>FROM loan_guarantee AS lg</code><br>
또는<br>
<code>FROM loan_guarantee lg</code>  (AS 생략 가능)<br><br>
이후 <code>lg.컬럼명</code>으로 어느 테이블의 컬럼인지 명확히 표시합니다.<br>
두 테이블에 같은 이름의 컬럼이 있을 때 반드시 필요합니다.
</div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("## 3개 테이블 JOIN")
    sql_3tbl = """-- 주택보증 + 주택연금 + 지역명 동시 조회
SELECT
    r.region_name        AS 지역명,
    lg.base_year         AS 기준연도,
    SUM(lg.supply_count) AS 보증공급건수,
    hp.join_count        AS 연금가입건수,
    hp.pension_payment   AS "연금지급액(억)"
FROM loan_guarantee  lg
JOIN regions         r   ON lg.region_id = r.region_id
JOIN housing_pension hp  ON lg.region_id = hp.region_id
                         AND lg.base_year = hp.base_year
GROUP BY r.region_name, lg.base_year,
         hp.join_count, hp.pension_payment
ORDER BY lg.base_year, 보증공급건수 DESC;"""
    with st.expander("예제 — 3개 테이블 JOIN", expanded=True):
        st.code(sql_3tbl, language="sql")
        show_result(conn, sql_3tbl, "join_3tbl")

    st.divider()
    st.markdown("## ⚠️ 자주 하는 JOIN 실수")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="warn-box">
<b>실수 1 — ON 조건 누락 (카테시안 곱)</b><br><br>
<code>FROM loan_guarantee, regions</code><br>
← ON 없이 쉼표로 연결하면 모든 행의 조합<br>
&nbsp;&nbsp;(32행 × 8행 = 256행)이 생성됩니다!<br><br>
<b>올바른 방법:</b><br>
<code>FROM loan_guarantee lg</code><br>
<code>JOIN regions r ON lg.region_id = r.region_id</code>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="warn-box">
<b>실수 2 — 컬럼명 중복 (ambiguous column)</b><br><br>
두 테이블 모두 <code>region_id</code>를 가질 때<br>
<code>SELECT region_id</code>로 쓰면 오류 발생.<br><br>
<b>올바른 방법:</b><br>
<code>SELECT lg.region_id</code> 또는 <code>r.region_id</code><br>
처럼 테이블 별칭을 명시하세요.
</div>""", unsafe_allow_html=True)

    st.divider()
    practice_block(conn,
        "regions와 loan_guarantee를 JOIN하여 '수도권' 지역의 2022~2023년 전세 관련 상품(LIKE 활용)을 지역명·기준연도·상품유형·공급건수로 조회하고 공급건수 내림차순으로 정렬하세요.",
        """SELECT
    r.region_name    AS 지역명,
    lg.base_year     AS 기준연도,
    lg.product_type  AS 상품유형,
    lg.supply_count  AS 공급건수
FROM loan_guarantee lg
JOIN regions r ON lg.region_id = r.region_id
WHERE  r.region_type = '수도권'
  AND  lg.base_year BETWEEN 2022 AND 2023
  AND  lg.product_type LIKE '%전세%'
ORDER BY lg.supply_count DESC;""",
        "p_join",
        hint="JOIN 후 WHERE에서 region_type, base_year BETWEEN, product_type LIKE 세 조건을 AND로 연결하세요.")


# ══════════════════════════════════════════════════════════════
# 9. 복합 쿼리 실전
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[9]:
    st.markdown('<div class="section-header">🚀 복합 쿼리 실전</div>', unsafe_allow_html=True)
    st.markdown("""
지금까지 배운 모든 키워드를 조합하는 실전 문제입니다.
**먼저 직접 SQL을 작성해 실행해보고**, 📋 정답 보기로 비교해보세요.
    """)
    st.markdown("""<div class="tip-box">💡 <b>풀이 순서 추천</b><br>
① 어떤 테이블이 필요한지 파악 → ② JOIN 구조 결정 → ③ WHERE 조건 작성
→ ④ GROUP BY / HAVING → ⑤ SELECT 컬럼 & 별칭 정리 → ⑥ ORDER BY</div>""",
    unsafe_allow_html=True)
    st.divider()

    practice_block(conn,
        "📌 실전 1 — 연도·지역별 보증 현황 리포트\n\n"
        "기준연도·지역명·지역구분·상품유형별로 공급건수 합계와 보증금액 합계(소수점1자리)를 구하고,\n"
        "기준연도 내림차순 → 공급건수 합계 내림차순으로 정렬하세요.",
        """SELECT
    lg.base_year                        AS 기준연도,
    r.region_name                       AS 지역명,
    r.region_type                       AS 지역구분,
    lg.product_type                     AS 상품유형,
    SUM(lg.supply_count)                AS 총공급건수,
    ROUND(SUM(lg.guarantee_amount), 1)  AS "총보증금액(억)"
FROM loan_guarantee lg
JOIN regions r ON lg.region_id = r.region_id
GROUP BY lg.base_year, r.region_name, r.region_type, lg.product_type
ORDER BY lg.base_year DESC, 총공급건수 DESC;""",
        "adv1",
        hint="regions JOIN 후 4개 컬럼으로 GROUP BY, SUM·ROUND로 집계하세요.")

    st.divider()
    practice_block(conn,
        "📌 실전 2 — 평균 연금지급액 초과 지역 (서브쿼리)\n\n"
        "housing_pension에서 전체 평균 연금지급액보다 높은 연도·지역명 데이터를\n"
        "연금지급액 내림차순으로 조회하세요.",
        """SELECT
    hp.base_year             AS 기준연도,
    r.region_name            AS 지역명,
    hp.pension_payment       AS "연금지급액(억)"
FROM housing_pension hp
JOIN regions r ON hp.region_id = r.region_id
WHERE hp.pension_payment > (
    SELECT AVG(pension_payment) FROM housing_pension
)
ORDER BY hp.pension_payment DESC;""",
        "adv2",
        hint="WHERE 조건에 서브쿼리 (SELECT AVG(...) FROM housing_pension)를 사용하세요.")

    st.divider()
    practice_block(conn,
        "📌 실전 3 — 수도권 vs 지방 연도별 보증 비교 (CASE WHEN)\n\n"
        "기준연도별로 수도권 공급건수 합계, 지방 공급건수 합계, 전국 합계를 나란히 조회하세요.\n"
        "CASE WHEN region_type = '수도권' THEN supply_count ELSE 0 END 패턴을 활용하세요.",
        """SELECT
    lg.base_year AS 기준연도,
    SUM(CASE WHEN r.region_type = '수도권' THEN lg.supply_count ELSE 0 END) AS 수도권공급건수,
    SUM(CASE WHEN r.region_type = '지방'   THEN lg.supply_count ELSE 0 END) AS 지방공급건수,
    SUM(lg.supply_count)                                                     AS 전국공급건수
FROM loan_guarantee lg
JOIN regions r ON lg.region_id = r.region_id
GROUP BY lg.base_year
ORDER BY lg.base_year;""",
        "adv3",
        hint="SUM(CASE WHEN 조건 THEN 값 ELSE 0 END) 패턴으로 조건부 합계를 구하세요.")

    st.divider()
    practice_block(conn,
        "📌 실전 4 — 전세 비중이 높은 연도 찾기\n\n"
        "기준연도별로 전체 공급건수 대비 전세(product_type='전세') 공급건수 비율(%)을 계산하고,\n"
        "비율이 40% 이상인 연도만 비율 내림차순으로 조회하세요.",
        """SELECT
    base_year  AS 기준연도,
    SUM(CASE WHEN product_type = '전세' THEN supply_count ELSE 0 END) AS 전세공급건수,
    SUM(supply_count) AS 전체공급건수,
    ROUND(
        100.0 * SUM(CASE WHEN product_type = '전세' THEN supply_count ELSE 0 END)
              / SUM(supply_count), 1
    ) AS "전세비율(%)"
FROM loan_guarantee
GROUP BY base_year
HAVING ROUND(
    100.0 * SUM(CASE WHEN product_type = '전세' THEN supply_count ELSE 0 END)
          / SUM(supply_count), 1
) >= 40
ORDER BY "전세비율(%)" DESC;""",
        "adv4",
        hint="CASE WHEN으로 전세 건수를 조건부 합산하고, 전체 합으로 나눠 비율을 구한 뒤 HAVING으로 필터하세요.")


# ══════════════════════════════════════════════════════════════
# 10. 자유 실습 & 연습과제
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[10]:
    st.markdown('<div class="section-header">✏️ 자유 실습 & 연습과제</div>', unsafe_allow_html=True)

    tab_free, tab_quiz = st.tabs(["🔓 자유 실습", "📝 연습과제 (정답 포함)"])

    with tab_free:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📋 테이블 컬럼**")
            st.markdown("""
- `regions` : region_id, region_name, region_type
- `loan_guarantee` : guarantee_id, guarantee_no, base_year, region_id, product_type, supply_count, guarantee_amount
- `housing_pension` : pension_id, base_year, region_id, join_count, pension_payment, avg_house_price
            """)
        with col2:
            st.markdown("**⚡ 빠른 참조**")
            st.code("""SELECT col, COUNT(*), SUM(col), AVG(col)
FROM t WHERE 조건
GROUP BY col HAVING 집계조건
ORDER BY col DESC;

JOIN: FROM a JOIN b ON a.key = b.key
LIKE: WHERE col LIKE 'G-2023%'
NULL: WHERE col IS NULL""", language="sql")

        presets = [
            "직접 입력",
            "SELECT * FROM regions",
            "SELECT * FROM loan_guarantee LIMIT 10",
            "SELECT base_year, SUM(supply_count) AS 총공급건수 FROM loan_guarantee GROUP BY base_year ORDER BY base_year",
            "SELECT lg.guarantee_no, r.region_name, lg.product_type, lg.supply_count FROM loan_guarantee lg JOIN regions r ON lg.region_id = r.region_id WHERE lg.base_year = 2023",
            "SELECT base_year, region_id, pension_payment FROM housing_pension ORDER BY pension_payment DESC LIMIT 10",
        ]
        preset = st.selectbox("예제 불러오기", presets)
        default = "" if preset == "직접 입력" else preset
        user_sql = st.text_area("SQL 입력", value=default, height=160, placeholder="SELECT ...")
        if st.button("▶ 실행", type="primary"):
            if user_sql.strip():
                df, err = run_sql(conn, user_sql)
                if err:
                    st.error(f"오류: {err}")
                else:
                    st.success(f"✅ {len(df)}행 반환")
                    st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning("SQL을 입력해주세요.")

    with tab_quiz:
        st.markdown("아래 5개 문제를 직접 풀어보고 📋 정답 보기로 확인하세요.")
        st.divider()

        quizzes = [
            {
                "no": "1", "level": "🟢 기초",
                "q": "loan_guarantee 에서 2023년 보증 데이터를 보증금액 내림차순으로 조회하세요.\n(보증번호·상품유형·공급건수·보증금액 컬럼 포함)",
                "hint": "WHERE base_year = 2023 후 ORDER BY guarantee_amount DESC",
                "answer": """SELECT
    guarantee_no     AS 보증번호,
    product_type     AS 상품유형,
    supply_count     AS 공급건수,
    guarantee_amount AS "보증금액(억)"
FROM   loan_guarantee
WHERE  base_year = 2023
ORDER BY guarantee_amount DESC;""",
            },
            {
                "no": "2", "level": "🟢 기초",
                "q": "보증번호가 'G-2022'로 시작하는 건의 상품유형별 공급건수 합계를 구하고, 합계 내림차순으로 정렬하세요.",
                "hint": "WHERE guarantee_no LIKE 'G-2022%' 후 GROUP BY product_type",
                "answer": """SELECT
    product_type      AS 상품유형,
    SUM(supply_count) AS 총공급건수
FROM   loan_guarantee
WHERE  guarantee_no LIKE 'G-2022%'
GROUP BY product_type
ORDER BY 총공급건수 DESC;""",
            },
            {
                "no": "3", "level": "🟡 중급",
                "q": "기준연도별로 주택연금 총 가입건수와 총 연금지급액(소수점 1자리)을 조회하고, 연도 오름차순으로 정렬하세요.",
                "hint": "housing_pension에서 GROUP BY base_year, SUM·ROUND 활용",
                "answer": """SELECT
    base_year                       AS 기준연도,
    SUM(join_count)                 AS 총가입건수,
    ROUND(SUM(pension_payment), 1)  AS "총연금지급액(억)"
FROM   housing_pension
GROUP BY base_year
ORDER BY base_year ASC;""",
            },
            {
                "no": "4", "level": "🟡 중급",
                "q": "loan_guarantee 와 regions 를 JOIN하여 '수도권' 지역의 2023년 보증 현황을\n지역명·상품유형·공급건수로 조회하고, 공급건수 내림차순으로 정렬하세요.",
                "hint": "INNER JOIN 후 WHERE region_type = '수도권' AND base_year = 2023",
                "answer": """SELECT
    r.region_name    AS 지역명,
    lg.product_type  AS 상품유형,
    lg.supply_count  AS 공급건수
FROM loan_guarantee lg
JOIN regions r ON lg.region_id = r.region_id
WHERE  r.region_type = '수도권'
  AND  lg.base_year = 2023
ORDER BY lg.supply_count DESC;""",
            },
            {
                "no": "5", "level": "🔴 심화",
                "q": "housing_pension 에서 지역별 전체 기간 평균 연금지급액을 구하고,\n그 평균이 전체 데이터 평균보다 높은 지역(region_name)만 평균 내림차순으로 조회하세요.",
                "hint": "regions JOIN 후 GROUP BY region_name, HAVING AVG(...) > (SELECT AVG(...) FROM housing_pension)",
                "answer": """SELECT
    r.region_name                    AS 지역명,
    ROUND(AVG(hp.pension_payment),1) AS "평균연금지급액(억)"
FROM housing_pension hp
JOIN regions r ON hp.region_id = r.region_id
GROUP BY r.region_name
HAVING AVG(hp.pension_payment) > (
    SELECT AVG(pension_payment) FROM housing_pension
)
ORDER BY "평균연금지급액(억)" DESC;""",
            },
        ]

        for q in quizzes:
            st.markdown(f"### 문제 {q['no']} &nbsp; {q['level']}")
            practice_block(conn, q["q"], q["answer"],
                           f"quiz_{q['no']}", hint=q["hint"])
            st.divider()

        st.markdown("""<div class="tip-box">
✅ <b>실수 방지 최종 체크리스트</b><br>
• NULL 비교 → <code>IS NULL</code> 사용 (<code>= NULL</code>은 항상 FALSE)<br>
• 집계함수 조건 → <code>WHERE</code> 아닌 <code>HAVING</code>에 작성<br>
• GROUP BY → SELECT의 비집계 컬럼 모두 포함<br>
• JOIN → <code>ON</code> 조건 누락 시 카테시안 곱 발생<br>
• JOIN 후 중복 컬럼명 → 테이블 별칭(lg.region_id, r.region_id)으로 구분<br>
• <code>LIKE '%값%'</code> → 대용량에서 Full Scan 발생 주의
</div>""", unsafe_allow_html=True)
