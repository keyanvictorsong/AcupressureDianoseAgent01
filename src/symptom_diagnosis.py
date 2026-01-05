"""
Symptom-based Acupressure Diagnosis System
Usage: python symptom_diagnosis.py "low back pain"
       python symptom_diagnosis.py --list  (show all symptoms)
"""

import json
import sys
import os
from typing import List, Optional, Dict

# Import acupoint data from locator
from acupoint_locator import ACUPOINT_DATA, generate_image_urls, find_acupoint


def load_symptom_database() -> Dict:
    """Load the symptom-to-acupoint mapping database"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, "DignoseSource", "acupressure_by_symptom.json")

    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def normalize_code(code: str) -> str:
    """Normalize acupoint code for lookup"""
    # Handle special cases
    code_upper = code.upper().replace(" ", "_")
    if code_upper == "AURICULAR_SHENMEN":
        return "AURICULAR_SHENMEN"
    return code_upper


def find_symptom(query: str, db: Dict) -> Optional[Dict]:
    """Find matching symptom entry"""
    query_lower = query.lower()

    for symptom_entry in db['symptoms']:
        symptom = symptom_entry['symptom'].lower()
        # Check if query matches any part of the symptom
        if query_lower in symptom or any(word in symptom for word in query_lower.split()):
            return symptom_entry

    return None


def diagnose(symptom_query: str) -> Dict:
    """
    Main diagnosis function.
    Input: symptom description (e.g., "low back pain", "headache", "nausea")
    Output: Dict with symptom info, recommended acupoints with full location details and images
    """
    db = load_symptom_database()

    # Find matching symptom
    symptom_entry = find_symptom(symptom_query, db)

    if not symptom_entry:
        return {
            "success": False,
            "error": f"No matching symptom found for: {symptom_query}",
            "available_symptoms": [s['symptom'] for s in db['symptoms']]
        }

    # Get detailed info for each recommended acupoint
    enriched_points = []
    for point in symptom_entry['points']:
        code = normalize_code(point['code'])

        # Get full acupoint data
        full_data = find_acupoint(code)

        if full_data:
            enriched_points.append({
                "code": point['code'],
                "name": point['name'],
                "chinese_name": full_data.get('chinese_name', ''),
                "meridian": point['meridian'],
                "basic_hint": point['location_hint'],
                "notes": point.get('notes', ''),
                # Detailed location from our database
                "standard_location": full_data.get('standard_location', ''),
                "standard_location_en": full_data.get('standard_location_en', ''),
                "simple_method": full_data.get('simple_method', ''),
                "simple_method_en": full_data.get('simple_method_en', ''),
                "anatomical": full_data.get('anatomical', ''),
                "caution": full_data.get('caution', ''),
                # Image sources
                "image_sources": full_data.get('image_sources', [])
            })
        else:
            # Fallback if we don't have detailed data
            enriched_points.append({
                "code": point['code'],
                "name": point['name'],
                "meridian": point['meridian'],
                "basic_hint": point['location_hint'],
                "notes": point.get('notes', ''),
                "image_sources": [
                    {
                        "name": "Google Images",
                        "url": f"https://www.google.com/search?tbm=isch&q={point['code']}+{point['name']}+acupoint+location",
                        "type": "image_search"
                    }
                ]
            })

    return {
        "success": True,
        "symptom": symptom_entry['symptom'],
        "sources": symptom_entry.get('sources', []),
        "acupoints": enriched_points,
        "disclaimer": db.get('disclaimer', 'For educational reference only.')
    }


def format_diagnosis(result: Dict) -> str:
    """Format diagnosis result for terminal display"""
    if not result['success']:
        output = [f"\n❌ {result['error']}\n"]
        output.append("Available symptoms:")
        for s in result['available_symptoms']:
            output.append(f"  • {s}")
        return "\n".join(output)

    output = []
    output.append(f"\n{'='*70}")
    output.append(f"🩺 症状诊断: {result['symptom']}")
    output.append(f"{'='*70}")

    for i, point in enumerate(result['acupoints'], 1):
        output.append(f"\n{'─'*70}")
        output.append(f"【穴位 {i}】{point['code']} - {point.get('chinese_name', '')} ({point['name']})")
        output.append(f"经络: {point['meridian']}")

        if point.get('caution'):
            output.append(f"⚠️  注意: {point['caution']}")

        output.append(f"\n📍 定位:")
        if point.get('standard_location'):
            output.append(f"   标准: {point['standard_location']}")
        if point.get('standard_location_en'):
            output.append(f"   EN: {point['standard_location_en']}")

        output.append(f"\n👆 简便取穴:")
        if point.get('simple_method'):
            output.append(f"   {point['simple_method']}")
        if point.get('simple_method_en'):
            output.append(f"   {point['simple_method_en']}")
        elif point.get('basic_hint'):
            output.append(f"   {point['basic_hint']}")

        if point.get('notes'):
            output.append(f"\n💡 提示: {point['notes']}")

        output.append(f"\n🖼️ 图片资源 (点击查看位置):")
        for j, src in enumerate(point.get('image_sources', [])[:5], 1):  # Show top 5
            output.append(f"   {j}. [{src['name']}] {src['url']}")

    output.append(f"\n{'='*70}")
    output.append(f"⚠️  {result['disclaimer']}")
    output.append(f"{'='*70}\n")

    return "\n".join(output)


def list_symptoms(db: Dict) -> str:
    """List all available symptoms"""
    output = ["\n📋 可查询症状列表:\n"]
    for i, s in enumerate(db['symptoms'], 1):
        output.append(f"  {i}. {s['symptom']}")
    return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python symptom_diagnosis.py <SYMPTOM>")
        print("       python symptom_diagnosis.py --list")
        print("\nExamples:")
        print("  python symptom_diagnosis.py 'low back pain'")
        print("  python symptom_diagnosis.py headache")
        print("  python symptom_diagnosis.py nausea")
        return

    query = sys.argv[1]

    if query == "--list":
        db = load_symptom_database()
        print(list_symptoms(db))
        return

    result = diagnose(query)
    print(format_diagnosis(result))

    # Save JSON output
    if result['success']:
        output_file = f"diagnosis_{query.replace(' ', '_').replace('/', '_')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON saved to: {output_file}")


if __name__ == "__main__":
    main()
