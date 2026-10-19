import os
import time
import random
import requests
import subprocess
from datetime import datetime
from urllib.parse import quote

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
FB_PAGE_ID = os.environ.get('FB_PAGE_ID')
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"

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
    "Massage cho bé: lợi ích, kỹ thuật massage nhẹ nhàng cho bé sơ sinh",
    "Dạy bé kỹ năng tự lập: tự ăn, tự mặc quần áo, dọn đồ chơi",
    "Âm nhạc và bé: bài hát ru, nhạc giúp bé phát triển thính giác",
    "Bé tập nói: cách khuyến khích bé nói, trò chuyện với bé mỗi ngày",
    "Chăm sóc răng miệng cho bé: khi nào bé mọc răng, cách vệ sinh",
    "Mẹ sau sinh: cân bằng chăm con và chăm bản thân, tránh kiệt sức",
    "An toàn cho bé: chống ngã, để xa vật nguy hiểm, an toàn khi ngủ"
]

def gemini_generate(prompt):
    """Gọi Gemini API với retry."""
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    for attempt in range(5):
        try:
            res = requests.post(GEMINI_URL, json=payload, timeout=30)
            data = res.json()
            if "candidates" in data:
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"Gemini lỗi: {data.get('error', {}).get('message', 'unknown')}")
        except Exception as e:
            print(f"Gemini request lỗi: {e}")
        if attempt < 4:
            time.sleep(15)
    return None

def generate_reel_content():
    """Tạo nội dung ngắn cho Reel (caption) và 4 mô tả cảnh."""
    topic = random.choice(TOPICS)

    prompt = f"""Bạn là chuyên gia nuôi dạy con của app Bé Ơi.
Tạo nội dung cho 1 Facebook Reel ngắn về chủ đề: {topic}

Trả về đúng format sau (không thêm gì khác):
CAPTION:
(Caption ngắn gọn 50-80 từ, có emoji, cuối có hashtag #BéƠi #ChămsócBé #MẹVàBé và nhắc tải app Bé Ơi)

TIP1:
(Mẹo/lời khuyên thứ 1, tối đa 12 từ tiếng Việt)

TIP2:
(Mẹo/lời khuyên thứ 2, tối đa 12 từ tiếng Việt)

TIP3:
(Mẹo/lời khuyên thứ 3, tối đa 12 từ tiếng Việt)

TITLE:
(Tiêu đề ngắn gọn 5-8 từ tiếng Việt cho video)"""

    result = gemini_generate(prompt)
    if not result:
        raise Exception("Không tạo được nội dung Reel")

    parts = {}
    current_key = None
    current_lines = []
    for line in result.split('\n'):
        line = line.strip()
        if line in ['CAPTION:', 'TIP1:', 'TIP2:', 'TIP3:', 'TITLE:']:
            if current_key:
                parts[current_key] = '\n'.join(current_lines).strip()
            current_key = line.replace(':', '')
            current_lines = []
        elif current_key:
            current_lines.append(line)
    if current_key:
        parts[current_key] = '\n'.join(current_lines).strip()

    print(f"Caption: {parts.get('CAPTION', '')[:80]}...")
    print(f"Tips: {parts.get('TIP1', '')} | {parts.get('TIP2', '')} | {parts.get('TIP3', '')}")
    print(f"Title: {parts.get('TITLE', '')}")
    return parts

def generate_scene_images(parts):
    """Tạo 4 ảnh AI cho 4 cảnh trong video (vertical 1080x1920)."""
    caption = parts.get('CAPTION', '')
    tip1 = parts.get('TIP1', '')
    tip2 = parts.get('TIP2', '')
    tip3 = parts.get('TIP3', '')
    title = parts.get('TITLE', '')

    scenes_prompt = f"""Read this Vietnamese Facebook Reel content carefully:
---
Title: {title}
Caption: {caption}
Tip 1: {tip1}
Tip 2: {tip2}
Tip 3: {tip3}
---

Based on the SPECIFIC content above, generate 4 English image prompts (one per line, max 25 words each).
Each prompt MUST directly illustrate the EXACT activity or scene described:

Scene 1: Illustrate the MAIN subject from the title "{title}" — show the specific baby activity mentioned
Scene 2: Illustrate EXACTLY what tip 1 says: "{tip1}" — show the specific action described
Scene 3: Illustrate EXACTLY what tip 2 says: "{tip2}" — show the specific action described
Scene 4: Illustrate EXACTLY what tip 3 says: "{tip3}" — show the specific action described

IMPORTANT: Be VERY specific. Do NOT use generic baby images. If the tip says "massage baby's gums with gauze", show exactly that. If it says "read book with baby", show a parent reading to a baby.
Style for ALL: soft pastel watercolor, cute cartoon, warm lighting, vertical portrait.
Return ONLY 4 lines, one prompt per line, no numbering."""

    result = gemini_generate(scenes_prompt)
    if not result:
        result = "cute baby smiling with mother, pastel watercolor\nbaby eating healthy food, kawaii illustration\nbaby sleeping peacefully, soft pastel colors\nhappy family with baby, warm illustration"

    scene_prompts = [line.strip() for line in result.strip().split('\n') if line.strip()][:4]
    # Pad to 4 if needed
    while len(scene_prompts) < 4:
        scene_prompts.append("cute happy baby with mother, soft pastel illustration")

    images = []
    for i, sp in enumerate(scene_prompts):
        print(f"🎨 Tạo ảnh cảnh {i+1}/{len(scene_prompts)}: {sp[:60]}...")
        encoded = quote(sp)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&seed={random.randint(1,99999)}&nologo=true"
        for retry in range(3):
            try:
                res = requests.get(url, timeout=90, allow_redirects=True)
                if res.status_code == 200 and 'image' in res.headers.get('Content-Type', ''):
                    img_path = f"/tmp/scene_{i}.jpg"
                    with open(img_path, 'wb') as f:
                        f.write(res.content)
                    images.append(img_path)
                    print(f"  ✅ {len(res.content)} bytes")
                    break
                elif res.status_code == 402:
                    wait = 30 * (retry + 1)
                    print(f"  ⏳ Rate limit, đợi {wait}s... ({retry+1}/3)")
                    time.sleep(wait)
                else:
                    print(f"  ❌ Status {res.status_code}")
                    break
            except Exception as e:
                print(f"  ❌ Lỗi: {e}")
                break
        # Delay giữa các ảnh để tránh rate limit
        if i < len(scene_prompts) - 1:
            time.sleep(15)

    if len(images) < 2:
        raise Exception(f"Chỉ tạo được {len(images)} ảnh, cần ít nhất 2")
    return images

def create_video(images, parts):
    """Dùng ffmpeg tạo video từ ảnh — simple concat với fade transition."""
    output_path = "/tmp/reel.mp4"
    duration_per_image = 4  # seconds per scene

    # Simple approach: scale + concat with fade (no zoompan — too slow on CI)
    inputs = []
    filters = []
    for i, img in enumerate(images):
        inputs.extend(['-loop', '1', '-t', str(duration_per_image), '-i', img])
        filters.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
                       f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24[v{i}]")

    if len(images) == 1:
        filter_str = filters[0]
        last_label = "v0"
    else:
        filter_str = ";".join(filters)
        # Simple concat with fade between scenes
        concat_inputs = "".join(f"[v{i}]" for i in range(len(images)))
        filter_str += f";{concat_inputs}concat=n={len(images)}:v=1:a=0[final]"
        last_label = "final"

    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', filter_str,
        '-map', f'[{last_label}]',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'fast',
        '-crf', '20',
        '-movflags', '+faststart',
        output_path
    ]

    print(f"🎬 Tạo video ({len(images)} cảnh x {duration_per_image}s)...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"ffmpeg stderr: {result.stderr[-500:]}")
        raise Exception(f"ffmpeg failed with code {result.returncode}")

    size = os.path.getsize(output_path)
    print(f"✅ Video tạo xong: {size} bytes ({size/1024/1024:.1f} MB)")
    return output_path

def upload_reel(video_path, caption):
    """Upload video lên Facebook Reels qua API."""
    file_size = os.path.getsize(video_path)

    # Step 1: Start upload session
    print("📤 Bắt đầu upload Reel...")
    start_url = f"https://graph.facebook.com/v26.0/{FB_PAGE_ID}/video_reels"
    start_res = requests.post(start_url, data={
        "upload_phase": "start",
        "access_token": FB_PAGE_TOKEN,
    }, timeout=30)
    start_data = start_res.json()

    if "video_id" not in start_data:
        raise Exception(f"Start upload failed: {start_data}")

    video_id = start_data["video_id"]
    print(f"Video ID: {video_id}")

    # Step 2: Upload binary
    upload_url = f"https://rupload.facebook.com/video-upload/v26.0/{video_id}"
    with open(video_path, 'rb') as f:
        video_data = f.read()

    upload_res = requests.post(upload_url, data=video_data, headers={
        "Authorization": f"OAuth {FB_PAGE_TOKEN}",
        "offset": "0",
        "file_size": str(file_size),
        "Content-Type": "application/octet-stream",
    }, timeout=120)
    upload_data = upload_res.json()
    print(f"Upload response: {upload_data}")

    if not upload_data.get("success"):
        raise Exception(f"Upload binary failed: {upload_data}")

    # Step 3: Finish and publish
    finish_url = f"https://graph.facebook.com/v26.0/{FB_PAGE_ID}/video_reels"
    finish_res = requests.post(finish_url, data={
        "upload_phase": "finish",
        "access_token": FB_PAGE_TOKEN,
        "video_id": video_id,
        "title": caption[:80],
        "description": caption,
    }, timeout=60)
    finish_data = finish_res.json()

    if finish_data.get("success"):
        print(f"✅ Reel đăng thành công! Video ID: {video_id}")
    else:
        raise Exception(f"Finish upload failed: {finish_data}")

def main():
    print(f"🚀 Bắt đầu tạo Reel: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n📝 Đang tạo nội dung Reel...")
    parts = generate_reel_content()

    print("\n🎨 Đang tạo ảnh AI cho các cảnh...")
    images = generate_scene_images(parts)

    print("\n🎬 Đang tạo video...")
    video_path = create_video(images, parts)

    print("\n📤 Đang đăng Reel lên Facebook...")
    upload_reel(video_path, parts.get('CAPTION', ''))

    # Cleanup
    for img in images:
        os.remove(img) if os.path.exists(img) else None
    os.remove(video_path) if os.path.exists(video_path) else None

    print("\n🎉 Hoàn tất!")

if __name__ == "__main__":
    main()
