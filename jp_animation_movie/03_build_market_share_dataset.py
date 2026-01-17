from __future__ import annotations

from pathlib import Path
import pandas as pd

# =========================
# 설정
# =========================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

MOVIE_FILE = DATA_DIR / "boxoffice_top30_with_movieinfo.xlsx"
YEAR_FILE  = DATA_DIR / "KOBIS_총_관객수_및_매출액_연도별.xls"

COVID_BEFORE_MAX = 2019   # <= 2019: 코로나 이전
COVID_AFTER_MIN  = 2020   # >= 2024: 코로나 이후 
USE_YEAR_FROM = 2015

# =========================
# 출력 옵션
# =========================
pd.set_option("display.width", 160)
pd.set_option("display.max_columns", None)
pd.set_option("display.unicode.east_asian_width", True)

def fmt_pct(s: pd.Series) -> pd.Series:
    return (s * 100).round(4)

def fmt_int(s: pd.Series) -> pd.Series:
    return s.map(lambda x: f"{int(x):,}" if pd.notna(x) else "")

# =========================
# 로드
# =========================
def load_movies(path: Path) -> pd.DataFrame:
    # 연도별 박스오피스 2015~2025 데이터
    df = pd.read_excel(path)

    # 타입 정리
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["salesAcc"] = pd.to_numeric(df["salesAcc"], errors="coerce")
    df["audiAcc"]  = pd.to_numeric(df["audiAcc"], errors="coerce")

    # 불리언 정리 (이미 True/False여도 안전하게)
    for c in ["is_animation", "is_japan"]:
        df[c] = df[c].fillna(False).astype(bool)

    df = df.dropna(subset=["year", "salesAcc", "audiAcc"])
    df = df[df["year"] >= USE_YEAR_FROM].copy()

    # period 라벨(네 기준을 정확히 반영)
    df["period"] = pd.NA
    df.loc[df["year"] <= COVID_BEFORE_MAX, "period"] = "코로나 이전"
    df.loc[df["year"] >= COVID_AFTER_MIN,  "period"] = "코로나 이후"
    df = df.dropna(subset=["period"]).copy()

    return df

def load_year_base(path: Path) -> pd.DataFrame:
    # 연도별 총 관객수 및 매출액 데이터
    tables = pd.read_html(path)
    dfy = tables[1].copy()

    # MultiIndex -> 단일 컬럼
    dfy.columns = [f"{a}_{b}" for (a, b) in dfy.columns]

    year_base = (
        dfy[["연도_연도", "전체_매출액", "전체_관객수"]]
          .rename(columns={
              "연도_연도": "year",
              "전체_매출액": "total_sales",
              "전체_관객수": "total_audience",
          })
          .copy()
    )

    year_base["year"] = pd.to_numeric(year_base["year"], errors="coerce")
    year_base = year_base.dropna(subset=["year"])
    year_base["year"] = year_base["year"].astype(int)

    year_base["total_sales"] = pd.to_numeric(year_base["total_sales"], errors="coerce")
    year_base["total_audience"] = pd.to_numeric(year_base["total_audience"], errors="coerce")

    year_base = year_base[year_base["year"] >= USE_YEAR_FROM].copy()
    return year_base

# df, dfy 데이터 합치기
def build_df2(movies: pd.DataFrame, year_base: pd.DataFrame) -> pd.DataFrame:
    # 연도를 기준으로
    df2 = movies.merge(year_base, on="year", how="left")

    # 매출 점유율 = 해당 영화 매출액 / 그 해 전체 영화 매출액
    df2["sales_share"] = df2["salesAcc"] / df2["total_sales"]
    # 관객 점유율 = 해당 영화 관객 수 / 그 해 전체 영화 관객 수
    df2["audi_share"]  = df2["audiAcc"]  / df2["total_audience"]

    # 퍼센트로 보기 편하게!
    df2["sales_share_pct"] = fmt_pct(df2["sales_share"])
    df2["audi_share_pct"]  = fmt_pct(df2["audi_share"])

    print(df2)
    return df2

def main():
    movies = load_movies(MOVIE_FILE)      # 파일2 결과
    year_base = load_year_base(YEAR_FILE) # 연도별 전체 시장
    df2 = build_df2(movies, year_base)    # 점유율 파생

    # (선택이지만 강추) 폴더 없으면 생성
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 저장
    output = DATA_DIR / "analysis_master_df2.xlsx"
    df2.to_excel(output, index=False)

    print(f"✅ 저장 완료: {output}")

if __name__ == "__main__":
    main()

