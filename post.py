import os
import anthropic
import requests
from datetime import datetime

CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')
FB_PAGE_ID = os.environ.get('FB_PAGE_ID')
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')

def generate_content():
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    
    hour = datetime.utcnow().hour
    
    if hour < 8:
        topic = "buổi sáng - mẹo khởi động ngày mới cùng bé"
    elif hour < 14:
        topic = "buổi trưa - dinh dưỡng và giấc ngủ trưa của bé"
    else:
        topic = "buổi tối - thư giãn và gắn kết gia đình với bé"
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Bạn là chuyên gia tư vấn nuôi dạy con của app Bé Ơi.
Viết 1 bài đăng Facebook về chủ đề: {topic}
Yêu cầu:
- Thân thiện, ấm áp với các mẹ Việt Nam
- Có emoji phù hợp
- 150-250 từ
- Cuối bài nhắc tải app Bé Ơi
- Hashtag: #BéƠi #ChămsócBé #MẹVàBé
Chỉ trả về nội dung bài viết."""
        }]
    )
    return message.content[0].text

def post_to_facebook(content):
    url = f"https://graph.facebook.com/v26.0/{FB_PAGE_ID}/feed"
    response = requests.post(url, data={
        "message": content,
        "access_token": FB_PAGE_TOKEN
    })
    result = response.json()
    if "id" in result:
        print(f"✅ Đăng thành công! Post ID: {result['id']}")
    else:
        print(f"❌ Lỗi: {result}")

def main():
    print(f"🚀 Bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Đang tạo nội dung...")
    content = generate_content()
    print(f"Nội dung:\n{content}\n")
    print("📤 Đang đăng lên Facebook...")
    post_to_facebook(content)

if __name__ == "__main__":
    main()
