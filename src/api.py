"""
Acupressure Diagnosis API
Run: python api.py
API will be available at http://localhost:8080
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
import requests

# LLM API Configuration (set your API key in environment variable)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Import from our modules
from acupoint_locator import ACUPOINT_DATA, find_acupoint, generate_image_urls
from symptom_diagnosis import diagnose, load_symptom_database

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(PROJECT_ROOT, "DignoseSource", "acupoint_images")
CHINESE_IMAGE_DIR = os.path.join(PROJECT_ROOT, "DignoseSource", "Chinese acuPointData", "acupoints.asp_files")

# Mapping from acupoint code to Chinese name pattern for image lookup
# Some images use 穴 suffix, some don't
CODE_TO_CHINESE = {
    "GB30": "环跳穴",
    "BL23": "肾俞穴",
    "BL40": "委中穴",
    "BL60": "昆仑穴",
    "KI3": "太溪穴",
    "LI4": "合谷穴",
    "LR3": "太冲穴",
    "PC6": "内关穴",
    "ST36": "足三里",  # No 穴 suffix
    "SP6": "三阴交",   # No 穴 suffix
    "SP4": "公孙穴",
    "HT7": "神门穴",
    "KI1": "涌泉穴",
    "GB20": "风池穴",
    "GB21": "肩井穴",
    "SI3": "后溪穴",
    "SJ5": "外关穴",
    "BL2": "攒竹穴",
    "EX-HN3": "印堂穴",
    "EX-HN5": "太阳穴",
    "TF4": "耳神门穴",
    "GV20": "百会穴",
    "CV17": "膻中穴",
    "LI11": "曲池穴",
    "LR14": "期门穴",
    "BL32": "次髎穴",
    "GB34": "阳陵泉",  # No 穴 suffix
    "GV4": "命门穴",
}

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access


@app.route('/')
def index():
    """API info"""
    return jsonify({
        "name": "Acupressure Diagnosis API",
        "version": "1.0",
        "endpoints": {
            "GET /symptoms": "List all available symptoms",
            "GET /diagnose/<symptom>": "Get acupoints for a symptom",
            "GET /acupoint/<code>": "Get details for a specific acupoint",
            "GET /acupoints": "List all acupoints in database",
            "GET /search?q=<query>": "Search symptoms and acupoints"
        }
    })


@app.route('/symptoms')
def list_symptoms():
    """List all available symptoms"""
    db = load_symptom_database()
    symptoms = [s['symptom'] for s in db['symptoms']]
    return jsonify({
        "count": len(symptoms),
        "symptoms": symptoms
    })


@app.route('/diagnose/<symptom>')
def diagnose_symptom(symptom):
    """Get acupoint recommendations for a symptom"""
    result = diagnose(symptom)
    return jsonify(result)


@app.route('/acupoint/<code>')
def get_acupoint(code):
    """Get detailed info for a specific acupoint"""
    result = find_acupoint(code)
    if result:
        return jsonify({
            "success": True,
            "acupoint": result
        })
    else:
        return jsonify({
            "success": False,
            "error": f"Acupoint '{code}' not found",
            "available": list(ACUPOINT_DATA.keys())
        }), 404


@app.route('/acupoints')
def list_acupoints():
    """List all acupoints in database"""
    acupoints = []
    for code, data in ACUPOINT_DATA.items():
        acupoints.append({
            "code": data.get("code", code),
            "chinese_name": data.get("chinese_name", ""),
            "english_name": data.get("english_name", ""),
            "meridian": data.get("meridian", "")
        })
    return jsonify({
        "count": len(acupoints),
        "acupoints": acupoints
    })


@app.route('/search')
def search():
    """Search symptoms and acupoints"""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"error": "Please provide search query ?q=<query>"}), 400

    results = {
        "query": query,
        "symptoms": [],
        "acupoints": []
    }

    # Search symptoms
    db = load_symptom_database()
    for s in db['symptoms']:
        if query in s['symptom'].lower():
            results['symptoms'].append(s['symptom'])

    # Search acupoints
    for code, data in ACUPOINT_DATA.items():
        searchable = f"{code} {data.get('chinese_name', '')} {data.get('english_name', '')} {data.get('pinyin', '')}".lower()
        if query in searchable:
            results['acupoints'].append({
                "code": data.get("code", code),
                "chinese_name": data.get("chinese_name", ""),
                "english_name": data.get("english_name", "")
            })

    return jsonify(results)


# LLM prompt for complex symptom analysis
LLM_SYSTEM_PROMPT = """你是一位专业的中医针灸穴位顾问。用户会描述他们的症状，请你：

1. 分析症状，理解用户的问题
2. 推荐适合的穴位按摩（如果有的话）
3. 提供一些日常保健建议

我们数据库中有以下穴位：
- GB30 环跳 - 腰腿痛、坐骨神经痛
- BL23 肾俞 - 腰痛、肾虚
- BL40 委中 - 腰背痛、腿痛
- LI4 合谷 - 头痛、牙痛、感冒
- GB20 风池 - 头痛、颈椎病、感冒
- SP6 三阴交 - 妇科问题、失眠、消化
- ST36 足三里 - 消化、增强体质
- PC6 内关 - 恶心、心悸、焦虑
- HT7 神门 - 失眠、焦虑、心悸
- LR3 太冲 - 头痛、高血压、情绪
- CV17 膻中 - 胸闷、咳嗽、乳腺问题
- GV20 百会 - 头痛、眩晕、失眠

请用简洁的中文回答，格式如下：
【症状分析】简短分析
【推荐穴位】列出1-3个最相关的穴位代码（如 LI4, GB20）
【保健建议】2-3条实用建议
【注意事项】如果症状严重需要就医请提醒"""


def call_llm_api(user_message):
    """Call LLM API for complex symptom analysis"""

    # Try OpenAI first
    if OPENAI_API_KEY:
        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": LLM_SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OpenAI API error: {e}")

    # Try Anthropic Claude
    if ANTHROPIC_API_KEY:
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 500,
                    "system": LLM_SYSTEM_PROMPT,
                    "messages": [
                        {"role": "user", "content": user_message}
                    ]
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json()["content"][0]["text"]
        except Exception as e:
            print(f"Anthropic API error: {e}")

    return None


# Keyword mapping for natural language understanding
SYMPTOM_KEYWORDS = {
    "headache": ["head", "头", "头痛", "头疼", "migraine", "偏头痛"],
    "neck": ["neck", "颈", "脖子", "shoulder", "肩", "肩膀", "僵硬", "stiff"],
    "back": ["back", "腰", "背", "sciatica", "坐骨", "spine", "脊"],
    "anxiety": ["anxiety", "anxious", "stress", "紧张", "焦虑", "压力", "nervous"],
    "insomnia": ["sleep", "insomnia", "失眠", "睡不着", "睡眠", "tired", "疲劳"],
    "nausea": ["nausea", "vomit", "恶心", "呕吐", "motion", "晕车", "stomach", "胃"],
    "eye": ["eye", "眼", "vision", "视力", "疲劳"],
    "digestion": ["digest", "消化", "stomach", "胃", "bloat", "腹胀"],
    "menstrual": ["period", "menstrual", "月经", "痛经", "cramp"],
}


@app.route('/chat', methods=['POST'])
def chat_diagnose():
    """Natural language symptom diagnosis - chat style"""
    data = request.get_json() or {}
    user_input = data.get('message', '').lower()

    if not user_input:
        return jsonify({"error": "Please provide a message"}), 400

    # Find matching symptoms based on keywords
    matched_symptoms = []
    db = load_symptom_database()

    for symptom_key, keywords in SYMPTOM_KEYWORDS.items():
        for keyword in keywords:
            if keyword in user_input:
                # Find the full symptom name in database
                for s in db['symptoms']:
                    if symptom_key in s['symptom'].lower():
                        if s['symptom'] not in matched_symptoms:
                            matched_symptoms.append(s['symptom'])
                break

    # If no keyword match, try direct search in symptom names
    if not matched_symptoms:
        for s in db['symptoms']:
            symptom_lower = s['symptom'].lower()
            for word in user_input.split():
                if len(word) > 2 and word in symptom_lower:
                    if s['symptom'] not in matched_symptoms:
                        matched_symptoms.append(s['symptom'])

    if not matched_symptoms:
        # Try LLM for complex symptoms
        llm_response = call_llm_api(user_input)
        if llm_response:
            # Extract acupoint codes from LLM response
            import re
            acupoint_codes = re.findall(r'\b(GB\d+|BL\d+|LI\d+|SP\d+|ST\d+|PC\d+|HT\d+|LR\d+|KI\d+|CV\d+|GV\d+|SI\d+|SJ\d+|EX-HN\d+)\b', llm_response, re.IGNORECASE)
            acupoint_codes = list(set([c.upper() for c in acupoint_codes]))

            # Get acupoint details for recommended points
            recommended_acupoints = []
            for code in acupoint_codes[:3]:  # Max 3 acupoints
                if code in ACUPOINT_DATA:
                    point_data = ACUPOINT_DATA[code]
                    recommended_acupoints.append({
                        "code": code,
                        "chinese_name": point_data.get("chinese_name", ""),
                        "name": point_data.get("english_name", "")
                    })

            return jsonify({
                "success": True,
                "mode": "llm",
                "user_input": user_input,
                "llm_response": llm_response,
                "recommended_acupoints": recommended_acupoints
            })

        # No LLM available, return error
        return jsonify({
            "success": False,
            "message": "抱歉，我没有找到匹配的症状。请试试：头痛、失眠、焦虑、腰痛、颈椎等关键词。\n\n如需更智能的分析，请设置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY 环境变量。",
            "available_symptoms": [s['symptom'] for s in db['symptoms']]
        })

    # Get diagnosis for first matched symptom
    primary_symptom = matched_symptoms[0]
    result = diagnose(primary_symptom.split('/')[0].strip())

    return jsonify({
        "success": True,
        "user_input": user_input,
        "matched_symptoms": matched_symptoms,
        "diagnosis": result
    })


@app.route('/images/<code>')
def get_acupoint_images(code):
    """Get list of images for an acupoint from all sources"""
    code_upper = code.upper()
    images = []

    # Source 1: Scraped images from IMAGE_DIR (e.g., /DignoseSource/acupoint_images/GB30/)
    point_dir = os.path.join(IMAGE_DIR, code_upper)
    if os.path.exists(point_dir):
        for f in os.listdir(point_dir):
            if f.endswith(('.jpg', '.png', '.gif', '.webp')):
                images.append(f"/images/{code_upper}/{f}")

    # Source 2: Chinese acuPointData images (named by Chinese name)
    chinese_name = CODE_TO_CHINESE.get(code_upper, "")
    if chinese_name and os.path.exists(CHINESE_IMAGE_DIR):
        for f in os.listdir(CHINESE_IMAGE_DIR):
            # Match files like "合谷穴1.jpg", "三阴交1.jpg"
            if f.startswith(chinese_name) and f.endswith(('.jpg', '.png', '.gif', '.webp')):
                images.append(f"/images/chinese/{f}")

    return jsonify({"code": code_upper, "images": images, "count": len(images)})


@app.route('/images/<code>/<filename>')
def serve_image(code, filename):
    """Serve acupoint image file from scraped folder"""
    point_dir = os.path.join(IMAGE_DIR, code.upper())
    return send_from_directory(point_dir, filename)


@app.route('/images/chinese/<filename>')
def serve_chinese_image(filename):
    """Serve acupoint image file from Chinese acuPointData folder"""
    return send_from_directory(CHINESE_IMAGE_DIR, filename)


# ============ ChatGPT Plugin Support ============

@app.route('/.well-known/ai-plugin.json')
def serve_plugin_manifest():
    """Serve ChatGPT plugin manifest"""
    return send_from_directory(
        os.path.join(PROJECT_ROOT, '.well-known'),
        'ai-plugin.json',
        mimetype='application/json'
    )


@app.route('/openapi.yaml')
def serve_openapi_spec():
    """Serve OpenAPI specification"""
    return send_from_directory(PROJECT_ROOT, 'openapi.yaml', mimetype='text/yaml')


@app.route('/logo.png')
def serve_logo():
    """Serve plugin logo"""
    # Return a simple placeholder or actual logo
    return send_from_directory(os.path.join(PROJECT_ROOT, 'web'), 'logo.png')


if __name__ == '__main__':
    print("\n🔌 Acupressure Diagnosis API")
    print("=" * 40)
    print("Endpoints:")
    print("  GET /symptoms          - List symptoms")
    print("  GET /diagnose/<symptom> - Get diagnosis")
    print("  GET /acupoint/<code>   - Get acupoint details")
    print("  GET /acupoints         - List all acupoints")
    print("  GET /search?q=<query>  - Search")
    print("=" * 40)
    print("\nStarting server at http://localhost:8080\n")
    app.run(debug=True, port=8080)
