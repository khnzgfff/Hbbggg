import os
import sys
import json
import random
import subprocess
import requests
from datetime import datetime
from gtts import gTTS
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ==================== الإعدادات ====================
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "your_key_here")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
OUTPUT_DIR = "output"
VOICE_DIR = "voice"
VIDEO_DIR = "videos"
FINAL_DIR = "final"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)

# ==================== المشاهد والقوالب ====================
SPORTS_TEMPLATES = [
    "هدف_عالمي_في_دوري_ابطال_اوروبا",
    "لقطة_مهارية_كرة_قدم",
    "هدف_في_الدوري_المصري",
    "لقطة_مضحكة_في_الملعب",
    "تحدي_كرة_الشوارع",
    "هدف_خيالي_في_التمرة_الأخيرة",
    "لقطة_محمد_صلاح_مع_ليفربول",
    "مشهد_كرتوني_كرة_القدم",
    "تعليق_رياضي_ساخن",
    "إفيه_على_حارس_المرمى"
]

EGYPTIAN_CATCHPHRASES = [
    "يا جدعان ده مش طبيعي",
    "إيه الجمال ده يا فنان",
    "والله العظيم ما حد يصدق",
    "ده اللي محتاجينه والله",
    "يلا بينا يا أسطى",
    "ده إنت اللي بتعمل كده يا معلم",
    "مش معقول والله العظيم",
    "إنت فاكر نفسك في ملعب الهوكي",
    "العبها صح يا عم",
    "والنبي ده على كيفك"
]

SPORTS_KEYWORDS = [
    "هدف عالمي", "مهارات كرة قدم", "لقطة رياضية",
    "هدف في الدقيقة 90", "محمد صلاح", "الأهلي والزمالك",
    "دوري أبطال أوروبا", "كرة الشوارع", "تحدي المهارات",
    "تعليق رياضي مصري", "إفيهات كرة قدم", "كومنتات رياضية"
]

# ==================== الدوال الأساسية ====================
def generate_egyptian_script_with_deepseek(topic):
    """توليد نص مصري ساخن باستخدام DeepSeek"""
    if DEEPSEEK_API_KEY == "your_key_here":
        return generate_fallback_script(topic)
    
    prompt = f"""أنت كاتب محتوى مصري محترف. اكتب لي تعليقًا صوتيًا مدته 30 ثانية 
    عن {topic}. استخدم العامية المصرية الشعبية والإفيهات.
    اجعل النص حماسيًا ومضحكًا ويحافظ على المشاهد. 
    ابدأ بـ "يلا بينا" أو "يا جدعان".
    النص يجب أن يكون جاهزًا للتسجيل الصوتي مباشرة.
    لا تضع أي علامات أو رموز، فقط النص العربي الصافي."""
    
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.9,
                "max_tokens": 200
            },
            timeout=30
        )
        script = response.json()["choices"][0]["message"]["content"].strip()
        return script
    except Exception as e:
        print(f"DeepSeek error: {e}")
        return generate_fallback_script(topic)

def generate_fallback_script(topic):
    """نص احتياطي في حالة عدم توفر DeepSeek"""
    templates = [
        f"يا جدعان شوفوا الجمال ده! {topic} والله العظيم مش طبيعي. ده اللي كنا منتظرينه من زمان. إنتوا متخيلين اللي حصل ده؟ يلا بينا نشوف التفاصيل!",
        f"إيه الحلاوة دي يا فنان! {topic} ده مش أي كلام والله. العبها صح يا عم. ده الفن والله، ده الإبداع المصري اللي محدش يعرف يعمله غيرنا!",
        f"والنبي ده {topic} على كيفك! يخرب عقلي والله. ده إنت اللي بتعمل كده يا معلم؟ شوفوا يا عالم، شوفوا إحنا بنعمل إيه!"
    ]
    return random.choice(templates)

def generate_voiceover(text, filename="voiceover.mp3"):
    """توليد الصوت من النص باستخدام gTTS"""
    voice_path = os.path.join(VOICE_DIR, filename)
    tts = gTTS(text=text, lang='ar', slow=False)
    tts.save(voice_path)
    return voice_path

def create_text_overlay(text, size=(1080, 300), font_size=60):
    """إنشاء نص مصري احترافي على خلفية شفافة"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # إضافة ظل للنص
    bbox = d.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
    d.text((position[0]+2, position[1]+2), text, font=font, fill=(0, 0, 0, 200))
    d.text(position, text, font=font, fill=(255, 215, 0, 255))
    
    return np.array(img)

def generate_sports_visuals(duration=30):
    """إنشاء فيديو رياضي جذاب"""
    clips = []
    colors = [(34, 139, 34), (0, 0, 139), (139, 0, 0), (255, 140, 0), (0, 100, 0)]
    
    for i in range(duration):
        img = Image.new('RGB', (1080, 1920), colors[i % len(colors)])
        d = ImageDraw.Draw(img)
        
        # رسم ملعب كرة قدم مبسط
        d.ellipse([440, 860, 640, 1060], outline=(255, 255, 255), width=3)
        d.line([540, 500, 540, 1420], fill=(255, 255, 255), width=2)
        d.rectangle([100, 400, 980, 1520], outline=(255, 255, 255), width=2)
        
        # إضافة حركة الكرة
        ball_x = 540 + int(200 * np.sin(i * 0.5))
        ball_y = 960 + int(100 * np.cos(i * 0.7))
        d.ellipse([ball_x-15, ball_y-15, ball_x+15, ball_y+15], 
                  fill=(255, 255, 255), outline=(0, 0, 0))
        
        # إضافة لاعبين مبسطين
        d.ellipse([ball_x-100, ball_y-50, ball_x-60, ball_y-10], 
                  fill=(255, 0, 0))
        d.ellipse([ball_x+60, ball_y+50, ball_x+100, ball_y+90], 
                  fill=(0, 0, 255))
        
        # نص متحرك
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()
        d.text((50, 50), "⚽ كرة قدم مصرية ⚽", font=font, fill=(255, 215, 0))
        
        clip = ImageClip(np.array(img)).set_duration(1.0)
        clips.append(clip)
    
    return concatenate_videoclips(clips, method="compose")

def create_final_video(voice_path, script):
    """تركيب الفيديو النهائي مع الصوت والنصوص"""
    bg_video = generate_sports_visuals(duration=30)
    
    audio = AudioFileClip(voice_path)
    bg_video = bg_video.set_audio(audio)
    
    # إضافة النص كصورة متحركة
    text_img = create_text_overlay(script[:100], size=(1080, 400), font_size=50)
    text_clip = ImageClip(text_img).set_duration(30).set_position(('center', 1400))
    
    final = CompositeVideoClip([bg_video, text_clip])
    
    output_path = os.path.join(FINAL_DIR, "final_video.mp4")
    final.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        threads=4,
        preset='ultrafast'
    )
    
    audio.close()
    final.close()
    return output_path

# ==================== التنفيذ الرئيسي ====================
if __name__ == "__main__":
    print("🏃 بدء توليد المحتوى الرياضي المصري...")
    
    # 1. اختيار موضوع عشوائي أو من ملف
    topic_file = "topic.txt"
    if os.path.exists(topic_file):
        with open(topic_file, 'r', encoding='utf-8') as f:
            topic = f.read().strip()
    else:
        topic = f"{random.choice(SPORTS_KEYWORDS)} {random.choice(EGYPTIAN_CATCHPHRASES)}"
    
    print(f"📝 الموضوع: {topic}")
    
    # 2. توليد السيناريو
    print("🧠 توليد السيناريو المصري...")
    script = generate_egyptian_script_with_deepseek(topic)
    print(f"📜 السيناريو: {script}")
    
    # 3. حفظ النص
    script_file = os.path.join(OUTPUT_DIR, "script.txt")
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script)
    
    # 4. توليد الصوت
    print("🔊 توليد الصوت...")
    voice_path = generate_voiceover(script)
    print(f"✅ الصوت جاهز: {voice_path}")
    
    # 5. إنشاء الفيديو
    print("🎬 تركيب الفيديو النهائي...")
    final_path = create_final_video(voice_path, script)
    
    print("=" * 50)
    print(f"🎉 الفيديو جاهز: {final_path}")
    print("=" * 50)
