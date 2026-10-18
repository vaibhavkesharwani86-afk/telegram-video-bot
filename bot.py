import os
import cv2
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import yt_dlp

TOKEN = "8298900825:AAHkeT6hHFwjMvD_147nTG0cl--mAXfq4ds"

def download_youtube_short(url):
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': 'downloaded_video.mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 'downloaded_video.mp4'

def remove_captions(input_video_path, output_video_path):
    cap = cv2.VideoCapture(input_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        start_y = int(height * 0.75)
        mask[start_y:height, 0:width] = 255
        
        cleaned_frame = cv2.inpaint(frame, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
        out.write(cleaned_frame)
        
    cap.release()
    out.release()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ कृपया कोई वैध YouTube शॉर्ट लिंक भेजें।")
        return

    await update.message.reply_text("⏳ वीडियो डाउनलोड हो रही है...")
    
    try:
        video_path = download_youtube_short(url)
        await update.message.reply_text("⚙️ कैप्शन्स हटाए जा रहे हैं...")
        
        output_path = "clean_video.mp4"
        remove_captions(video_path, output_path)
        
        await update.message.reply_text("📤 भेजी जा रही है...")
        
        with open(output_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption="✨ लीजिए आपकी कैप्शन-फ्री वीडियो तैयार है!")
            
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(output_path): os.remove(output_path)
        
    except Exception as e:
        await update.message.reply_text(f"❌ कुछ गड़बड़ हो गई: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🤖 बॉट क्लाउड पर लाइव हो गया है...")
    app.run_polling()
  
