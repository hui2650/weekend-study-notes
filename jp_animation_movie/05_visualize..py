from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

# =========================
# (옵션) 한글 폰트 설정 (Windows 기준)
# =========================
# 이미 너가 쓰던 설정이 있으면 이 블록은 생략해도 됨

font_path ='C:/Windows/Fonts/malgun.ttf'
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)

plt.rcParams['axes.unicode_minus'] =False

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

def load_master_df2(path: Path) -> pd.DataFrame:
    """
    analysis_master_df2.xlsx를 로드
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
# 그래프 공통 컬러/스타일 
# =========================
COLOR_JP = "#E63946"      # 일본 애니 (강조 레드)
COLOR_NONJP = "#1D3557"   # 일반 애니 (딥 네이비)
COLOR_BAR = "#A8DADC"     # 보조 막대 (민트)
COLOR_GRAY = "#6C757D"

TITLE_SIZE = 16
LABEL_SIZE = 12
TICK_SIZE = 10

# =========================
# 그래프 저장 설정
# =========================
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

def save_fig(name: str):
    """
    현재 활성화된 figure를 png로 저장
    """
    plt.savefig(
        OUTPUT_DIR / f"{name}.png",
        dpi=300,
        bbox_inches="tight"
    )

def _style_axes(ax):
    ax.grid(True, axis="y", alpha=0.25, linestyle="--", linewidth=0.8)
    ax.tick_params(axis="both", labelsize=TICK_SIZE)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

def _annotate_max(ax, x_series, y_series, *, fmt="{:.2f}%"):
    # 최대값에 주석
    idx = y_series.idxmax()
    x = x_series.loc[idx]
    y = y_series.loc[idx]
    ax.scatter([x], [y], s=60, color=COLOR_JP, zorder=5)
    ax.annotate(
        f"최대 {fmt.format(y)}",
        xy=(x, y),
        xytext=(x, y + (y_series.max() * 0.08 if y_series.max() else 0.5)),
        ha="center",
        fontsize=10,
        color=COLOR_GRAY,
        arrowprops=dict(arrowstyle="->", color=COLOR_GRAY, lw=1),
    )

# =========================
# 1) 연도별 일본 애니 흥행 추이 (라인 + 막대)
# =========================
def plot_trend_jp_anim_by_year(df2: pd.DataFrame) -> None:
    df = df2.copy()

    years = list(range(USE_YEAR_FROM, 2026))  # 2015~2025 고정

    jp = df[(df["is_animation"] == True) & (df["is_japan"] == True)].copy()

    trend = (
        jp.groupby("year", as_index=False)
          .agg(
              jp_anim_count=("movieNm", "count"),
              jp_sum_audi_share=("audi_share", "sum"),
          )
    )

    # ✅ 모든 연도 채우기 (없는 해는 0)
    trend = (
        pd.DataFrame({"year": years})
          .merge(trend, on="year", how="left")
          .fillna({"jp_anim_count": 0, "jp_sum_audi_share": 0})
    )

    trend["jp_sum_audi_share_pct"] = (trend["jp_sum_audi_share"] * 100).round(4)

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 라인: 연간 관객 점유율 합(%)
    ax1.plot(
        trend["year"],
        trend["jp_sum_audi_share_pct"],
        marker="o",
        linewidth=2.8,
        markersize=6.5,
        color=COLOR_JP,
        label="관객 점유율 합(%)"
    )
    ax1.set_title("연도별 일본 애니 흥행 추이", fontsize=TITLE_SIZE, pad=12)
    ax1.set_xlabel("연도", fontsize=LABEL_SIZE)
    ax1.set_ylabel("일본 애니 연간 관객 점유율 합(%)", fontsize=LABEL_SIZE)
    ax1.set_xticks(years)
    ax1.set_xlim(min(years) - 0.3, max(years) + 0.3)
    _style_axes(ax1)

    # 주석: 최대값 표시
    _annotate_max(ax1, trend["year"], trend["jp_sum_audi_share_pct"], fmt="{:.2f}%")

    # 막대: 연간 편수 (보조축)
    ax2 = ax1.twinx()
    ax2.bar(
        trend["year"],
        trend["jp_anim_count"],
        alpha=0.35,
        color=COLOR_BAR,
        label="편수"
    )
    ax2.set_ylabel("일본 애니 편수(편)", fontsize=LABEL_SIZE)
    ax2.tick_params(axis="y", labelsize=TICK_SIZE)
    ax2.spines["top"].set_visible(False)

    # 범례(둘 다)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=10, frameon=False)

    plt.tight_layout()
    save_fig("01_trend_jp_animation_by_year")
    plt.show()

# =========================
# 2) 일본 애니 vs 일반 애니 평균 점유율 (전/후 비교, 그룹드 바)
# =========================
def plot_avg_share_jp_vs_nonjp_animation_by_period(df2: pd.DataFrame) -> None:
    df = df2.copy()

    # 애니만
    anim = df[df["is_animation"] == True].copy()

    # group 라벨 (일본 애니 / 일반 애니)
    anim["group"] = "일반 애니"
    anim.loc[anim["is_japan"] == True, "group"] = "일본 애니"

    summary = (
        anim.groupby(["period", "group"], as_index=False)
            .agg(
                avg_audi_share=("audi_share", "mean"),
                avg_sales_share=("sales_share", "mean"),
                movie_count=("movieNm", "count"),
            )
    )

    summary["avg_audi_share_pct"] = (summary["avg_audi_share"] * 100).round(2)
    summary["avg_sales_share_pct"] = (summary["avg_sales_share"] * 100).round(2)

    # period / group 순서 고정
    period_order = ["코로나 이전", "코로나 이후"]
    group_order = ["일본 애니", "일반 애니"]

    summary["period"] = pd.Categorical(summary["period"], categories=period_order, ordered=True)
    summary["group"] = pd.Categorical(summary["group"], categories=group_order, ordered=True)
    summary = summary.sort_values(["period", "group"])

    # 피벗으로 그리기 편하게
    pivot_audi = summary.pivot(index="period", columns="group", values="avg_audi_share_pct").reindex(period_order).fillna(0)

    x = range(len(pivot_audi.index))
    width = 0.38

    fig, ax = plt.subplots(figsize=(9.5, 5.4))

    bars_jp = ax.bar([i - width/2 for i in x], pivot_audi["일본 애니"], width=width, label="일본 애니", color=COLOR_JP)
    bars_non = ax.bar([i + width/2 for i in x], pivot_audi["일반 애니"], width=width, label="일반 애니", color=COLOR_NONJP, alpha=0.9)

    ax.set_title("일본 애니 vs 일반 애니 평균 관객 점유율 (코로나 전/후)", fontsize=TITLE_SIZE, pad=12)
    ax.set_xlabel("기간", fontsize=LABEL_SIZE)
    ax.set_ylabel("평균 관객 점유율(%)", fontsize=LABEL_SIZE)
    ax.set_xticks(list(x))
    ax.set_xticklabels(pivot_audi.index.astype(str), fontsize=TICK_SIZE)
    _style_axes(ax)

    # 값 라벨(막대 위)
    for b in list(bars_jp) + list(bars_non):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, h + 0.06, f"{h:.2f}%", ha="center", va="bottom", fontsize=9, color=COLOR_GRAY)

    # 주석: 전/후 일본 애니 변화량(Δ)
    jp_before = float(pivot_audi.loc["코로나 이전", "일본 애니"])
    jp_after = float(pivot_audi.loc["코로나 이후", "일본 애니"])
    delta = jp_after - jp_before
    ax.annotate(
        f"일본 애니 변화 Δ {delta:+.2f}%p",
        xy=(1 - width/2, jp_after),
        xytext=(1, max(jp_after, jp_before) + 0.9),
        fontsize=10,
        color=COLOR_GRAY,
        arrowprops=dict(arrowstyle="->", color=COLOR_GRAY, lw=1),
        ha="center"
    )

    ax.legend(fontsize=10, frameon=False)

    plt.tight_layout()
    save_fig("02_avg_share_jp_vs_nonjp_by_period")
    plt.show()

# =========================
# 3) 애니 시장 내 일본 애니 비중 (전/후 비교 바)
# =========================
def plot_jp_share_within_animation_market(df2: pd.DataFrame) -> None:
    df = df2.copy()

    # 애니 전체(분모)
    anim_total = (
        df[df["is_animation"] == True]
          .groupby("period", as_index=False)
          .agg(
              anim_sum_audi_share=("audi_share", "sum"),
              anim_sum_sales_share=("sales_share", "sum"),
          )
    )

    # 일본 애니(분자)
    jp_total = (
        df[(df["is_animation"] == True) & (df["is_japan"] == True)]
          .groupby("period", as_index=False)
          .agg(
              jp_sum_audi_share=("audi_share", "sum"),
              jp_sum_sales_share=("sales_share", "sum"),
          )
    )

    out = anim_total.merge(jp_total, on="period", how="left")
    out[["jp_sum_audi_share", "jp_sum_sales_share"]] = out[["jp_sum_audi_share", "jp_sum_sales_share"]].fillna(0)

    out["jp_within_anim_audi_pct"] = (out["jp_sum_audi_share"] / out["anim_sum_audi_share"] * 100).round(2)
    out["jp_within_anim_sales_pct"] = (out["jp_sum_sales_share"] / out["anim_sum_sales_share"] * 100).round(2)

    # period 순서 고정
    order = ["코로나 이전", "코로나 이후"]
    out["period"] = pd.Categorical(out["period"], categories=order, ordered=True)
    out = out.sort_values("period")

    x = range(len(out))
    width = 0.38

    fig, ax = plt.subplots(figsize=(9.5, 5.4))

    bars_audi = ax.bar([i - width/2 for i in x], out["jp_within_anim_audi_pct"], width=width, label="관객 기준", color=COLOR_JP)
    bars_sales = ax.bar([i + width/2 for i in x], out["jp_within_anim_sales_pct"], width=width, label="매출 기준", color=COLOR_NONJP, alpha=0.9)

    ax.set_title("애니 시장 내 일본 애니 비중 (코로나 전/후)", fontsize=TITLE_SIZE, pad=12)
    ax.set_xlabel("기간", fontsize=LABEL_SIZE)
    ax.set_ylabel("비중(%)", fontsize=LABEL_SIZE)
    ax.set_xticks(list(x))
    ax.set_xticklabels(out["period"].astype(str), fontsize=TICK_SIZE)
    _style_axes(ax)

    # 값 라벨
    for b in list(bars_audi) + list(bars_sales):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, h + 0.25, f"{h:.1f}%", ha="center", va="bottom", fontsize=9, color=COLOR_GRAY)

    # 주석: 관객 기준 증감
    before = float(out.loc[out["period"] == "코로나 이전", "jp_within_anim_audi_pct"].iloc[0])
    after = float(out.loc[out["period"] == "코로나 이후", "jp_within_anim_audi_pct"].iloc[0])
    ax.annotate(
        f"관객 기준 Δ {after-before:+.1f}%p",
        xy=(1 - width/2, after),
        xytext=(1, max(before, after) + 8),
        fontsize=10,
        color=COLOR_GRAY,
        arrowprops=dict(arrowstyle="->", color=COLOR_GRAY, lw=1),
        ha="center"
    )

    ax.legend(fontsize=10, frameon=False)

    plt.tight_layout()
    save_fig("03_jp_share_within_animation_market")
    plt.show()


# =========================
# 4) 연도별 평균 점유율 라인 2개 겹치기 (역전 시점 강조)
# =========================
def plot_line_avg_share_jp_vs_nonjp_by_year(df2: pd.DataFrame) -> None:
    df = df2.copy()

    # 애니만
    anim = df[df["is_animation"] == True].copy()

    # 그룹 라벨
    anim["group"] = "일반 애니"
    anim.loc[anim["is_japan"] == True, "group"] = "일본 애니"

    # 연도별 평균(영화 1편당 평균 점유율)
    yearly_avg = (
        anim.groupby(["year", "group"], as_index=False)
            .agg(
                avg_audi_share=("audi_share", "mean"),
                count=("movieNm", "count"),
            )
            .sort_values(["year", "group"])
    )

    # 피벗
    pivot = yearly_avg.pivot(index="year", columns="group", values="avg_audi_share").fillna(0).sort_index()
    pivot_pct = pivot * 100

    # 없는 컬럼 대비
    for col in ["일반 애니", "일본 애니"]:
        if col not in pivot_pct.columns:
            pivot_pct[col] = 0.0

    fig, ax = plt.subplots(figsize=(11.5, 6))

    ax.plot(
        pivot_pct.index,
        pivot_pct["일반 애니"],
        marker="o",
        linewidth=2.0,
        markersize=6.0,
        linestyle="--",
        color=COLOR_NONJP,
        label="일반 애니 (연도별 평균)"
    )
    ax.plot(
        pivot_pct.index,
        pivot_pct["일본 애니"],
        marker="o",
        linewidth=2.8,
        markersize=6.5,
        color=COLOR_JP,
        label="일본 애니 (연도별 평균)"
    )

    ax.set_title("연도별 애니 평균 관객 점유율(%) 추이: 일본 애니 vs 일반 애니", fontsize=TITLE_SIZE, pad=12)
    ax.set_xlabel("연도", fontsize=LABEL_SIZE)
    ax.set_ylabel("영화 1편당 평균 관객 점유율(%)", fontsize=LABEL_SIZE)
    ax.grid(True, axis="y", alpha=0.25, linestyle="--", linewidth=0.8)
    ax.tick_params(axis="both", labelsize=TICK_SIZE)
    ax.legend(loc="upper left", fontsize=10, frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # ✅ 역전 시점(일본 애니 평균이 일반 애니 평균을 처음으로 초과한 해)
    diff = pivot_pct["일본 애니"] - pivot_pct["일반 애니"]
    if (diff > 0).any():
        cross_year = int(diff[diff > 0].index[0])
        ax.axvline(cross_year, color=COLOR_GRAY, linestyle=":", linewidth=1.2, alpha=0.9)
        top_y = max(pivot_pct["일본 애니"].max(), pivot_pct["일반 애니"].max())
        ax.text(
            cross_year + 0.05,
            top_y,
            f"역전 시작: {cross_year}년",
            fontsize=10,
            color=COLOR_GRAY,
            va="top"
        )

    plt.tight_layout()
    save_fig("04_avg_share_trend_jp_vs_nonjp_by_year")
    plt.show()


# =========================
# 실행부
# =========================

def main():
    df2 = load_master_df2(MASTER_FILE)

    plot_trend_jp_anim_by_year(df2)
    plot_avg_share_jp_vs_nonjp_animation_by_period(df2)
    plot_jp_share_within_animation_market(df2)
    plot_line_avg_share_jp_vs_nonjp_by_year(df2)

if __name__ == "__main__":
    main()