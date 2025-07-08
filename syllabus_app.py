import streamlit as st
import pandas as pd
import os
import re

# --- アプリの基本的なUIを設定 ---
st.set_page_config(page_title="シラバス整形アプリ", layout="wide")
st.title("📝 シラバス整形アプリ")
st.write("大学のシラバス情報が入ったCSVファイルをアップロードすると、整形されたHTMLファイル（統合版）をダウンロードできます。")

# --- ファイルアップロード機能 ---
uploaded_file = st.file_uploader("ここにシラバスのCSVファイルをドラッグ＆ドロップしてください", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='cp932')
        st.success("CSVファイルの読み込みに成功しました！")
        df.fillna('', inplace=True)
        
        # --- 並び替えと絞り込み用の学年データを抽出 ---
        df['year_num'] = df['授業科目'].str.extract(r'(\d)').astype(float)


        # --- 絞り込みと並び替えのUI ---
        st.subheader("絞り込みと並び替え")
        
        # --- ▼▼▼ 新機能: 学年選択チェックボックスを追加 ▼▼▼ ---
        col1, col2 = st.columns(2) # 画面を2つの列に分割

        with col1: # 左側の列に学科選択を配置
            department_options = ['N', 'S', 'E', 'B']
            selected_departments = st.multiselect(
                '学科を選択してください（複数選択可）',
                department_options,
                default=department_options
            )

        with col2: # 右側の列に学年選択を配置
            year_options = [1, 2, 3, 4]
            selected_years = st.multiselect(
                '学年を選択してください（複数選択可）',
                year_options,
                default=year_options
            )
        
        sort_option = st.radio(
            "並び替え方法を選択:",
            ('並び替えなし', '学年で昇順', '学年で降順'),
            horizontal=True
        )

        # --- フィルタリング処理 ---
        # まず学科で絞り込み
        if selected_departments:
            df_filtered = df[df['授業科目'].str.contains('|'.join(selected_departments), na=False)]
        else:
            df_filtered = df.copy() # 何も選択されなければ全学科を対象

        # 次に学年で絞り込み
        if selected_years:
            df_filtered = df_filtered[df_filtered['year_num'].isin(selected_years)]
        
        
        # --- 並び替え処理 ---
        if not df_filtered.empty:
            if sort_option == '学年で昇順':
                df_filtered = df_filtered.sort_values(by='year_num', ascending=True)
            elif sort_option == '学年で降順':
                df_filtered = df_filtered.sort_values(by='year_num', ascending=False)
            
            st.info(f"{len(df_filtered)}件の科目を処理します。")
        else:
             st.warning("条件に一致する科目がありません。")


        # --- HTML生成処理 ---
        if not df_filtered.empty:
            all_syllabi_parts = []
            for index, row in df_filtered.iterrows():
                # (以降のデータ抽出、HTML生成ロジックは前回と全く同じです)
                kamoku_mei = row.get('授業科目', '')
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

                syllabus_part = f"""
            <div class="container">
                <h1>{kamoku_mei}</h1>
                <div class="section-box">
                    <h2>科目基本情報</h2>
                    <ul>
                        <li><strong>科目ナンバリング</strong>: {kamoku_numbering}</li>
                        <li><strong>担当教員</strong>: {tanin_kyoin}</li>
                        <li><strong>開講年度・学期</strong>: {kaiko_nendo} {kaiko_ki}</li>
                        <li><strong>開講年次</strong>: {kaiko_nenji}</li>
                        <li><strong>単位数</strong>: {tani}</li>
                        <li><strong>授業形態</strong>: {jugyo_keitai}</li>
                    </ul>
                </div>
                <div class="section-box">
                    <h2>科目概要</h2>
                    <p><strong>テーマ（ねらい）及び到達目標</strong>:<br/>{theme_goal}</p>
                    <p><strong>授業概要</strong>:<br/>{gaiyo}</p>
                </div>
                <div class="section-box">
                    <h2>授業計画</h2>
                    <ul>{keikaku_list_items}</ul>
                </div>
                <div class="section-box">
                    <h2>成績評価</h2>
                    <p>{hyoka_hoho}</p>
                    <ul>
                        <li><strong>試験</strong>: {shiken_jisshi}</li>
                        <li><strong>再試験</strong>: {saishiken}</li>
                    </ul>
                </div>
                <div class="section-box">
                    <h2>教科書・参考書</h2>
                    <p><strong>教科書</strong>:</p>
                    <ul>{textbooks_list_items}</ul>
                    <p><strong>参考書</strong>:</p>
                    <ul>{references_list_items}</ul>
                </div>
            </div>
            <hr style="border: 1px dashed #ccc; margin: 40px 0;">
        """
                all_syllabi_parts.append(syllabus_part)

            html_header = """
        <!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><title>全科目シラバス一覧</title><style>body { font-family: 'Meiryo', sans-serif; line-height: 1.6; margin: 40px; background-color: #f4f4f4; } .container { max-width: 800px; margin: auto; border: 1px solid #ccc; padding: 20px 40px; background-color: #fff; box-shadow: 0 0 10px rgba(0,0,0,0.05); } h1 { text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; } h2 { border-bottom: 1px solid #ddd; padding-bottom: 5px; } ul { list-style: none; padding-left: 0; } li { margin-bottom: 8px; } strong { font-weight: bold; } .section-box { margin-bottom: 30px; }</style></head><body>
        """
            html_footer = "</body></html>"
            final_html = html_header + "".join(all_syllabi_parts) + html_footer
            
            st.download_button(
                label="絞り込み・並び替え結果のHTMLをダウンロード",
                data=final_html,
                file_name="処理後シラバス_統合版.html",
                mime="text/html"
            )

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.error("文字コードが'cp932'ではない可能性があります。またはCSVの列名が想定と違うようです。")