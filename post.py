import os
import time
import requests
from datetime import datetime

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
FB_PAGE_ID = os.environ.get('FB_PAGE_ID')
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"

def generate_content():
    hour = datetime.utcnow().hour

    if hour < 8:
        topic = "buổi sáng - mẹo khởi động ngày mới cùng bé"
    elif hour < 14:
        topic = "buổi trưa - dinh dưỡng và giấc ngủ trưa của bé"
    else:
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

def post_to_facebook(content):
    url = f"https://graph.facebook.com/v26.0/{FB_PAGE_ID}/feed"
    response = requests.post(url, data={
        "message": content,
        "access_token": FB_PAGE_TOKEN
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
    print("📤 Đang đăng lên Facebook Page Bé Ơi...")
    post_to_facebook(content)

if __name__ == "__main__":
    main()
