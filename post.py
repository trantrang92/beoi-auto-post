import os
import time
import random
import requests
from datetime import datetime

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
FB_PAGE_ID = os.environ.get('FB_PAGE_ID')
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"

PHOTO_KEYWORDS = [
    "baby mother", "newborn baby", "mom baby smile",
    "baby care", "mother child love", "baby playing",
    "happy baby", "cute baby", "baby sleeping", "family baby"
]

def get_photo_url():
    try:
        keyword = random.choice(PHOTO_KEYWORDS).replace(" ", "+")
        # Unsplash source - không cần API key
        url = f"https://source.unsplash.com/800x600/?{keyword}"
        res = requests.get(url, timeout=15, allow_redirects=True)
        if res.status_code == 200 and 'image' in res.headers.get('Content-Type', ''):
            return res.url
        print("Không lấy được ảnh từ Unsplash")
    except Exception as e:
        print(f"Lỗi lấy ảnh: {e}")
    return None

def generate_content():
    topic = "buổi tối - thư giãn và gắn kết gia đình với bé"

    prompt = f"""Bạn là chuyên gia tư vấn nuôi dạy con của app Bé Ơi.
Viết 1 bài đăng Facebook về chủ đề: {topic}
Yêu cầu:
- Thân thiện, ấm áp với các mẹ Việt Nam
- Có emoji phù hợp
- 150-250 từ
- Cuối bài nhắc tải app Bé Ơi
- Hashtag: #BéƠi #ChămsócBé #MẹVàBé
Chỉ trả về nội dung bài viết."""

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for attempt in range(5):
        try:
            print(f"Lần {attempt+1}/5...")
            res = requests.post(GEMINI_URL, json=payload, timeout=30)
            data = res.json()
            if "candidates" in data:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            print(f"Lỗi Gemini: {data.get('error', {}).get('message', data)}")
        except Exception as e:
            print(f"Lỗi request: {e}")
        if attempt < 4:
            time.sleep(15)

    raise Exception("Gemini thất bại sau 5 lần thử")

def post_to_facebook(content, photo_url=None):
    if photo_url:
        # Upload ảnh trực tiếp lên Facebook
        img_data = requests.get(photo_url, timeout=15).content
        upload_url = f"https://graph.facebook.com/v26.0/{FB_PAGE_ID}/photos"
        response = requests.post(upload_url, data={
            "caption": content,
            "access_token": FB_PAGE_TOKEN,
            "published": "true"
        }, files={"source": ("photo.jpg", img_data, "image/jpeg")}, timeout=60)
    else:
        url = f"https://graph.facebook.com/v26.0/{FB_PAGE_ID}/feed"
        response = requests.post(url, data={
            "message": content,
            "access_token": FB_PAGE_TOKEN,
            "published": "true"
        }, timeout=30)

    result = response.json()
    if "id" in result:
        print(f"✅ Đăng thành công! Post ID: {result['id']}")
    else:
        raise Exception(f"❌ Facebook API Error: {result}")

def main():
    print(f"🚀 Bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Đang tạo nội dung với Gemini AI...")
    content = generate_content()
    print(f"Nội dung:\n{content}\n")
    print("🖼️ Đang lấy ảnh minh họa...")
    photo_url = get_photo_url()
    print(f"Ảnh: {photo_url}")
    print("📤 Đang đăng lên Facebook Page Bé Ơi...")
    post_to_facebook(content, photo_url)

if __name__ == "__main__":
    main()
