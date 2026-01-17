from pathlib import Path
import pandas as pd
import re

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

all_years_df = []

def to_int(series: pd.Series) -> pd.Series:
    """'1,234,567' 같은 문자열을 int로 변환"""
    return pd.to_numeric(series.astype(str).str.replace(",", ""), errors="coerce")

for year in range(2015, 2026):
    file_path = DATA_DIR / f"KOBIS_연도별박스오피스_{year}.xls"
    print("처리 중:", file_path)

    # 1) HTML 테이블 읽기 (파일 안의 모든 table을 리스트로 반환)
    tables = pd.read_html(file_path, encoding="utf-8")  # 인코딩은 필요시 cp949로 바꿔봐

    # 2) 보통 첫 번째 테이블이 본문인 경우가 많아서 일단 tables[0] 사용
    #    만약 컬럼이 이상하면 아래 "테이블 선택" 로직을 켜면 됨
    df = tables[0]

    # 3) 컬럼명 정리 (KOBIS 표 컬럼명에 맞춰 통일)
    #    실제 컬럼명이 조금 다를 수 있으니 여기서 맞춰주면 됨
    df = df.rename(columns={
        "영화명": "movieNm",
        "개봉일": "openDt",
        "관객수": "audiAcc",
        "매출액": "salesAcc",
        "스크린수": "scrnCnt",
        "순위": "rank"
    })

    # 4) 필수 컬럼 체크 (없으면 테이블이 잘못 선택된 것)
    required = {"movieNm", "openDt", "audiAcc"}
    if not required.issubset(df.columns):
        # ✅ 테이블이 여러 개인 경우: 필요한 컬럼이 있는 테이블을 찾아서 선택
        picked = None
        for t in tables:
            t2 = t.rename(columns={
                "영화명": "movieNm",
                "개봉일": "openDt",
                "관객수": "audiAcc",
                "매출액": "salesAcc",
                "스크린수": "scrnCnt",
                "순위": "rank"
            })
            if required.issubset(t2.columns):
                picked = t2
                break
        if picked is None:
            raise ValueError(f"{file_path}에서 박스오피스 테이블을 찾지 못함. 컬럼들: {list(df.columns)}")
        df = picked

    # 5) 숫자 컬럼들을 숫자로 변환
    df["audiAcc"] = to_int(df["audiAcc"])
    if "salesAcc" in df.columns:
        df["salesAcc"] = to_int(df["salesAcc"])
    else:
        df["salesAcc"] = pd.NA

    if "scrnCnt" in df.columns:
        df["scrnCnt"] = to_int(df["scrnCnt"])
    else:
        df["scrnCnt"] = pd.NA

    # 6) 관객수 기준 Top30 자르기
    df_top30 = df.sort_values("audiAcc", ascending=False).head(30).copy()

    # 7) 집계연도 컬럼 추가
    df_top30["year"] = year

    # 8) 필요한 컬럼만 정리 (원하면 더 남겨도 됨)
    keep = ["year", "movieNm", "openDt", "salesAcc", "audiAcc", "scrnCnt"]
    if "rank" in df_top30.columns:
        keep.insert(1, "rank")

    all_years_df.append(df_top30[keep])

# 9) 11개 연도 Top30 합치기 → 330행
final_df = pd.concat(all_years_df, ignore_index=True)

# 10) 저장
output_xlsx = DATA_DIR / "boxoffice_top30_2015_2025.xlsx"
output_csv = DATA_DIR / "boxoffice_top30_2015_2025.csv"

final_df.to_excel(output_xlsx, index=False)
final_df.to_csv(output_csv, index=False, encoding="utf-8-sig")

print(f"✅ 완료: {output_xlsx} 생성")
print("총 행 개수:", len(final_df))
print(final_df.head())
