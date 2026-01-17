from __future__ import annotations

import re
import time
from pathlib import Path

import pandas as pd
import requests

# =========================
# 설정
# =========================
KOBIS_KEY = "d98ec60f84b6fde17b49119958d77bb6"  # 네 키 (나중에 .env로 빼는 게 베스트)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "boxoffice_top30_2015_2025.xlsx"
OUTPUT_FILE = DATA_DIR / "boxoffice_top30_with_movieinfo.xlsx"
FAIL_LOG_FILE = DATA_DIR / "movieCd_match_failed.csv"

API_SLEEP = 0.12
TIMEOUT = 10

SEARCH_URL = "https://kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json"
INFO_URL = "https://kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json"

session = requests.Session()

# =========================
# 유틸
# =========================
def norm_openDt(openDt: str) -> str:
    digits = re.sub(r"\D", "", str(openDt))
    return digits[:8]

def clean_movieNm(name: str) -> str:
    s = str(name).replace("\xa0", " ").strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("\u200b", "").replace("\ufeff", "")
    return s

def call_json(url: str, params: dict) -> dict:
    r = session.get(url, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    return data

# =========================
# 1) movieCd 찾기
# =========================
def find_movieCd(movieNm: str, openDt_norm: str) -> str:
    movieNm = clean_movieNm(movieNm)
    year = openDt_norm[:4] if len(openDt_norm) >= 4 else ""

    params = {
        "key": KOBIS_KEY,
        "movieNm": movieNm,
        "curPage": 1,
        "itemPerPage": 20,
    }

    # ✅ KOBIS는 openStartDt/openEndDt를 YYYY(연도)로 받음
    if year:
        params["openStartDt"] = year
        params["openEndDt"] = year

    data = call_json(SEARCH_URL, params)

    # faultInfo면 실패
    if "faultInfo" in data:
        return ""

    lst = data.get("movieListResult", {}).get("movieList", []) or []
    if not lst:
        # 연도 필터가 너무 빡센 케이스 대비: 필터 없이 1회 재시도
        params2 = {
            "key": KOBIS_KEY,
            "movieNm": movieNm,
            "curPage": 1,
            "itemPerPage": 20,
        }
        data2 = call_json(SEARCH_URL, params2)
        if "faultInfo" in data2:
            return ""
        lst = data2.get("movieListResult", {}).get("movieList", []) or []
        if not lst:
            return ""

    # 완전일치 우선
    exact = next((m for m in lst if clean_movieNm(m.get("movieNm", "")) == movieNm), None)
    picked = exact or lst[0]
    return picked.get("movieCd", "") or ""

# =========================
# 2) movieInfo 가져오기 (genres + nations)
# =========================
def fetch_movieinfo(movieCd: str) -> tuple[str, str]:
    """
    return: (genres_csv, nations_csv)
    """
    params = {"key": KOBIS_KEY, "movieCd": movieCd}
    data = call_json(INFO_URL, params)

    if "faultInfo" in data:
        return "", ""

    movie = data.get("movieInfoResult", {}).get("movieInfo", {}) or {}

    genres = movie.get("genres", []) or []
    nations = movie.get("nations", []) or []

    genres_csv = ", ".join([g.get("genreNm", "") for g in genres if g.get("genreNm")])
    nations_csv = ", ".join([n.get("nationNm", "") for n in nations if n.get("nationNm")])

    return genres_csv, nations_csv

# =========================
# 메인
# =========================
def main():
    df = pd.read_excel(INPUT_FILE)

    # 혹시 한글 컬럼이면 통일
    df = df.rename(columns={"영화명": "movieNm", "개봉일": "openDt"})

    must = {"movieNm", "openDt"}
    if not must.issubset(df.columns):
        raise ValueError(f"필수 컬럼이 없어요. 필요: {must}, 현재: {list(df.columns)}")

    df["movieNm"] = df["movieNm"].astype(str).apply(clean_movieNm)
    df["openDt_norm"] = df["openDt"].apply(norm_openDt)

    # 캐시(중복 호출 절감)
    movieCd_cache: dict[tuple[str, str], str] = {}
    info_cache: dict[str, tuple[str, str]] = {}  # movieCd -> (genres, nations)

    movieCds, genres_list, nations_list = [], [], []
    failed_rows = []

    total = len(df)

    for idx, (_, row) in enumerate(df.iterrows(), start=1):
        key = (row["movieNm"], row["openDt_norm"])

        # (A) movieCd
        if key in movieCd_cache:
            movieCd = movieCd_cache[key]
        else:
            movieCd = find_movieCd(row["movieNm"], row["openDt_norm"])
            movieCd_cache[key] = movieCd
            time.sleep(API_SLEEP)

        movieCds.append(movieCd)

        # (B) genres + nations
        if not movieCd:
            genres_list.append("")
            nations_list.append("")
            failed_rows.append({
                "year": row.get("year", ""),
                "movieNm": row["movieNm"],
                "openDt": row["openDt"],
                "openDt_norm": row["openDt_norm"],
                "reason": "no_movieCd",
            })
        else:
            if movieCd in info_cache:
                genres_csv, nations_csv = info_cache[movieCd]
            else:
                genres_csv, nations_csv = fetch_movieinfo(movieCd)
                info_cache[movieCd] = (genres_csv, nations_csv)
                time.sleep(API_SLEEP)

            genres_list.append(genres_csv)
            nations_list.append(nations_csv)

        # ✅ 진행상황 출력 (10개 단위 + 마지막)
        if idx % 10 == 0 or idx == total:
            print(f"{idx}/{total} 불러오기 완료")


    df["movieCd"] = movieCds
    df["genres"] = genres_list
    df["nations"] = nations_list

    # 파생 컬럼
    df["is_animation"] = df["genres"].fillna("").str.contains("애니메이션", na=False)
    df["is_japan"] = df["nations"].fillna("").str.contains("일본", na=False)

    df.to_excel(OUTPUT_FILE, index=False)

    failed_df = pd.DataFrame(failed_rows)
    failed_df.to_csv(FAIL_LOG_FILE, index=False, encoding="utf-8-sig")

    print("✅ 완료:", OUTPUT_FILE)
    print("movieCd 매칭 실패 개수:", (df["movieCd"].fillna("") == "").sum())
    print("실패 로그:", FAIL_LOG_FILE)

if __name__ == "__main__":
    main()
