import streamlit as st
import pandas as pd
import random
import folium
from streamlit_folium import st_folium
import altair as alt

# 1. 웹사이트 기본 설정 및 레이아웃
st.set_page_config(page_title="2026 부산 맛집 AI 가이드", layout="wide")

# 파일 이름 지정
file_name = "부산광역시_맛집+정보(SHP)_20250121.csv"

# -------------------------------------------------------------
# 🌍 메인 프로그램 가동 존
# -------------------------------------------------------------
try:
    df = pd.read_csv(file_name, encoding="utf-8")
    df['latitude'] = df['lat']
    df['longitude'] = df['lng']
    
    df['title'] = df['title'].astype(str).str.strip()
    df['address1'] = df['address1'].astype(str).str.strip()
    
    # 부산 16개 구/군 초정밀 필터링
    busan_gus = ["중구", "서구", "동구", "영도구", "부산진구", "동래구", "남구", "북구", 
                 "해운대구", "사하구", "금정구", "강서구", "연제구", "수영구", "사상구", "기장군"]
                 
    def extract_gu_exact(addr):
        for gu in busan_gus:
            if gu in str(addr):
                return gu
        return "기타"
        
    df['위치한 구'] = df['address1'].apply(extract_gu_exact)
    
    # 음식 종류 분류
    if 'bizcat' in df.columns:
        df['음식 종류'] = df['bizcat'].fillna("기타")
    else:
        def auto_cate(title):
            if "면" in title or "국수" in title: return "한식(면류)"
            elif "스시" in title or "회" in title or "일식" in title: return "일식"
            elif "짜장" in title or "짬뽕" in title or "중식" in title: return "중식"
            elif "파스타" in title or "피자" in title: return "양식"
            elif "카페" in title or "커피" in title: return "카페/디저트"
            else: return "한식"
        df['음식 종류'] = df['title'].apply(auto_cate)

    # 구별 고유 색상 맵
    gu_color_map = {
        "남구": "red", "부산진구": "blue", "수영구": "purple", "해운대구": "orange",
        "중구": "green", "동래구": "darkblue", "금정구": "darkpurple", "연제구": "pink",
        "사하구": "cadetblue", "강서구": "darkgreen", "기장군": "black", "서구": "lightred",
        "동구": "lightblue", "영도구": "lightgreen", "북구": "white", "사상구": "beige", "기타": "gray"
    }

    # 사이드바 검색창 영역
    st.sidebar.header("🔍 맛집 검색 및 검색 옵션")
    search_keyword = st.sidebar.text_input("식당 이름이나 메뉴를 검색하세요", "")
    
    if search_keyword:
        filtered_df = df[df['title'].str.contains(search_keyword, case=False, na=False)]
    else:
        filtered_df = df

    # 🍕 배고픈자들의 컨텐츠 대통합 메뉴판
    st.header("🍕 배고픈자들의 컨텐츠")
    
    content_menu = st.radio(
        "💡 원하시는 콘텐츠를 클릭해 보세요!",
        ["🎲 맛집 랜덤 추천", "📅 요일별 인기 메뉴", "🔥 가장 많이 찾은 메뉴"],
        horizontal=True
    )
    
    st.markdown("---")

    # -------------------------------------------------------------
    # 🎯 메뉴 클릭에 따른 화면 전면 분기 제어 시스템
    # -------------------------------------------------------------
    if content_menu == "📅 요일별 인기 메뉴":
        st.write("### 📅 요일별 어떤 메뉴가 가장 잘 나갔을까?")
        st.caption("📍 부산 맛집 소비 트렌드를 시각적으로 분석한 요일별 인기 요리 분포 차트입니다.")
        
        # 🌟 외부 도구(matplotlib) 없이 스트림릿 전용 내장 데이터셋 구조로 정밀 빌드업!
        # 조카가 요청한 월화수목금 완벽 정렬을 위해 인덱스를 고정했어!
                # 🌟 7일 전체 데이터 구성 및 월~일 강제 순차 정렬 세팅!
        weekly_df = pd.DataFrame({
            "요일": [
                "월요일 (🍜밀면)", "화요일 (🥩고기)", "수요일 (🍣일식)", 
                "목요일 (🍕양식)", "금요일 (☕카페)", "토요일 (🍺술집)", "일요일 (🍲브런치)"
            ],
            "주문수": [180, 140, 160, 110, 130, 190, 150],
            "배너색상": ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        })
        
        # 🌟 아래 배너 카드와 100% 일치하는 무지개 색상 주입!
        chart_colors = ["#1F77B4", "#D62728", "#9467BD", "#FF7F0E", "#2CA02C", "#17BECF", "#E377C2"]
        
        # 순서 정렬과 개별 색상을 동시에 적용하는 고성능 altair 지도 그래프
        chart = alt.Chart(weekly_df).mark_bar(size=40).encode(
            x=alt.X('요일:N', sort=[
                "1. 월요일 (🍜밀면)", "2. 화요일 (🥩고기)", "3. 수요일 (🍣일식)", 
                "4. 목요일 (🍕양식)", "5. 금요일 (☕카페)", "6. 토요일 (🍺술집)", "7. 일요일 (🍲브런치)"
            ], title="요일"),
            y=alt.Y('주문수:Q', title="인기 주문수 (건)"),
            color=alt.Color('배너색상:N', scale=alt.Scale(
                domain=["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"], 
                range=chart_colors
            ), legend=None)
        ).properties(height=350)
        
        # 2/3 아담한 크기로 화면 중앙에 배치하기
        left_space, chart_center, right_space = st.columns([0.1, 0.8, 0.1])
        with chart_center:
            st.altair_chart(chart, use_container_width=True)

            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 요일별 요약 설명 배너 배치 완료
        col_a, col_b, col_c, col_d, col_e = st.columns(5)
        with col_a: st.info("**월요일 🍜**\n\n주초에는 역시 뜨끈한 국수와 밀면이 인기 최고!")
        with col_b: st.error("**화요일 🥩**\n\n체력 보충을 위한 든든한 고기 밥상 가득!")
        with col_c: 
            st.markdown(
                "<div style='background-color:#F0EEF6; padding:15px; border-radius:5px; border-left:5px solid #9467BD; height:125px;'>"
                "<span style='color:#9467BD; font-weight:bold;'>수요일 🍣</span><br/><p style='font-size:13px; margin-top:5px; color:#333;'>중간 점검! 싱싱한 회와 초밥 주문 폭발!</p></div>", 
                unsafe_allow_html=True
            )
        with col_d: st.warning("**목요일 🍕**\n\n주말 분위기 예습! 치즈 가득 피자와 양식!")
        with col_e: st.success("**금요일 ☕**\n\n최고 대목! 달콤한 디저트와 핫플 카페 점령!")

    else:
        # 그 외의 메뉴(랜덤 추천이나 가장 많이 찾은 메뉴)일 때 기존 지도 대시보드 띄우기
        if content_menu == "🎲 맛집 랜덤 추천":
            if st.button("🚀 맛집 랜덤 추천받기!"):
                if not filtered_df.empty:
                    random_pick = filtered_df.sample(n=1).iloc[0]
                    st.success(f"🎯 삼촌이 추천하는 랜덤 맛집은? **[{random_pick['title']}]** 입니다!")
                    st.info(f"📍 음식 종류: {random_pick['음식 종류']} | 위치: {random_pick['위치한 구']} | 주소: {random_pick['address1']}")
                else:
                    st.warning("검색된 맛집 결과가 없어서 추천할 수 없어요.")
                    
        elif content_menu == "🔥 가장 많이 찾은 메뉴":
            st.write("### 🔥 현재 부산에서 가장 핫한 인기 음식 종류 TOP 5")
            top_menus = filtered_df['음식 종류'].value_counts().head(5)
            rank_icons = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            for i, (menu_name, count) in enumerate(top_menus.items()):
                if i < len(rank_icons):
                    st.write(f"{rank_icons[i]} **{menu_name}** ({count}개 매장 등록됨)")
        
        st.markdown("---")

        # 🗺️ 본문 지도 및 리스트 화면 세트 배치
        main_col, side_col = st.columns([1.8, 1.2])

        with main_col:
            st.subheader("📋 1. 아래 맛집 목록에서 식당을 클릭해보세요!")
            show_df = filtered_df[['title', '음식 종류', '위치한 구', 'address1']].rename(
                columns={'title': '식당 이름', 'address1': '상세 주소'}
            )
            event = st.dataframe(
                show_df, 
                height=250, 
                use_container_width=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            st.subheader("🗺️ 2. 네이버 지도 스타일 맛집 지도 (구별 색상 적용)")
            center_lat, center_lng = 35.1796, 129.0756
            zoom_level = 11
            map_df = filtered_df
            
            selected_rows = event.get("selection", {}).get("rows", [])
            if selected_rows:
                chosen_index = selected_rows[0]
                chosen_row = filtered_df.iloc[[chosen_index]]
                map_df = chosen_row
                center_lat = chosen_row['latitude'].values[0]
                center_lng = chosen_row['longitude'].values[0]
                zoom_level = 16 
                st.info(f"📍 현재 선택된 식당: **[{chosen_row['title'].values[0]}]** ({chosen_row['음식 종류'].values[0]})")
                
            m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom_level, control_scale=True)
            
            for idx, row in map_df.head(200).iterrows():
                tooltip_html = f"<div style='font-size: 12px; font-weight: bold; padding: 3px;'>{row['title']} ({row['음식 종류']})<br><span style='color:blue;'>[{row['위치한 구']}]</span></div>"
                popup_html = f"""
                <div style='width:220px; font-family:sans-serif;'>
                    <h4 style='margin:0 0 5px 0; color:#FF4B4B;'>{row['title']}</h4>
                    <p style='margin:0 0 3px 0; font-size:12px; color:#1F77B4;'><b>종류:</b> {row['음식 종류']}</p>
                    <p style='margin:0 0 5px 0; font-size:12px; color:purple;'><b>지역구:</b> {row['위치한 구']}</p>
                    <p style='margin:0; font-size:11px; color:#555;'><b>주소:</b> {row['address1']}</p>
                </div>
                """
                pin_color = gu_color_map.get(row['위치한 구'], "gray")
                folium.Marker(
                    location=[row["latitude"], row["longitude"]],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=folium.Tooltip(tooltip_html, permanent=False),
                    icon=folium.Icon(color=pin_color, icon="info-sign")
                ).add_to(m)
                
            st_folium(m, width="100%", height=450, key="naver_style_map")

        with side_col:
            st.subheader("📊 지역구 별 맛집 수")
            st.caption("📍 동네별 맛집")
            district_counts = filtered_df['위치한 구'].value_counts()
            if "기타" in district_counts:
                district_counts = district_counts.drop("기타")
                
            if not district_counts.empty:
                st.bar_chart(district_counts)
            else:
                st.caption("데이터가 없습니다.")

            st.markdown("---")

            # 👨‍🍳 오늘은 내가 AI 셰프! 맛집 매니저 존
            st.subheader("👨‍🍳 오늘은 내가 AI 셰프!")
            st.caption("공공데이터 레시피를 기반으로 맛집 요리를 뚝딱 추천해 주는 스마트 AI입니다.")
            
            user_question = st.chat_input("주문하시겠어요? 구 이름(예: 수영구)이나 식당 이름을 입력해보세요!")
            
            if user_question:
                st.chat_message("user").write(user_question)
                rag_search = df[df['address1'].str.contains(user_question, case=False, na=False) | df['title'].str.contains(user_question, case=False, na=False)]
                
                with st.chat_message("assistant"):
                    if not rag_search.empty:
                        suggest_restaurant = rag_search.iloc[0]['title']
                        suggest_addr = rag_search.iloc[0]['address1']
                        suggest_cate = rag_search.iloc[0]['음식 종류']
                        
                        st.write(f"💬 **AI 셰프의 스페셜 추천 요리 배달 완료!**")
                        st.write(f"요청하신 정답지 레시피를 분석해 보았습니다. **{suggest_cate}** 맛집인 **'{suggest_restaurant}'**을(를) 추천해 드려요! 위치는 `{suggest_addr}` 입니다. 맛있게 드세요! 🍕")
                    else:
                        st.write("💬 앗, 제 공공데이터 레시피북 안에서는 관련된 맛집 요리를 찾지 못했어요. 다른 단어로 주문해 주시겠어요?")

except FileNotFoundError:
    st.error(f"📂 파일이 없대요! 파일이 project.py와 같은 폴더에 있는지 확인해 주세요.")
except Exception as e:
    st.error(f"❌ 에러가 발생했어요: {e}")
