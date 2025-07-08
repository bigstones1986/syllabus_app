import streamlit as st
import pandas as pd
import re

# --- アプリの基本的なUIを設定 ---
st.set_page_config(page_title="シラバス整形・検索アプリ", page_icon="✅", layout="wide")

with st.container():
    st.title("✅ シラバス整形・検索アプリ")
    st.write("CSVファイルをアップロードし、条件で絞り込んだ結果から、さらに必要な科目だけを選んでHTMLとして出力します。")

# --- HTML生成ロジックを関数として定義 ---
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
        
        keikaku_list_items = ""
        for i in range(1, 16):
            col_name = f'授業計画(15回)（第{i}回）'
            plan = str(row.get(col_name, ''))
            if plan:
                plan_clean = re.sub('<[^<]+?>', '', plan).strip()
                keikaku_list_items += f"<li><strong>第{i}回</strong>: {plan_clean}</li>"

        hyoka_hoho = str(row.get('評価方法', '')).replace('<br>', '<br/>')
        saishiken = row.get('再試験有無', '')
        shiken_jisshi = row.get('試験実施について', '')

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

        # 1科目分のHTMLパーツ
        syllabus_part = f"""
        <div class="container">
            <h1>{kamoku_mei}</h1>
            <div class="section-box"><h2>科目基本情報</h2><ul>
                <li><strong>科目ナンバリング</strong>: {kamoku_numbering}</li><li><strong>担当教員</strong>: {tanin_kyoin}</li>
                <li><strong>開講年度・学期</strong>: {kaiko_nendo} {kaiko_ki}</li><li><strong>開講年次</strong>: {kaiko_nenji}</li>
                <li><strong>単位数</strong>: {tani}</li><li><strong>授業形態</strong>: {jugyo_keitai}</li>
            </ul></div>
            <div class="section-box"><h2>科目概要</h2><p><strong>テーマ（ねらい）及び到達目標</strong>:<br/>{theme_goal}</p><p><strong>授業概要</strong>:<br/>{gaiyo}</p></div>
            <div class="section-box"><h2>授業計画</h2><ul>{keikaku_list_items}</ul></div>
            <div class="section-box"><h2>成績評価</h2><p>{hyoka_hoho}</p><ul><li><strong>試験</strong>: {shiken_jisshi}</li><li><strong>再試験</strong>: {saishiken}</li></ul></div>
            <div class="section-box"><h2>教科書・参考書</h2><p><strong>教科書</strong>:</p><ul>{textbooks_list_items}</ul><p><strong>参考書</strong>:</p><ul>{references_list_items}</ul></div>
        </div><hr style="border: none; margin: 40px 0;">"""
        all_syllabi_parts.append(syllabus_part)
    
    # HTML全体の骨組み
    st_style = "<style>body{background-color:#f0f2f6}.container{background-color:#fff;border-radius:15px;box-shadow:0 4px 12px rgba(0,0,0,.1);margin:auto;max-width:800px;padding:20px 40px;transition:transform .2s}.container:hover{transform:translateY(-5px)}h1{color:#1a73e8;border-bottom:2px solid #1a73e8;text-align:center}h2{color:#3c4043;border-bottom:1px solid #dfe1e5}ul{list-style:none;padding-left:0}li{margin-bottom:8px}</style>"
    html_header = f'<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><title>全科目シラバス一覧</title>{st_style}</head><body>'
    html_footer = "</body></html>"
    
    return html_header + "".join(all_syllabi_parts) + html_footer

# --- メインの処理 ---
uploaded_file = st.file_uploader("ここにシラバスのCSVファイルをドラッグ＆ドロップしてください", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='cp932')
        st.success("CSVファイルの読み込みに成功しました！")
        df.fillna('', inplace=True)
        df['sort_year'] = df['授業科目'].str.extract(r'(\d)').astype(float)

        st.markdown("---")
        st.subheader("1. 絞り込みと並び替え")
        
        # 絞り込み条件
        bracket_contents = df['授業科目'].str.extract(r'【(.*?)】')[0]
        unique_options = sorted([opt for opt in bracket_contents.dropna().unique() if opt])
        selected_options = st.multiselect('対象で絞り込み', unique_options, default=unique_options)
        keyword = st.text_input("キーワードでさらに絞り込み")
        
        # 並び替え条件
        sort_option = st.radio("学年で並び替え", ('並び替えなし', '学年で昇順', '学年で降順'), horizontal=True)

        # フィルタリング実行
        df_filtered = df.copy()
        if selected_options:
            escaped_options = [re.escape(opt) for opt in selected_options]
            df_filtered = df_filtered[df_filtered['授業科目'].str.contains('|'.join(escaped_options), na=False)]
        if keyword:
            search_columns = ['授業科目', '担当教員', '授業概要', 'テーマ(ねらい)及び到達目標']
            mask = df_filtered[search_columns].apply(lambda col: col.str.contains(keyword, case=False, na=False)).any(axis=1)
            df_filtered = df_filtered[mask]
        
        # 並び替え実行
        if sort_option == '学年で昇順':
            df_filtered = df_filtered.sort_values(by='sort_year', ascending=True)
        elif sort_option == '学年で降順':
            df_filtered = df_filtered.sort_values(by='sort_year', ascending=False)
        
        # --- ▼▼▼ 新機能: 絞り込み結果を可視化し、最終選択 ▼▼▼ ---
        st.markdown("---")
        st.subheader(f"2. 結果の選択（{len(df_filtered)}件ヒット）")
        st.write("HTMLとして出力したい科目にチェックを入れてください。")

        selected_rows_indices = []
        if not df_filtered.empty:
            for index, row in df_filtered.iterrows():
                if st.checkbox(row['授業科目'], value=True, key=f"check_{index}"):
                    selected_rows_indices.append(index)
            
            # 選択された行だけを最終的なデータフレームにする
            df_final = df.loc[selected_rows_indices]

            if not df_final.empty:
                # 選択されたデータでHTMLを生成
                final_html = create_html_content(df_final)
                
                # ダウンロードボタン
                st.markdown("---")
                st.download_button(
                    label=f"✅ 選択した{len(df_final)}件のHTMLをダウンロード",
                    data=final_html,
                    file_name="選択後シラバス_統合版.html",
                    mime="text/html"
                )
            else:
                st.warning("出力対象の科目が選択されていません。")
        else:
            st.warning("条件に一致する科目がありません。")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.error("文字コードが'cp932'ではない可能性があります。またはCSVの列名が想定と違うようです。")