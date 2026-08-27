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
        keyword = random.choice(PHOTO_KEYWORDS).replace(" ", ",")
        seed = random.randint(1, 1000)
        url = f"https://loremflickr.com/800/600/{keyword}?random={seed}&lock={seed}"
        res = requests.get(url, timeout=15, allow_redirects=True)
        if res.status_code == 200 and 'image' in res.headers.get('Content-Type', ''):
            print(f"Ảnh URL: {res.url}")
            return res.url
        print(f"Không lấy được ảnh, status: {res.status_code}")
    except Exception as e:
        print(f"Lỗi lấy ảnh: {e}")
    return None

TOPICS = [
    "Dinh dưỡng cho bé: thực đơn ăn dặm, bữa ăn cân bằng, thực phẩm tốt cho trí não",
    "Giấc ngủ của bé: mẹo giúp bé ngủ ngon, giờ ngủ phù hợp theo độ tuổi",
    "Phát triển vận động: bé tập lẫy, tập bò, tập đi, các mốc phát triển",
    "Sức khỏe bé: dấu hiệu bé ốm, cách chăm sóc khi bé sốt, tiêm phòng",
    "Trò chơi phát triển trí não: đồ chơi phù hợp, hoạt động kích thích sáng tạo",
    "Gắn kết gia đình: đọc sách cùng bé, thời gian chất lượng bên con",
    "Tắm và vệ sinh cho bé: cách tắm an toàn, chăm sóc da bé",
    "Mẹo chăm bé mùa nóng: giữ mát, phòng rôm sảy, bổ sung nước",
    "Mẹo chăm bé mùa lạnh: giữ ấm, phòng cảm cúm, tăng đề kháng",
    "Tâm lý bé: hiểu cảm xúc của bé, cách dỗ bé khóc, xây dựng thói quen tốt",
    "Sữa mẹ và cách cho bé bú: lợi ích sữa mẹ, tư thế cho bú đúng cách",
    "Bé và giấc ngủ trưa: tầm quan trọng, cách tạo thói quen ngủ trưa",
    "Massage cho bé: lợi ích, kỹ thuật massage nhẹ nhàng cho bé sơ sinh",
    "Chuẩn bị đồ đi ra ngoài cùng bé: checklist, mẹo tiện lợi cho mẹ",
    "Dạy bé kỹ năng tự lập: tự ăn, tự mặc quần áo, dọn đồ chơi",
    "Âm nhạc và bé: bài hát ru, nhạc giúp bé phát triển thính giác",
    "Bé tập nói: cách khuyến khích bé nói, trò chuyện với bé mỗi ngày",
    "Chăm sóc răng miệng cho bé: khi nào bé mọc răng, cách vệ sinh",
    "Mẹ sau sinh: cân bằng chăm con và chăm bản thân, tránh kiệt sức",
    "An toàn cho bé: chống ngã, để xa vật nguy hiểm, an toàn khi ngủ"
]

def generate_content():
    topic = random.choice(TOPICS)

    prompt = f"""Bạn là chuyên gia tư vấn nuôi dạy con của app Bé Ơi.
Viết 1 bài đăng Facebook về chủ đề: {topic}
Yêu cầu:
- Thân thiện, ấm áp với các mẹ Việt Nam
- Có emoji phù hợp
- 150-250 từ
- Cuối bài nhắc tải app Bé Ơi
- Hashtag: #BéƠi #ChămsócBé #MẹVàBé
- Không lặp lại nội dung các bài trước
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
