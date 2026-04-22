import streamlit as st

# アプリのタイトル
st.title("自分専用：全自動スライド動画メーカー 🎬")
st.write("テーマを入力するだけで、AIが原稿を考え、音声付きのスライド動画を自動生成します。")

# ユーザーからの入力エリア
st.sidebar.header("設定")
theme = st.sidebar.text_input("スライドのテーマ", "例：日本の歴史について")
slide_count = st.sidebar.slider("スライドの枚数", min_value=3, max_value=10, value=5)

# メイン画面の表示
st.subheader(f"テーマ：『{theme}』")
st.write(f"このテーマで、全{slide_count}枚のスライド動画を作成します。")

# 実行ボタン
if st.button("動画を生成する（テスト）"):
    st.info("今はまだテスト段階です。ここに「AI原稿作成」と「動画合成」の機能を追加していきます！")
