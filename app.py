import streamlit as st
import pandas as pd
from datetime import date, datetime

st.title("簡易会計アプリ（空行無視・未入力フィードバック版）")

st.write("取引情報を表形式でまとめて入力してください。")

# 取引区分リスト
transaction_types = ["収入", "支出"]

# 科目リスト
subjects = [
    "売上", "仕入", "水道光熱費", "旅費交通費", "通信費",
    "接待交際費", "修繕費", "消耗品費", "支払手数料", "車両費", "リース料"
]

# 初期表示する行数
initial_rows = 10

# 空のDataFrameを作成（取引日は空欄）
default_data = {
    "取引日": [None for _ in range(initial_rows)],
    "区分": ["" for _ in range(initial_rows)],
    "科目": ["" for _ in range(initial_rows)],
    "金額": [0 for _ in range(initial_rows)],
    "摘要": ["" for _ in range(initial_rows)]
}
df = pd.DataFrame(default_data)

# 列ごとの入力仕様を設定
column_config = {
    "取引日": st.column_config.DateColumn(
        label="取引日",
        format="YYYY/MM/DD",
        required=False
    ),
    "区分": st.column_config.SelectboxColumn(
        label="区分",
        options=transaction_types,
        required=False
    ),
    "科目": st.column_config.SelectboxColumn(
        label="科目",
        options=subjects,
        required=False
    ),
    "金額": st.column_config.NumberColumn(
        label="金額（円）",
        min_value=0,
        step=100
    ),
    "摘要": st.column_config.TextColumn(
        label="摘要"
    )
}

# st.data_editorを使って表形式入力
edited_df = st.data_editor(
    df,
    column_config=column_config,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True
)

# 保存ボタン
if st.button("保存する"):
    # まず「少しでも入力されている行」だけを対象にフィルタリング
    inputted_df = edited_df[
        (edited_df["取引日"].notna()) |
        (edited_df["区分"] != "") |
        (edited_df["科目"] != "") |
        (edited_df["金額"] > 0) |
        (edited_df["摘要"] != "")
    ].copy()

    # 入力された行が1件もない場合
    if inputted_df.empty:
        st.warning("保存するデータがありません。")
    else:
        # 上から順に、未入力項目がないかチェック
        for idx, row in inputted_df.iterrows():
            if (
                pd.isna(row["取引日"]) or
                row["区分"] == "" or
                row["科目"] == "" or
                row["金額"] == 0
            ):
                st.warning(f"{idx + 1}行目に入力していない項目があります。")
                break
        else:
            # 全部問題ないときの処理
            inputted_df["記帳日"] = date.today().strftime('%Y/%m/%d')

            # 金額をカンマ区切りで整形
            inputted_df["金額"] = inputted_df["金額"].apply(lambda x: "{:,}".format(int(x)))

            # 列順を指定して並び替え
            cols = ["記帳日", "取引日", "区分", "科目", "金額", "摘要"]
            inputted_df = inputted_df[cols]

            # ファイル名を自動生成
            filename = f"帳簿_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

            # 件数カウント
            entry_count = len(inputted_df)

            # 件数に応じたメッセージとダウンロードボタン表示
            st.success(f"{entry_count}件のデータを保存します。")
            st.download_button(
                label=f"{entry_count}件のデータをダウンロード",
                data=inputted_df.to_csv(index=False, encoding='utf-8-sig'),
                file_name=filename,
                mime='text/csv'
            )