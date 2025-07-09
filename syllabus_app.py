import streamlit as st
import pandas as pd
import re

def create_html_content(df_to_render):
    """
    データフレームを受け取り、整形されたHTML文字列を生成する関数
    """
    all_syllabi_parts = []
    for index, row in df_to_render.iterrows():
        # データ抽出
        kamoku_mei = str(row.get('授業科目', '')).replace('～', '-')
        if not kamoku_mei: continue
        
        kamoku_numbering = row.get('科目ナンバリング', '')
        tanin_kyoin = row.get('担当教員', '')
        kaiko_nendo = f"{row.get('年度', '')}年度"
        kaiko_ki = row.get('開講期', '')
        kaiko_nenji = row.get('開講年次', '')
        tani = str(row.get('単位', '')).replace('.00', '') + "単位"
        jugyo_keitai = row.get('授業形態', '')
        theme_goal = str(row.get('テーマ(ねらい)及び到達目標', '')).replace('<br>', '<br/>')
        gaiyo = str(row.get('授業概要', '')).replace('<br>', '<br/>')
        dp_info = str(row.get('DPとの対応', '')).replace('<br>', '<br/>')
        sonota_info = str(row.get('その他', '')).replace('<br>', '<br/>')

        # 授業計画の整形
        keikaku_list_items = ""
        for i in range(1, 16):
            col_name = f'授業計画(15回)（第{i}回）'
            plan = str(row.get(col_name, ''))
            if plan:
                plan_clean = re.sub('<[^<]+?>', '', plan).strip()
                keikaku_list_items += f"<li><strong>第{i}回</strong>: {plan_clean}</li>"

        # 成績評価の整形
        hyoka_hoho = str(row.get('評価方法', '')).replace('<br>', '<br/>')
        saishiken = row.get('再試験有無', '')
        shiken_jisshi = row.get('試験実施について', '')

        # 教科書・参考書の整形
        textbooks_list_items = ""
        for i in range(1, 7):
            if row.get(f'教科書（書籍名{i}）'):
                book_name = row.get(f'教科書（書籍名{i}）', '')
                author = row.get(f'教科書（著者{i}）', '')
                textbooks_list_items += f"<li>{book_name} ({author})</li>"
        if not textbooks_list_items: textbooks_list_items = "<li>指定なし</li>"

        references_list_items = ""
        for i in range(1, 11):
            if row.get(f'参考書（書籍名{i}）'):
                book_name = row.get(f'参考書（書籍名{i}）', '')
                references_list_items += f"<li>{book_name}</li>"
        if not references_list_items: references_list_items = "<li>特になし</li>"

        # 1科目分のHTMLパーツを生成
        syllabus_part = f"""
        <div class="container">
            <h1>{kamoku_mei}</h1>
            <div class="section-box"><h2>科目基本情報</h2><ul>
                <li><strong>科目ナンバリング</strong>: {kamoku_numbering}</li><li><strong>担当教員</strong>: {tanin_kyoin}</li>
                <li><strong>開講年度・学期</strong>: {kaiko_nendo} {kaiko_ki}</li><li><strong>開講年次</strong>: {kaiko_nenji}</li>
                <li><strong>単位数</strong>: {tani}</li><li><strong>授業形態</strong>: {jugyo_keitai}</li>
            </ul></div>
            <div class="section-box"><h2>科目概要</h2>
                <p><strong>テーマ（ねらい）及び到達目標</strong>:<br/>{theme_goal}</p>
                <p><strong>授業概要</strong>:<br/>{gaiyo}</p>
                <p><strong>DPとの対応</strong>:<br/>{dp_info}</p>
            </div>
            <div class="section-box"><h2>授業計画</h2><ul>{keikaku_list_items}</ul></div>
            <div class="section-box"><h2>成績評価</h2><p>{hyoka_hoho}</p><ul><li><strong>試験</strong>: {shiken_jisshi}</li><li><strong>再試験</strong>: {saishiken}</li></ul></div>
            <div class="section-box"><h2>その他</h2><p>{sonota_info}</p></div>
            <div class="section-box"><h2>教科書・参考書</h2><p><strong>教科書</strong>:</p><ul>{textbooks_list_items}</ul><p><strong>参考書</strong>:</p><ul>{references_list_items}</ul></div>
        </div>
        """
        all_syllabi_parts.append(syllabus_part)
    
    st_style = """
    <style>
        body { background-color: #f0f2f6; font-family: 'Meiryo', 'メイリオ', sans-serif; }
        .container { background-color: #fff; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: auto; max-width: 800px; padding: 20px 40px;}
        h1 { color: #1a73e8; border-bottom: 2px solid #1a73e8; text-align: center; font-size: 1.8em; padding-bottom: 10px; }
        h2 { color: #3c4043; border-bottom: 1px solid #dfe1e5; font-size: 1.3em; padding-bottom: 5px; margin-top: 30px;}
        ul { list-style: none; padding-left: 0; }
        li { margin-bottom: 8px; }
        p { margin-left: 5px; }
        strong { font-weight: bold; }
        @media print {
            body { background-color: #fff; }
            .container { page-break-after: always; box-shadow: none; border: 1px solid #ccc; }
        }
    </style>
    """
    html_header = f'<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><title>全科目シラバス一覧</title>{st_style}</head><body>'
    html_footer = "</body></html>"
    return html_header + "".join(all_syllabi_parts) + html_footer

# --- ここからメインのアプリ処理 ---
st.set_page_config(page_title="シラバス整形・検索アプリ", page_icon="🗂️", layout="wide")

st.sidebar.title("🗂️ 操作パネル")
uploaded_file = st.sidebar.file_uploader("1. CSVファイルをアップロード", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='cp932')
        df.fillna('', inplace=True)
        df['sort_year'] = df['授業科目'].str.extract(r'(\d)').astype(float)
        
        with st.sidebar.expander("2. 絞り込み", expanded=True):
            bracket_contents = df['授業科目'].str.extract(r'【(.*?)】')[0]
            unique_options = sorted([opt for opt in bracket_contents.dropna().unique() if opt])
            selected_options = st.multiselect('対象を選択', unique_options, default=unique_options)
            
            # ▼▼▼ 複数キーワードに対応するためのUI修正 ▼▼▼
            keyword_input = st.text_input("キーワード（スペースで区切って複数指定可）")
        
        with st.sidebar.expander("3. 並び替え", expanded=True):
            sort_option = st.radio("学年で並び替え", ('並び替えなし', '学年で昇順', '学年で降順'))

        st.title("📚 シラバス整形・検索結果")
        st.write("左のパネルで絞り込みや並び替えができます。")
        
        # フィルタリングと並び替え
        df_filtered = df.copy()
        if selected_options:
            escaped_options = [re.escape(opt) for opt in selected_options]
            df_filtered = df_filtered[df_filtered['授業科目'].str.contains('|'.join(escaped_options), na=False)]
        
        # ▼▼▼ 複数キーワード（AND検索）に対応するよう修正 ▼▼▼
        if keyword_input:
            keywords = keyword_input.split() # スペースで区切ってリスト化
            search_columns = ['授業科目', '担当教員', '授業概要', 'テーマ(ねらい)及び到達目標', 'その他']
            
            for keyword in keywords:
                # 各キーワードで順番に絞り込んでいく
                mask = df_filtered[search_columns].apply(
                    lambda col: col.str.contains(keyword, case=False, na=False)
                ).any(axis=1)
                df_filtered = df_filtered[mask]

        if sort_option == '学年で昇順':
            df_filtered = df_filtered.sort_values(by='sort_year', ascending=True)
        elif sort_option == '学年で降順':
            df_filtered = df_filtered.sort_values(by='sort_year', ascending=False)
        
        st.markdown("---")
        st.subheader(f"4. 結果の選択（{len(df_filtered)}件ヒット）")
        
        if 'select_all' not in st.session_state:
            st.session_state.select_all = True
        if 'last_uploaded_file' not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
            st.session_state.select_all = True
            st.session_state.last_uploaded_file = uploaded_file.name

        col1, col2, _, _ = st.columns(4)
        if col1.button("✅ すべて選択"):
            st.session_state.select_all = True
        if col2.button("✖️ すべてクリア"):
            st.session_state.select_all = False

        st.write("出力したい科目にチェックを入れてください。")

        selected_rows_indices = []
        if not df_filtered.empty:
            for index, row in df_filtered.iterrows():
                if st.checkbox(row['授業科目'], value=st.session_state.select_all, key=f"check_{index}"):
                    selected_rows_indices.append(index)
            
            df_final = df.loc[selected_rows_indices]

            if not df_final.empty:
                final_html = create_html_content(df_final)
                st.markdown("---")
                st.download_button(
                    label=f"📄 選択した{len(df_final)}件のHTMLをダウンロード",
                    data=final_html,
                    file_name="選択後シラバス_印刷対応版.html",
                    mime="text/html"
                )
            else:
                st.warning("出力対象の科目が選択されていません。")
        else:
            st.warning("条件に一致する科目がありません。")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.error("文字コードが'cp932'ではない可能性があります。またはCSVの列名が想定と違うようです。")
else:
    st.info("←サイドバーからCSVファイルをアップロードすると、処理が始まります。")