from __future__ import annotations

from pathlib import Path
import pandas as pd

# =========================
# 설정
# =========================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

MASTER_FILE = DATA_DIR / "analysis_master_df2.xlsx"

COVID_BEFORE_MAX = 2019   # <= 2019: 코로나 이전
COVID_AFTER_MIN  = 2020   # >= 2020: 코로나 이후
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
# 로드 (✅ 마스터 파일만)
# =========================
def load_master_df2(path: Path) -> pd.DataFrame:
    """
    analysis_master_df2.xlsx를 로드해서
    분석에 필요한 타입/결측/기간 라벨을 정리한다.
    """
    df2 = pd.read_excel(path)

    # ---- 필수 컬럼 체크 (파일 깨졌을 때 바로 알림)
    required_cols = {
        "year",
        "movieNm",
        "salesAcc",
        "audiAcc",
        "is_animation",
        "is_japan",
        "sales_share",
        "audi_share",
        "sales_share_pct",
        "audi_share_pct",
    }
    missing = required_cols - set(df2.columns)
    if missing:
        raise ValueError(f"MASTER_FILE에 필수 컬럼이 없습니다: {sorted(missing)}")


    return df2


# =========================
# 분석
# =========================

"""
연도별 일본 애니메이션 추이
"""
def trend_jp_animation_by_year(df2: pd.DataFrame) -> pd.DataFrame:

    jp = df2[(df2["is_animation"] == True) & (df2["is_japan"] == True)].copy()

    out = (
        jp.groupby("year", as_index=False)
          .agg(
              jp_anim_count=("movieNm", "count"),
              jp_avg_audi_share=("audi_share", "mean"),
              jp_sum_audi_share=("audi_share", "sum"),
              jp_avg_sales_share=("sales_share", "mean"),
              jp_sum_sales_share=("sales_share", "sum"),
          )
          .sort_values("year")
    )

    out["jp_avg_audi_share_pct"] = (out["jp_avg_audi_share"] * 100).round(4)
    out["jp_sum_audi_share_pct"] = (out["jp_sum_audi_share"] * 100).round(4)
    out["jp_avg_sales_share_pct"] = (out["jp_avg_sales_share"] * 100).round(4)
    out["jp_sum_sales_share_pct"] = (out["jp_sum_sales_share"] * 100).round(4)

    out = out.drop(columns=[
        "jp_avg_audi_share",
        "jp_sum_audi_share",
        "jp_avg_sales_share",
        "jp_sum_sales_share",
    ])

    return out

"""
일본 애니메이션의 흥행 양상 변화 (Top10 사례 제시)
"""
def top_n_movies(
    df2: pd.DataFrame,
    period: str,
    *,
    only_animation: bool = True,
    only_japan: bool = True,
    sort_by: str = "audi_share",
    n: int = 5,
) -> pd.DataFrame:
    """
    특정 기간(period)에서 조건에 맞는 영화 중
    '시장 점유율' 기준 TOP N 영화를 추출하는 함수

    기본 설정:
    - 애니메이션만
    - 일본 영화만
    - 관객 점유율(audi_share) 기준 정렬
    """

    cond = df2["period"].eq(period)

    if only_animation:
        cond &= df2["is_animation"].eq(True)

    if only_japan:
        cond &= df2["is_japan"].eq(True)

    cols = [
        "year",
        "rank",
        "movieNm",
        "nations",
        "genres",
        "audiAcc",
        "audi_share_pct",
        "salesAcc",
        "sales_share_pct",
    ]

    # rank 없는 경우 대비
    cols = [c for c in cols if c in df2.columns]

    out = (
        df2.loc[cond]
           .sort_values(sort_by, ascending=False)
           .head(n)
           .loc[:, cols]
           .copy()
    )

    out["audiAcc"] = fmt_int(out["audiAcc"])
    out["salesAcc"] = fmt_int(out["salesAcc"])

    return out


"""
일본 애니메이션의 ‘절대적 시장 영향력 변화’
"""
def make_summary(df2: pd.DataFrame) -> pd.DataFrame:
    """
    코로나 전/후에서
    일본 애니메이션(= 애니메이션 & 일본)이
    전체 영화 시장에서 차지하는 평균적 위상을 요약

    - 평균 점유율
    - 중앙값 점유율
    """
    df2 = df2.copy()
    df2["is_jp_anim"] = df2["is_animation"] & df2["is_japan"]

    out = (
        df2.groupby(["period", "is_jp_anim"], as_index=False)
           .agg(
               n=("movieNm", "count"),
               avg_audi_share=("audi_share", "mean"),
               median_audi_share=("audi_share", "median"),
               avg_sales_share=("sales_share", "mean"),
               median_sales_share=("sales_share", "median"),
           )
    )

    out["avg_audi_share_pct"] = fmt_pct(out["avg_audi_share"])
    out["median_audi_share_pct"] = fmt_pct(out["median_audi_share"])
    out["avg_sales_share_pct"] = fmt_pct(out["avg_sales_share"])
    out["median_sales_share_pct"] = fmt_pct(out["median_sales_share"])

    return out.drop(columns=[
        "avg_audi_share",
        "median_audi_share",
        "avg_sales_share",
        "median_sales_share",
    ])


"""
애니메이션 장르 내부에서의 상대적 위치 변화
"""
def compare_animation_groups(df2: pd.DataFrame) -> pd.DataFrame:
    """
    코로나 이전 / 이후를 기준으로
    애니메이션을 '일본 애니'와 '일반 애니'로 나누어

    1) 전체 영화 시장 내 편수 비중
    2) 평균 관객 점유율
    3) 평균 매출 점유율
    """
    df2 = df2.copy()

    anim = df2[df2["is_animation"] == True].copy()

    anim["group"] = pd.NA
    anim.loc[anim["is_japan"] == True,  "group"] = "일본 애니"
    anim.loc[anim["is_japan"] == False, "group"] = "일반 애니"

    total_movies = (
        df2.groupby("period")
           .size()
           .rename("total_movies")
           .reset_index()
    )

    summary = (
        anim.groupby(["period", "group"])
            .agg(
                movie_count=("movieNm", "count"),
                avg_audi_share=("audi_share", "mean"),
                avg_sales_share=("sales_share", "mean"),
            )
            .reset_index()
    )

    summary = summary.merge(total_movies, on="period", how="left")

    summary["movie_ratio_pct"] = (
        summary["movie_count"] / summary["total_movies"] * 100
    ).round(2)

    summary["avg_audi_share_pct"] = (summary["avg_audi_share"] * 100).round(2)
    summary["avg_sales_share_pct"] = (summary["avg_sales_share"] * 100).round(2)

    out = summary[[
        "period",
        "group",
        "movie_count",
        "movie_ratio_pct",
        "avg_audi_share_pct",
        "avg_sales_share_pct",
    ]].sort_values(["period", "group"])

    return out


"""
애니 시장 내 일본 애니 비중 변화 분석
"""
def jp_share_within_animation_market(df2: pd.DataFrame) -> pd.DataFrame:
    """
    코로나 전/후로 '애니 시장 내 일본 애니 비중' 비교
    """
    anim_total = (
        df2[df2["is_animation"] == True]
          .groupby("period", as_index=False)
          .agg(
              anim_sum_audi_share=("audi_share", "sum"),
              anim_sum_sales_share=("sales_share", "sum"),
          )
    )

    jp_total = (
        df2[(df2["is_animation"] == True) & (df2["is_japan"] == True)]
          .groupby("period", as_index=False)
          .agg(
              jp_sum_audi_share=("audi_share", "sum"),
              jp_sum_sales_share=("sales_share", "sum"),
          )
    )

    out = anim_total.merge(jp_total, on="period", how="left")
    out[["jp_sum_audi_share", "jp_sum_sales_share"]] = out[["jp_sum_audi_share", "jp_sum_sales_share"]].fillna(0)

    out["jp_within_anim_audi"] = out["jp_sum_audi_share"] / out["anim_sum_audi_share"]
    out["jp_within_anim_sales"] = out["jp_sum_sales_share"] / out["anim_sum_sales_share"]

    out["anim_sum_audi_share_pct"] = (out["anim_sum_audi_share"] * 100).round(4)
    out["jp_sum_audi_share_pct"] = (out["jp_sum_audi_share"] * 100).round(4)
    out["jp_within_anim_audi_pct"] = (out["jp_within_anim_audi"] * 100).round(2)

    out["anim_sum_sales_share_pct"] = (out["anim_sum_sales_share"] * 100).round(4)
    out["jp_sum_sales_share_pct"] = (out["jp_sum_sales_share"] * 100).round(4)
    out["jp_within_anim_sales_pct"] = (out["jp_within_anim_sales"] * 100).round(2)

    out = out[[
        "period",
        "anim_sum_audi_share_pct",
        "jp_sum_audi_share_pct",
        "jp_within_anim_audi_pct",
        "anim_sum_sales_share_pct",
        "jp_sum_sales_share_pct",
        "jp_within_anim_sales_pct",
    ]].sort_values("period")

    return out



# =========================
# 실행부
# =========================
def main():
    df2 = load_master_df2(MASTER_FILE)

    print("\n=== [추이] 연도별 일본 애니메이션 등장/점유율 추이 ===")
    trend_year = trend_jp_animation_by_year(df2)
    print(trend_year.to_string(index=False))
    print()

    print("\n=== [TOP10] 코로나 이전 일본 애니메이션 (audi_share 기준) ===")
    print(top_n_movies(df2, "코로나 이전", n=10).to_string(index=False))
    print()

    print("\n=== [TOP10] 코로나 이후 일본 애니메이션 (audi_share 기준) ===")
    print(top_n_movies(df2, "코로나 이후", n=10).to_string(index=False))
    print()

    print("\n=== [요약] 코로나 전/후 × 일본애니 여부(시장 점유율 평균/중앙값) ===")
    print(make_summary(df2).to_string(index=False))
    print()

    print("\n=== [비교] 일본 애니 vs 일반 애니 (코로나 전/후) ===")
    print(compare_animation_groups(df2).to_string(index=False))
    print()

    print("\n=== [비중] 애니 시장 내 일본 애니 점유 비중 (코로나 전/후) ===")
    share_within_anim = jp_share_within_animation_market(df2)
    print(share_within_anim.to_string(index=False))
    print()

if __name__ == "__main__":
    main()
