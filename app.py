import streamlit as st
import google.generativeai as genai
import re
import os
import asyncio
import edge_tts
import tempfile
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# --- 1. AIの設定 ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("APIキーが設定されていません。Streamlitの設定を確認してください。")
    st.stop()

# --- 2. 画面の見た目 ---
st.title("自分専用：全自動スライド動画メーカー 🎬")
st.write("テーマを入力するだけで、AIが原稿を考え、音声付きのスライド動画を自動生成します！")

st.sidebar.header("設定")
theme = st.sidebar.text_input("スライドのテーマ", "日本の歴史について")
slide_count = st.sidebar.slider("スライドの枚数", min_value=3, max_value=10, value=5)

# --- 3. 必要な関数（裏側で働く職人たち） ---

# ① AIに原稿を書かせる職人
def generate_script(theme, count):
    model = genai.GenerativeModel('gemini-3-flash-preview')
    prompt = f"""
    あなたはプロのスライド制作者です。以下のテーマで、動画用の構成案を{count}枚分作成してください。
    テーマ: {theme}
    各スライドについて、必ず以下の形式で出力してください：
    [スライド開始]
    タイトル: [スライドの見出し]
    ナレーション: [動画で読み上げる文章]
    [スライド終了]
    """
    response = model.generate_content(prompt)
    return response.text

# ② 原稿を「タイトル」と「ナレーション」に切り分ける職人
def parse_script(text):
    slides = []
    blocks = re.split(r'\[スライド開始\]', text)
    for block in blocks:
        if 'タイトル:' in block and 'ナレーション:' in block:
            title_match = re.search(r'タイトル:\s*(.*)', block)
            narration_match = re.search(r'ナレーション:\s*(.*)', block, re.DOTALL)
            if title_match and narration_match:
                # [スライド終了] などの余分な文字を消す
                narration = narration_match.group(1).split('[スライド終了]')[0].strip()
                slides.append({
                    'title': title_match.group(1).strip(),
                    'narration': narration
                })
    return slides

# ③ テキストから音声（MP3）を作る職人
async def generate_audio(text, output_path):
    # 日本語の女性の声（七海）を使用します
    communicate = edge_tts.Communicate(text, "ja-JP-NanamiNeural")
    await communicate.save(output_path)

# ④ タイトルから画像（背景）を作る職人
def create_image(title, output_path):
    # 暗いグレーの背景画像を作成 (1280x720)
    img = Image.new('RGB', (1280, 720), color=(40, 40, 40))
    draw = ImageDraw.Draw(img)
    # ※一旦デフォルトフォントを使用します。日本語が四角(□)に文字化けする場合は後で直します。
    font = ImageFont.load_default()
    
    # 文字を真ん中あたりに描画（簡易版）
    draw.text((100, 300), title, fill=(255, 255, 255), font=font)
    img.save(output_path)

# --- 4. 実行ボタンが押された時のメイン処理 ---
if st.button("🚀 動画を自動生成する"):
    with st.spinner("Step 1/3: AIが原稿を執筆中..."):
        try:
            script_text = generate_script(theme, slide_count)
            st.success("原稿の執筆が完了しました！")
            with st.expander("📝 生成された原稿を見る"):
                st.text(script_text)
                
            slides = parse_script(script_text)
            
            if not slides:
                st.error("原稿の形式が正しくありませんでした。もう一度お試しください。")
                st.stop()
                
        except Exception as e:
            st.error(f"原稿作成でエラーが発生しました: {e}")
            st.stop()

    with st.spinner("Step 2/3: 音声と画像を生成中..."):
        # 一時保存用のフォルダを作成
        temp_dir = tempfile.mkdtemp()
        clips = []
        
        try:
            for i, slide in enumerate(slides):
                # 1. 音声ファイルの作成
                audio_path = os.path.join(temp_dir, f"audio_{i}.mp3")
                asyncio.run(generate_audio(slide['narration'], audio_path))
                
                # 2. 画像ファイルの作成
                image_path = os.path.join(temp_dir, f"image_{i}.png")
                create_image(slide['title'], image_path)
                
                # 3. 画像と音声を合体させる
                audio_clip = AudioFileClip(audio_path)
                image_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                video_clip = image_clip.set_audio(audio_clip)
                clips.append(video_clip)
                
        except Exception as e:
            st.error(f"音声・画像生成でエラーが発生しました: {e}")
            st.stop()

    with st.spinner("Step 3/3: 動画を一つに結合中...（少し時間がかかります）"):
        try:
            # 全てのスライドを繋げる
            final_video = concatenate_videoclips(clips, method="compose")
            output_video_path = os.path.join(temp_dir, "final_output.mp4")
            
            # 動画ファイルとして出力 (1秒間に24コマ)
            final_video.write_videofile(output_video_path, fps=24, logger=None)
            
            st.success("🎉 動画が完成しました！")
            
            # 画面に完成した動画を表示して再生できるようにする
            with open(output_video_path, 'rb') as video_file:
                video_bytes = video_file.read()
                st.video(video_bytes)
                
        except Exception as e:
            st.error(f"動画の結合でエラーが発生しました: {e}")
