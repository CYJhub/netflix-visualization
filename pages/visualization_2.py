import streamlit as st
import pandas as pd
import folium
import country_converter as coco  # 국가 이름을 코드로 변환
from streamlit_folium import st_folium
import os

# 📌 Streamlit UI
st.title("Netflix 주간별 Top 1 Visualization")

# 🌍 국가별 위도/경도 데이터 (ISO 코드 기반) - 캐싱
@st.cache_data
def get_country_coords():
    iso_codes = [
        "AR", "AU", "AT", "BS", "BH", "BD", "BE", "BO", "BR", "BG", "CA", "CL", "CO", "CR", "HR", "CY", "CZ", "DK",
        "DO", "EC", "EG", "SV", "EE", "FI", "FR", "DE", "GR", "GP", "GT", "HN", "HK", "HU", "IS", "IN", "ID", "IE",
        "IL", "IT", "JM", "JP", "JO", "KE", "KW", "LV", "LB", "LT", "LU", "MY", "MV", "MT", "MQ", "MU", "MX", "MA",
        "NL", "NC", "NZ", "NI", "NG", "NO", "OM", "PK", "PA", "PY", "PE", "PH", "PL", "PT", "QA", "RO", "RE", "SA",
        "RS", "SG", "SK", "SI", "ZA", "KR", "ES", "LK", "SE", "CH", "TW", "TH", "TT", "TR", "UA", "AE", "GB", "US",
        "UY", "VE", "VN"
    ]

    latitudes = [
        -38.4161, -25.2744, 47.5162, 25.0343, 26.0667, 23.685, 50.8503, -16.5000, -14.235, 42.7339, 56.1304, -35.6751,
        4.5709, 9.7489, 45.1000, 35.1264, 49.8175, 56.2639, 18.7357, -1.8312, 26.8206, 13.6929, 58.5953, 61.9241,
        48.8566, 51.1657, 39.0742, 16.2650, 15.7835, 15.2000, 22.3193, 47.1625, 64.9631, 20.5937, -0.7893, 53.4129,
        31.0461, 41.8719, 18.1096, 35.6828, 31.9632, -1.2864, 29.3759, 56.8796, 33.8547, 55.1694, 49.8153, 4.2105,
        3.2028, 35.8997, 14.6415, -20.3484, 23.6345, 31.7917, 52.3676, -20.9043, -40.9006, 12.8654, 9.0820, 60.4720,
        21.5126, 30.3753, 8.9824, -23.4425, -9.1900, 13.4125, 51.9194, 39.3999, 25.3548, 45.9432, -21.1151, 23.8859,
        44.0165, 1.3521, 48.6690, 46.1512, -30.5595, 37.5665, 40.4637, 7.8731, 60.1282, 46.8182, 23.6978, 15.8700,
        10.6918, 38.9637, 48.3794, 25.2760, 55.3781, 37.0902, -32.5228, 6.4238, 14.0583
    ]

    longitudes = [
        -63.6167, 133.7751, 14.5501, -77.3963, 50.5577, 90.3563, 4.3517, -68.1500, -51.9253, 25.4858, -106.3468,
        -71.5429, -74.2973, -83.7534, 15.2000, 33.4299, 15.4720, 9.5018, -70.1627, -78.1834, 30.8025, -89.2182,
        25.0136, 25.7482, 2.3522, 10.4515, 21.8243, -61.5500, -90.2308, -86.2419, 114.1694, 19.5033, -19.0208,
        78.9629, 113.9213, -8.2439, 34.8516, 12.5674, -77.2975, 139.7595, 35.9304, 36.8219, 47.6581, 24.6032,
        35.8623, 23.8813, 114.1512, 101.9758, 73.2207, 14.3754, -61.0242, 57.5522, -102.5528, -7.0926, 4.9041,
        165.6180, 172.6362, -85.2072, 8.6753, 8.4689, 55.9233, 69.3451, -79.5199, -58.4438, -75.0152, 121.7740,
        19.1451, -8.2245, 51.1839, 24.9668, 45.0792, 44.4249, 46.1512, 22.9375, 103.8198, 19.6990, 14.9955, 22.9375,
        -30.5595, 126.9780, -3.7038, 80.7718, 18.6435, 8.2275, 120.9605, 100.9925, 31.1656, 35.2433, 31.1656,
        -95.7129, -3.4360, -95.7129, -55.7658
    ]

    return pd.DataFrame({"country_iso2": iso_codes, "latitude": latitudes, "longitude": longitudes})


# 데이터 캐싱
@st.cache_data
def load_data():
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    return (
        pd.read_csv(os.path.join(base_path, "2-2_movies.csv")),
        pd.read_csv(os.path.join(base_path, "2-2_tv.csv")),
    )


# 🏆 1위 작품만 필터링
movies_df, series_df = load_data()
movies_top1 = movies_df[movies_df["weekly_rank"] == 1]
series_top1 = series_df[series_df["weekly_rank"] == 1]
top1_df = pd.concat([movies_top1, series_top1], ignore_index=True)

# 국가 데이터 병합
country_coords = get_country_coords()
top1_df = top1_df.merge(country_coords, on="country_iso2", how="left")

# 📅 주간 목록
weeks = sorted(top1_df["week"].unique(), reverse=True)

# 📌 주간 선택 (Streamlit UI 추가)
selected_week = st.selectbox("주간을 선택하세요:", weeks)

# 🏆 주간별 데이터 필터링 (캐싱)
@st.cache_data
def filter_week_data(week):
    week_df = top1_df[top1_df["week"] == week]
    weekly_counts = week_df.groupby("show_title")["country_iso2"].nunique()
    week_df["category"] = week_df["show_title"].map(lambda x: "Global Hit" if weekly_counts[x] > 1 else "National Hit")
    return week_df

week_df = filter_week_data(selected_week)

# 🌍 국가별 작품 수 계산
country_counts_df = week_df.groupby(["country_iso2", "category"]).size().reset_index(name="count")

# ✅ 색상 설정 (국가 히트: 민트 / 글로벌 히트: 핑크)
color_map = {"National Hit": "#90EE90", "Global Hit": "lightpink"}

# 🗺️ Folium 지도 생성
m = folium.Map(location=[20, 0], zoom_start=2)

# 지도에 원 추가 (국가별 작품 수 반영)
for _, row in country_counts_df.iterrows():
    country_info = country_coords[country_coords["country_iso2"] == row["country_iso2"]]
    if not country_info.empty:
        lat, lon = country_info.iloc[0]["latitude"], country_info.iloc[0]["longitude"]
        radius = min(row["count"] * 5, 30)  # 작품 수에 비례, 최대 크기 제한

        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color_map[row["category"]],
            fill=True,
            fill_color=color_map[row["category"]],
            fill_opacity=0.8,
            popup=f"{row['category']}<br>국가 코드: {row['country_iso2']}<br>1위 작품 수: {row['count']}",
        ).add_to(m)

st.caption(f"주간별 1위 작품을 글로벌 히트 vs 국가 히트로 구분하여 시각화합니다. 현재 주간: **{selected_week}**")

# 지도 렌더링
st_folium(m, width=800, height=500)

# 국가별 1위 작품 목록 표시
st.write(f"### {selected_week} 주간 국가별 1위 작품 목록")
st.dataframe(week_df[["country_name", "show_title", "category"]].drop_duplicates())
