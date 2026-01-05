"""
Acupoint Image Scraper v2
Downloads 5+ images per acupoint from multiple sources
"""

import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

# Import acupoint data
from acupoint_locator import ACUPOINT_DATA

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(PROJECT_ROOT, "DignoseSource", "acupoint_images")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5,zh-CN;q=0.3"
}

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def download_image(url, save_path):
    """Download image from URL"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        content_type = resp.headers.get('content-type', '')
        if resp.status_code == 200 and len(resp.content) > 2000:
            if 'image' in content_type or url.endswith(('.jpg', '.png', '.gif', '.webp')):
                with open(save_path, 'wb') as f:
                    f.write(resp.content)
                return True
    except Exception as e:
        pass
    return False


def search_google_images(query, num_images=10):
    """Search Google Images"""
    search_url = f"https://www.google.com/search?q={quote(query)}&tbm=isch&safe=active"
    images = []
    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=15)
        # Extract image URLs from various patterns
        patterns = [
            r'"(https?://[^"]+\.(?:jpg|jpeg|png|gif|webp))"',
            r'src="(https?://[^"]+)"[^>]*class="[^"]*rg_i',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, resp.text, re.IGNORECASE)
            for url in matches:
                if 'google' not in url.lower() and 'gstatic' not in url.lower():
                    if url not in images:
                        images.append(url)

        # Also try data-src patterns
        soup = BeautifulSoup(resp.text, 'lxml')
        for img in soup.find_all('img'):
            for attr in ['data-src', 'data-iurl', 'src']:
                src = img.get(attr, '')
                if src and src.startswith('http') and 'google' not in src:
                    if src not in images:
                        images.append(src)
    except Exception as e:
        print(f"    Google error: {e}")

    return images[:num_images]


def search_bing_images(query, num_images=8):
    """Search Bing Images"""
    search_url = f"https://www.bing.com/images/search?q={quote(query)}&form=HDRSC2"
    images = []
    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=15)
        # Bing uses murl parameter for full image URLs
        pattern = r'murl&quot;:&quot;(https?://[^&]+)&quot;'
        matches = re.findall(pattern, resp.text)
        for url in matches:
            url = url.replace('\\u002f', '/')
            if url not in images:
                images.append(url)
    except Exception as e:
        print(f"    Bing error: {e}")

    return images[:num_images]


def search_baidu_images(query, num_images=8):
    """Search Baidu Images (Chinese)"""
    search_url = f"https://image.baidu.com/search/index?tn=baiduimage&word={quote(query)}"
    images = []
    try:
        resp = requests.get(search_url, headers={**HEADERS, "Accept-Language": "zh-CN,zh;q=0.9"}, timeout=15)
        # Baidu uses objURL or thumbURL
        patterns = [
            r'"objURL":"(https?://[^"]+)"',
            r'"thumbURL":"(https?://[^"]+)"',
            r'"middleURL":"(https?://[^"]+)"',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, resp.text)
            for url in matches:
                if url not in images:
                    images.append(url)
    except Exception as e:
        print(f"    Baidu error: {e}")

    return images[:num_images]


def scrape_tcm_sites(code, english_name, chinese_name, meridian):
    """Scrape from TCM educational sites"""
    images = []

    # YinYangHouse
    try:
        url = f"https://yinyanghouse.com/theory/acupuncturepoints/{code.lower()}/"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'lxml')
        for img in soup.find_all('img'):
            src = img.get('src', '') or img.get('data-src', '')
            if src and ('point' in src.lower() or 'meridian' in src.lower() or code.lower() in src.lower()):
                images.append(urljoin(url, src))
    except:
        pass

    # Acupuncture.com
    meridian_map = {
        "Gallbladder": "gallbladder", "Bladder": "bladder", "Kidney": "kidney",
        "Large Intestine": "largeintestine", "Liver": "liver", "Pericardium": "pericardium",
        "Heart": "heart", "Spleen": "spleen", "Stomach": "stomach",
        "Small Intestine": "smallintestine", "San Jiao": "sanjiao"
    }
    try:
        m = meridian_map.get(meridian, meridian.lower().replace(" ", ""))
        url = f"https://www.acupuncture.com/education/points/{m}/{code.lower()}.htm"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'lxml')
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and (code.lower() in src.lower() or '.gif' in src.lower() or '.jpg' in src.lower()):
                images.append(urljoin(url, src))
    except:
        pass

    return images


def scrape_acupoint_images(code, data):
    """Scrape 5+ images for a single acupoint"""
    print(f"\n📍 {code} - {data.get('chinese_name', '')} ({data.get('english_name', '')})")

    point_dir = os.path.join(IMAGE_DIR, code)
    ensure_dir(point_dir)

    chinese_name = data.get('chinese_name', '')
    english_name = data.get('english_name', '')
    meridian = data.get('meridian', '')

    all_images = []

    # 1. TCM educational sites
    print("  [1/4] Scraping TCM sites...")
    all_images.extend(scrape_tcm_sites(code, english_name, chinese_name, meridian))

    # 2. Google Images - multiple queries
    print("  [2/4] Searching Google Images...")
    queries = [
        f"{code} {english_name} acupoint location",
        f"{code} acupuncture point diagram",
        f"{chinese_name}穴 位置图",
    ]
    for q in queries:
        all_images.extend(search_google_images(q, 5))
        time.sleep(0.5)

    # 3. Bing Images
    print("  [3/4] Searching Bing Images...")
    all_images.extend(search_bing_images(f"{code} {english_name} acupoint", 6))

    # 4. Baidu Images (Chinese)
    print("  [4/4] Searching Baidu Images...")
    all_images.extend(search_baidu_images(f"{chinese_name}穴 位置 取穴", 6))

    # Remove duplicates while preserving order
    seen = set()
    unique_images = []
    for url in all_images:
        if url not in seen and url.startswith('http'):
            seen.add(url)
            unique_images.append(url)

    print(f"  Found {len(unique_images)} unique image URLs")

    # Download images (target: at least 5)
    downloaded = []
    for i, img_url in enumerate(unique_images):
        if len(downloaded) >= 8:  # Max 8 per point
            break

        ext = 'jpg'
        if '.png' in img_url.lower():
            ext = 'png'
        elif '.gif' in img_url.lower():
            ext = 'gif'
        elif '.webp' in img_url.lower():
            ext = 'webp'

        filename = f"{code}_{len(downloaded)+1}.{ext}"
        save_path = os.path.join(point_dir, filename)

        if download_image(img_url, save_path):
            downloaded.append(filename)
            print(f"  ✅ [{len(downloaded)}] {filename}")

        if len(downloaded) < 5 and i >= len(unique_images) - 1:
            print(f"  ⚠️  Only got {len(downloaded)} images")

    # Save metadata
    metadata = {
        "code": code,
        "chinese_name": chinese_name,
        "english_name": english_name,
        "images": downloaded,
        "image_count": len(downloaded)
    }
    with open(os.path.join(point_dir, "metadata.json"), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return len(downloaded)


def main():
    print("=" * 60)
    print("🖼️  Acupoint Image Scraper v2")
    print("   Target: 5+ images per acupoint")
    print("=" * 60)

    ensure_dir(IMAGE_DIR)

    total_downloaded = 0
    results = {}

    for code, data in ACUPOINT_DATA.items():
        try:
            count = scrape_acupoint_images(code, data)
            total_downloaded += count
            results[code] = count
            time.sleep(1.5)  # Be nice to servers
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results[code] = 0

    print("\n" + "=" * 60)
    print("📊 Summary:")
    for code, count in results.items():
        status = "✅" if count >= 5 else "⚠️" if count > 0 else "❌"
        print(f"  {status} {code}: {count} images")

    print(f"\n✅ Total: {total_downloaded} images downloaded")
    print(f"📁 Saved to: {IMAGE_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
