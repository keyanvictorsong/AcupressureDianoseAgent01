#!/usr/bin/env python3
"""Generate static JSON files for GitHub Pages hosting"""

import json
import os
import shutil

# Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
API_DIR = os.path.join(DOCS_DIR, "api")

# Import data
import sys
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
from acupoint_locator import ACUPOINT_DATA

# Load symptom database
with open(os.path.join(PROJECT_ROOT, "DignoseSource", "acupressure_by_symptom.json"), 'r', encoding='utf-8') as f:
    SYMPTOM_DB = json.load(f)

# Chinese name mapping
CODE_TO_CHINESE = {
    "GB30": "环跳穴", "BL23": "肾俞穴", "BL40": "委中穴", "BL60": "昆仑穴",
    "KI3": "太溪穴", "LI4": "合谷穴", "LR3": "太冲穴", "PC6": "内关穴",
    "ST36": "足三里", "SP6": "三阴交", "SP4": "公孙穴", "HT7": "神门穴",
    "KI1": "涌泉穴", "GB20": "风池穴", "GB21": "肩井穴", "SI3": "后溪穴",
    "SJ5": "外关穴", "BL2": "攒竹穴", "EX-HN3": "印堂穴", "EX-HN5": "太阳穴",
    "LV3": "太冲穴", "GV20": "百会穴", "CV17": "膻中穴", "LI11": "曲池穴",
    "AURICULAR_SHENMEN": "耳神门"
}

def ensure_dirs():
    """Create necessary directories"""
    os.makedirs(os.path.join(API_DIR, "acupoint"), exist_ok=True)
    os.makedirs(os.path.join(API_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(API_DIR, "diagnose"), exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, ".well-known"), exist_ok=True)

def generate_symptoms():
    """Generate symptoms.json"""
    symptoms = [s['symptom'] for s in SYMPTOM_DB['symptoms']]
    data = {"count": len(symptoms), "symptoms": symptoms}

    with open(os.path.join(API_DIR, "symptoms.json"), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Generated symptoms.json ({len(symptoms)} symptoms)")

def generate_acupoints():
    """Generate acupoints.json"""
    acupoints = []
    for code, data in ACUPOINT_DATA.items():
        acupoints.append({
            "code": data.get("code", code),
            "chinese_name": data.get("chinese_name", ""),
            "english_name": data.get("english_name", ""),
            "meridian": data.get("meridian", "")
        })

    result = {"count": len(acupoints), "acupoints": acupoints}

    with open(os.path.join(API_DIR, "acupoints.json"), 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✓ Generated acupoints.json ({len(acupoints)} acupoints)")

def generate_acupoint_details():
    """Generate individual acupoint JSON files"""
    for code, data in ACUPOINT_DATA.items():
        result = {"success": True, "acupoint": data}

        filepath = os.path.join(API_DIR, "acupoint", f"{code}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✓ Generated {len(ACUPOINT_DATA)} acupoint detail files")

def generate_diagnose_files():
    """Generate diagnosis result files for each symptom"""
    for symptom_data in SYMPTOM_DB['symptoms']:
        symptom = symptom_data['symptom']

        # Create safe filename
        safe_name = symptom.split('/')[0].strip().replace(' ', '_').lower()

        acupoints = []
        for point in symptom_data['points']:
            code = point['code']
            if code == "Auricular Shenmen":
                code = "AURICULAR_SHENMEN"

            acupoints.append({
                "code": code,
                "name": point['name'],
                "chinese_name": ACUPOINT_DATA.get(code, {}).get('chinese_name', ''),
                "location_hint": point.get('location_hint', ''),
                "notes": point.get('notes', '')
            })

        result = {
            "success": True,
            "symptom": symptom,
            "acupoints": acupoints,
            "disclaimer": SYMPTOM_DB.get('disclaimer', 'For educational reference only.')
        }

        filepath = os.path.join(API_DIR, "diagnose", f"{safe_name}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✓ Generated {len(SYMPTOM_DB['symptoms'])} diagnose files")

def copy_images():
    """Copy images to docs folder and generate image index files"""
    src_images = os.path.join(PROJECT_ROOT, "DignoseSource", "acupoint_images")
    chinese_images = os.path.join(PROJECT_ROOT, "DignoseSource", "Chinese acuPointData", "acupoints.asp_files")
    dst_images = os.path.join(DOCS_DIR, "images")

    image_count = 0

    # Copy scraped images
    if os.path.exists(src_images):
        for code_dir in os.listdir(src_images):
            code_path = os.path.join(src_images, code_dir)
            if os.path.isdir(code_path):
                dst_code_path = os.path.join(dst_images, code_dir)
                os.makedirs(dst_code_path, exist_ok=True)

                images_list = []
                for f in os.listdir(code_path):
                    if f.endswith(('.jpg', '.png', '.gif', '.webp')):
                        shutil.copy2(os.path.join(code_path, f), os.path.join(dst_code_path, f))
                        images_list.append(f"/images/{code_dir}/{f}")
                        image_count += 1

                # Generate image index for this acupoint
                index_data = {"code": code_dir, "images": images_list, "count": len(images_list)}
                with open(os.path.join(API_DIR, "images", f"{code_dir}.json"), 'w', encoding='utf-8') as f:
                    json.dump(index_data, f, ensure_ascii=False, indent=2)

    # Copy Chinese images
    chinese_dst = os.path.join(dst_images, "chinese")
    os.makedirs(chinese_dst, exist_ok=True)

    if os.path.exists(chinese_images):
        for f in os.listdir(chinese_images):
            if f.endswith(('.jpg', '.png', '.gif', '.webp')):
                shutil.copy2(os.path.join(chinese_images, f), os.path.join(chinese_dst, f))
                image_count += 1

    # Update image indexes with Chinese images
    for code, chinese_name in CODE_TO_CHINESE.items():
        index_path = os.path.join(API_DIR, "images", f"{code}.json")

        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        else:
            index_data = {"code": code, "images": [], "count": 0}

        # Add Chinese images
        if os.path.exists(chinese_images):
            for f in os.listdir(chinese_images):
                if f.startswith(chinese_name.rstrip('穴')) and f.endswith(('.jpg', '.png', '.gif', '.webp')):
                    img_path = f"/images/chinese/{f}"
                    if img_path not in index_data["images"]:
                        index_data["images"].append(img_path)

        index_data["count"] = len(index_data["images"])

        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"✓ Copied {image_count} images")

def generate_chat_mapping():
    """Generate keyword to symptom mapping for static chat"""
    mapping = {
        "headache": "headache",
        "头痛": "headache",
        "头疼": "headache",
        "migraine": "headache",
        "偏头痛": "headache",

        "neck": "neck",
        "颈": "neck",
        "脖子": "neck",
        "shoulder": "neck",
        "肩": "neck",

        "back": "low_back_pain",
        "腰": "low_back_pain",
        "背": "low_back_pain",
        "sciatica": "low_back_pain",
        "坐骨": "low_back_pain",

        "anxiety": "anxiety",
        "焦虑": "anxiety",
        "紧张": "anxiety",
        "stress": "anxiety",
        "压力": "anxiety",

        "insomnia": "insomnia",
        "失眠": "insomnia",
        "睡不着": "insomnia",
        "sleep": "insomnia",

        "nausea": "nausea",
        "恶心": "nausea",
        "呕吐": "nausea",
        "晕车": "nausea",
        "vomit": "nausea"
    }

    with open(os.path.join(API_DIR, "keyword_mapping.json"), 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print("✓ Generated keyword_mapping.json")

def generate_plugin_files():
    """Generate ChatGPT plugin manifest and OpenAPI spec"""

    # ai-plugin.json - needs to be updated by user with their domain
    plugin_manifest = {
        "schema_version": "v1",
        "name_for_human": "穴位诊断助手",
        "name_for_model": "acupressure_diagnosis",
        "description_for_human": "输入症状，获取穴位按摩建议和位置图片。",
        "description_for_model": "This plugin helps users find acupressure points based on symptoms. When a user describes pain or discomfort, use this plugin to get recommended acupoints with location images. Endpoints: /api/symptoms.json for symptom list, /api/diagnose/{symptom}.json for diagnosis, /api/images/{code}.json for acupoint images.",
        "auth": {"type": "none"},
        "api": {
            "type": "openapi",
            "url": "https://YOUR_USERNAME.github.io/YOUR_REPO/openapi.yaml"
        },
        "logo_url": "https://YOUR_USERNAME.github.io/YOUR_REPO/logo.png",
        "contact_email": "your@email.com",
        "legal_info_url": "https://YOUR_USERNAME.github.io/YOUR_REPO/"
    }

    with open(os.path.join(DOCS_DIR, ".well-known", "ai-plugin.json"), 'w', encoding='utf-8') as f:
        json.dump(plugin_manifest, f, ensure_ascii=False, indent=2)

    # OpenAPI spec for static files
    openapi_spec = """openapi: 3.0.1
info:
  title: 穴位诊断助手 API (Static)
  description: 根据症状推荐穴位按摩方案，提供穴位位置图片 (静态托管版本)
  version: 1.0.0
servers:
  - url: https://YOUR_USERNAME.github.io/YOUR_REPO
paths:
  /api/symptoms.json:
    get:
      operationId: listSymptoms
      summary: 获取所有支持的症状列表
      responses:
        "200":
          description: 症状列表

  /api/acupoints.json:
    get:
      operationId: listAcupoints
      summary: 获取所有穴位列表
      responses:
        "200":
          description: 穴位列表

  /api/diagnose/{symptom}.json:
    get:
      operationId: diagnoseSymptom
      summary: 根据症状获取穴位推荐
      parameters:
        - name: symptom
          in: path
          required: true
          schema:
            type: string
          description: 症状关键词 (headache, insomnia, anxiety, neck, low_back_pain, nausea)
      responses:
        "200":
          description: 穴位推荐结果

  /api/images/{code}.json:
    get:
      operationId: getAcupointImages
      summary: 获取穴位图片列表
      parameters:
        - name: code
          in: path
          required: true
          schema:
            type: string
          description: 穴位代码 (如 LI4, GB20, SP6)
      responses:
        "200":
          description: 图片URL列表
"""

    with open(os.path.join(DOCS_DIR, "openapi.yaml"), 'w', encoding='utf-8') as f:
        f.write(openapi_spec)

    print("✓ Generated plugin files (ai-plugin.json, openapi.yaml)")

def generate_index_html():
    """Generate a simple index.html for the static site"""
    html = """<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>穴位诊断助手 | Acupressure Diagnosis</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 { color: #667eea; margin-bottom: 10px; }
        .subtitle { color: #666; margin-bottom: 30px; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #333; font-size: 18px; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 5px; }
        .btn-grid { display: flex; flex-wrap: wrap; gap: 10px; }
        .btn {
            padding: 12px 20px;
            border: 2px solid #667eea;
            border-radius: 25px;
            background: white;
            color: #667eea;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        .btn:hover { background: #667eea; color: white; }
        .result {
            background: #f5f5f5;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            display: none;
        }
        .result.show { display: block; }
        .acupoint-card {
            background: white;
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
        }
        .acupoint-card h3 { color: #667eea; }
        .code {
            background: #667eea;
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-right: 8px;
        }
        .images { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
        .images img {
            width: 100px;
            height: 100px;
            object-fit: cover;
            border-radius: 8px;
            cursor: pointer;
        }
        .disclaimer {
            background: #fff3cd;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 穴位诊断助手</h1>
        <p class="subtitle">选择你的症状，获取穴位按摩建议</p>

        <div class="section">
            <h2>常见症状</h2>
            <div class="btn-grid">
                <button class="btn" onclick="diagnose('headache')">🤕 头痛</button>
                <button class="btn" onclick="diagnose('insomnia')">😴 失眠</button>
                <button class="btn" onclick="diagnose('anxiety')">😰 焦虑</button>
                <button class="btn" onclick="diagnose('neck')">💆 颈肩痛</button>
                <button class="btn" onclick="diagnose('low_back_pain')">🦴 腰痛</button>
                <button class="btn" onclick="diagnose('nausea')">🤢 恶心</button>
            </div>
        </div>

        <div class="result" id="result"></div>

        <div class="disclaimer">
            ⚠️ 本工具仅供健康参考，不能替代专业医疗诊断。如有严重症状请及时就医。
        </div>
    </div>

    <script>
        const BASE = window.location.origin + window.location.pathname.replace(/\\/[^\\/]*$/, '');

        async function diagnose(symptom) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<p>加载中...</p>';
            resultDiv.classList.add('show');

            try {
                const res = await fetch(`${BASE}/api/diagnose/${symptom}.json`);
                const data = await res.json();

                let html = `<h3>针对「${data.symptom}」推荐穴位：</h3>`;

                for (const point of data.acupoints) {
                    // Fetch images
                    let images = [];
                    try {
                        const imgRes = await fetch(`${BASE}/api/images/${point.code}.json`);
                        const imgData = await imgRes.json();
                        images = imgData.images || [];
                    } catch(e) {}

                    html += `
                        <div class="acupoint-card">
                            <h3><span class="code">${point.code}</span>${point.chinese_name || ''} ${point.name}</h3>
                            <p>${point.location_hint || ''}</p>
                            <div class="images">
                                ${images.slice(0, 4).map(img =>
                                    `<img src="${BASE}${img}" onclick="window.open(this.src)" alt="${point.code}">`
                                ).join('')}
                            </div>
                        </div>
                    `;
                }

                resultDiv.innerHTML = html;
            } catch(e) {
                resultDiv.innerHTML = '<p>加载失败，请稍后重试</p>';
            }
        }
    </script>
</body>
</html>
"""

    with open(os.path.join(DOCS_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(html)

    print("✓ Generated index.html")

def main():
    print("=" * 50)
    print("生成静态网站文件...")
    print("=" * 50)

    ensure_dirs()
    generate_symptoms()
    generate_acupoints()
    generate_acupoint_details()
    generate_diagnose_files()
    copy_images()
    generate_chat_mapping()
    generate_plugin_files()
    generate_index_html()

    print("=" * 50)
    print("✅ 完成！静态文件已生成到 docs/ 目录")
    print()
    print("下一步：")
    print("1. 创建 GitHub 仓库")
    print("2. 推送代码")
    print("3. 在 Settings > Pages 启用 GitHub Pages (选择 docs/ 目录)")
    print("4. 修改 docs/.well-known/ai-plugin.json 和 docs/openapi.yaml 中的域名")
    print("=" * 50)

if __name__ == "__main__":
    main()
