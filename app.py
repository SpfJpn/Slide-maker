import streamlit as st
import google.generativeai as genai

# --- 1. AIの設定（Secretsに保存したキーを呼び出す） ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("APIキーが設定されていません。StreamlitのSecretsの設定を確認してください。")
    st.stop()

# --- 2. 画面の見た目 ---
st.title("自分専用：全自動スライド動画メーカー 🎬")
st.write("AIがテーマに沿った構成案とナレーションを自動で作成します。")

st.sidebar.header("設定")
theme = st.sidebar.text_input("スライドのテーマ", "日本の歴史について")
slide_count = st.sidebar.slider("スライドの枚数", min_value=3, max_value=10, value=5)

# --- 3. AIに原稿を書かせる命令（関数） ---
def generate_script(theme, count):
    # ご確認いただいた通り、最新主流の Gemini 3 Flash に変更しました！
    # （もしエラーが出る場合は 'gemini-3-flash-preview' に変更してください）
    model = genai.GenerativeModel('gemini-3-flash')
    
    prompt = f"""
    あなたはプロのスライド制作者です。
    以下のテーマで、動画用のスライド構成案を{count}枚分作成してください。
    
    テーマ: {theme}
    
    各スライドについて、以下の形式で出力してください：
    スライド[番号]
    タイトル: [スライドの見出し]
    ナレーション: [動画で読み上げる100文字程度の文章]
    ---
    """
    
    response = model.generate_content(prompt)
    return response.text

# --- 4. 実行ボタンが押された時の処理 ---
if st.button("AIに原稿を作らせる"):
    with st.spinner("AIが思考中... しばらくお待ちください"):
        try:
            # AIに原稿を生成してもらう
            script = generate_script(theme, slide_count)
            
            st.success("原稿が完成しました！")
            
            # 生成された内容を画面に表示する
            st.subheader("生成された構成案")
            st.text_area("編集も可能です", value=script, height=400)
            
            # 後のステップ（動画化）のために保存しておく
            st.session_state["script"] = script
            
        except Exception as e:
            st.error(f"AIの呼び出しに失敗しました。エラー内容: {e}")

st.info("原稿ができたら、次はこれに『音声』と『画像』を自動でつけていきます。")
