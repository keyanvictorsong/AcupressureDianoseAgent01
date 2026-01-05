"""
Acupoint Locator - Find acupoint location info and images
Usage: python acupoint_locator.py GB30
"""

import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class AcupointLocation:
    code: str
    chinese_name: str
    english_name: str
    pinyin: str
    meridian: str

    # Location info
    standard_location: str
    simple_method: str
    anatomical: str

    # Clinical
    indications: List[str]
    functions: List[str]

    # Image resources
    image_sources: List[dict]

    # Reference sources
    sources: List[str]


# Reliable acupoint image sources (prioritized)
IMAGE_SOURCES = [
    {
        "name": "Yin Yang House",
        "url_pattern": "https://yinyanghouse.com/theory/acupuncturepoints/{code_lower}/",
        "type": "educational",
        "has_meridian_chart": True
    },
    {
        "name": "Acupuncture.com",
        "url_pattern": "https://www.acupuncture.com/education/points/{meridian_lower}/{code_lower}.htm",
        "type": "educational",
        "has_point_diagram": True
    },
    {
        "name": "MeandQi",
        "url_pattern": "https://www.meandqi.com/tcm-education-center/acupuncture/{meridian_lower}-channel/{name_lower}-{code_lower}",
        "type": "educational",
        "has_body_map": True
    },
    {
        "name": "Sacred Lotus",
        "url_pattern": "https://www.sacredlotus.com/go/acupuncture/point/{code_lower}-{pinyin_lower}",
        "type": "educational",
        "has_chart": True
    },
    {
        "name": "TCM Wiki",
        "url_pattern": "https://tcmwiki.com/wiki/{code_lower}",
        "type": "reference",
        "has_images": True
    },
    {
        "name": "Iaomai App (3D)",
        "url_pattern": "https://www.iaomai.app/en/acupuncture-points/{code}-{pinyin_lower}",
        "type": "3d_visualization",
        "has_3d_model": True
    },
    {
        "name": "百度百科",
        "url_pattern": "https://baike.baidu.com/item/{chinese_name}穴",
        "type": "chinese_reference",
        "has_images": True
    },
    {
        "name": "经络穴位网",
        "url_pattern": "http://m.jingluoxuewei.com/search?q={chinese_name}",
        "type": "chinese_educational",
        "has_diagrams": True
    },
    {
        "name": "ResearchGate (Scientific)",
        "url_pattern": "https://www.researchgate.net/search?q={code}+acupoint+location",
        "type": "scientific",
        "has_anatomical_diagrams": True
    },
    {
        "name": "Google Images",
        "url_pattern": "https://www.google.com/search?tbm=isch&q={code}+{english_name}+acupoint+location",
        "type": "image_search",
        "has_multiple_images": True
    }
]


# Sample acupoint data (to be expanded)
ACUPOINT_DATA = {
    "GB30": {
        "code": "GB30",
        "chinese_name": "环跳",
        "english_name": "Huantiao",
        "pinyin": "huantiao",
        "meridian": "Gallbladder",
        "meridian_chinese": "足少阳胆经",
        "standard_location": "在臀部外侧，侧卧屈髋，在股骨大转子最凸点与骶管裂孔连线的外侧1/3与内侧2/3交点上",
        "standard_location_en": "At the junction of the lateral 1/3 and medial 2/3 of the line connecting the prominence of the greater trochanter and the sacral hiatus, with patient in lateral recumbent position with thigh flexed",
        "simple_method": "侧卧屈腿，以拇指关节横纹按在股骨大转子上，拇指指向脊柱，拇指尖所指的凹陷处即是本穴",
        "simple_method_en": "Lie on side with knee bent. Place thumb knuckle on greater trochanter, point thumb toward spine. The depression at thumb tip is the point.",
        "anatomical": "臀大肌深层，坐骨神经和股方肌；有臀下动静脉，深层有坐骨神经",
        "indications": [
            "腰腿痹痛 (low back and leg pain)",
            "下肢痿痹 (lower limb weakness/paralysis)",
            "半身不遂 (hemiplegia)",
            "坐骨神经痛 (sciatica)",
            "髋关节疾患 (hip joint disorders)"
        ],
        "functions": [
            "强健腰膝 (strengthen lumbar and knees)",
            "舒经活络 (unblock meridians)",
            "活血止痛 (promote blood circulation, relieve pain)"
        ]
    },
    "BL23": {
        "code": "BL23",
        "chinese_name": "肾俞",
        "english_name": "Shenshu",
        "pinyin": "shenshu",
        "meridian": "Bladder",
        "meridian_chinese": "足太阳膀胱经",
        "standard_location": "在腰部，当第2腰椎棘突下，旁开1.5寸",
        "standard_location_en": "On the lower back, 1.5 cun lateral to the lower border of the spinous process of the 2nd lumbar vertebra (L2)",
        "simple_method": "俯卧，在第二腰椎棘突下（与肚脐水平），旁开约两横指处",
        "simple_method_en": "Prone position. Find L2 spinous process (level with navel), then 2 finger-widths lateral to it.",
        "anatomical": "腰背筋膜，最长肌；有第2腰动静脉后支，深层为腰丛",
        "indications": [
            "腰痛 (low back pain)",
            "肾虚腰酸 (kidney deficiency back soreness)",
            "遗精阳痿 (seminal emission, impotence)",
            "月经不调 (irregular menstruation)",
            "耳鸣耳聋 (tinnitus, deafness)"
        ],
        "functions": [
            "补肾益精 (tonify kidney, benefit essence)",
            "强腰壮骨 (strengthen lumbar and bones)",
            "温阳利水 (warm yang, promote urination)"
        ]
    },
    "BL40": {
        "code": "BL40",
        "chinese_name": "委中",
        "english_name": "Weizhong",
        "pinyin": "weizhong",
        "meridian": "Bladder",
        "meridian_chinese": "足太阳膀胱经",
        "standard_location": "在膝后区，腘横纹中点，股二头肌腱与半腱肌腱之间",
        "standard_location_en": "At the midpoint of the popliteal crease, between the tendons of biceps femoris and semitendinosus",
        "simple_method": "屈膝，在膝盖后面横纹的正中央凹陷处",
        "simple_method_en": "Bend knee. Find the center of the crease behind the knee.",
        "anatomical": "腘窝中央，有腘动静脉，深层为腘静脉；布有股后皮神经，胫神经",
        "indications": [
            "腰背痛 (low back pain)",
            "下肢痿痹 (lower limb weakness)",
            "腹痛吐泻 (abdominal pain, vomiting, diarrhea)",
            "中暑 (heatstroke)",
            "丹毒 (erysipelas)"
        ],
        "functions": [
            "舒筋活络 (relax sinews, activate collaterals)",
            "清热解毒 (clear heat, resolve toxins)",
            "强腰健膝 (strengthen lumbar and knees)"
        ]
    },
    "BL60": {
        "code": "BL60",
        "chinese_name": "昆仑",
        "english_name": "Kunlun",
        "pinyin": "kunlun",
        "meridian": "Bladder",
        "meridian_chinese": "足太阳膀胱经",
        "standard_location": "在踝区，外踝尖与跟腱之间的凹陷中",
        "standard_location_en": "In the depression between the tip of the lateral malleolus and the Achilles tendon",
        "simple_method": "外脚踝骨最高点与跟腱之间的凹陷处",
        "simple_method_en": "Find the hollow between the outer ankle bone and the Achilles tendon.",
        "anatomical": "有腓骨短肌，小隐静脉及腓肠神经",
        "indications": [
            "头痛项强 (headache, neck stiffness)",
            "腰骶痛 (lumbosacral pain)",
            "踝关节痛 (ankle pain)",
            "坐骨神经痛 (sciatica)",
            "难产 (difficult labor)"
        ],
        "functions": [
            "舒筋活络 (relax sinews, activate collaterals)",
            "散风清热 (dispel wind, clear heat)",
            "安神定志 (calm spirit)"
        ]
    },
    "KI3": {
        "code": "KI3",
        "chinese_name": "太溪",
        "english_name": "Taixi",
        "pinyin": "taixi",
        "meridian": "Kidney",
        "meridian_chinese": "足少阴肾经",
        "standard_location": "在踝区，内踝尖与跟腱之间的凹陷中",
        "standard_location_en": "In the depression between the tip of the medial malleolus and the Achilles tendon",
        "simple_method": "内脚踝骨最高点与跟腱之间的凹陷处",
        "simple_method_en": "Find the hollow between the inner ankle bone and the Achilles tendon.",
        "anatomical": "有胫后动脉，胫神经",
        "indications": [
            "肾虚腰痛 (kidney deficiency back pain)",
            "头晕耳鸣 (dizziness, tinnitus)",
            "失眠多梦 (insomnia, excessive dreaming)",
            "咽喉肿痛 (sore throat)",
            "月经不调 (irregular menstruation)"
        ],
        "functions": [
            "滋阴益肾 (nourish yin, benefit kidney)",
            "清热降火 (clear heat, reduce fire)",
            "强腰壮骨 (strengthen lumbar and bones)"
        ]
    },
    "LI4": {
        "code": "LI4",
        "chinese_name": "合谷",
        "english_name": "Hegu",
        "pinyin": "hegu",
        "meridian": "Large Intestine",
        "meridian_chinese": "手阳明大肠经",
        "standard_location": "在手背，第1、2掌骨间，当第2掌骨桡侧的中点处",
        "standard_location_en": "On the dorsum of the hand, between the 1st and 2nd metacarpal bones, at the midpoint of the 2nd metacarpal bone on the radial side",
        "simple_method": "拇指、食指并拢，虎口处肌肉隆起最高点",
        "simple_method_en": "Press thumb and index finger together. The point is at the highest bulge of muscle in the web space.",
        "anatomical": "第一骨间背侧肌中；有手背静脉网，桡动脉从手背穿向手掌；布有桡神经浅支",
        "indications": [
            "头痛 (headache)",
            "牙痛 (toothache)",
            "咽喉肿痛 (sore throat)",
            "感冒发热 (cold and fever)",
            "腹痛便秘 (abdominal pain, constipation)"
        ],
        "functions": [
            "疏风解表 (dispel wind, release exterior)",
            "通经活络 (unblock meridians)",
            "镇静止痛 (calm and relieve pain)"
        ],
        "caution": "孕妇禁用 (Contraindicated in pregnancy)"
    },
    "LV3": {
        "code": "LV3",
        "chinese_name": "太冲",
        "english_name": "Taichong",
        "pinyin": "taichong",
        "meridian": "Liver",
        "meridian_chinese": "足厥阴肝经",
        "standard_location": "在足背，当第1、2跖骨结合部之前凹陷中",
        "standard_location_en": "On the dorsum of the foot, in the depression proximal to the 1st metatarsal space",
        "simple_method": "足背第一、二趾骨之间，往脚踝方向推，推到两骨交汇处的凹陷",
        "simple_method_en": "On top of foot between big toe and 2nd toe. Slide finger toward ankle until you feel a depression where the bones meet.",
        "anatomical": "第一跖骨间隙的背侧；有足背静脉网，第一跖背动脉；布有腓深神经",
        "indications": [
            "头痛眩晕 (headache, dizziness)",
            "目赤肿痛 (red swollen eyes)",
            "胁痛 (hypochondriac pain)",
            "月经不调 (irregular menstruation)",
            "情志抑郁 (emotional depression)"
        ],
        "functions": [
            "疏肝理气 (soothe liver, regulate qi)",
            "平肝熄风 (calm liver, extinguish wind)",
            "清热利湿 (clear heat, drain dampness)"
        ]
    },
    "PC6": {
        "code": "PC6",
        "chinese_name": "内关",
        "english_name": "Neiguan",
        "pinyin": "neiguan",
        "meridian": "Pericardium",
        "meridian_chinese": "手厥阴心包经",
        "standard_location": "在前臂掌侧，当曲泽与大陵的连线上，腕横纹上2寸，掌长肌腱与桡侧腕屈肌腱之间",
        "standard_location_en": "On the palmar side of the forearm, 2 cun above the wrist crease, between the tendons of palmaris longus and flexor carpi radialis",
        "simple_method": "手腕横纹向上三横指（2寸），两筋之间",
        "simple_method_en": "Three finger-widths above wrist crease, between the two tendons in the center of the inner forearm.",
        "anatomical": "在掌长肌腱与桡侧腕屈肌腱之间；有前臂正中动静脉，深层为前臂掌侧骨间动静脉；布有前臂内侧皮神经，正中神经",
        "indications": [
            "心悸 (palpitations)",
            "胸闷 (chest oppression)",
            "恶心呕吐 (nausea, vomiting)",
            "失眠 (insomnia)",
            "晕车晕船 (motion sickness)"
        ],
        "functions": [
            "宁心安神 (calm heart, tranquilize spirit)",
            "理气止痛 (regulate qi, relieve pain)",
            "和胃降逆 (harmonize stomach, descend rebellious qi)"
        ]
    },
    "ST36": {
        "code": "ST36",
        "chinese_name": "足三里",
        "english_name": "Zusanli",
        "pinyin": "zusanli",
        "meridian": "Stomach",
        "meridian_chinese": "足阳明胃经",
        "standard_location": "在小腿前外侧，当犊鼻下3寸，距胫骨前缘一横指",
        "standard_location_en": "On the anterior lateral side of the leg, 3 cun below ST35 (Dubi), one finger-breadth lateral to the anterior crest of the tibia",
        "simple_method": "膝盖外侧凹陷（外膝眼）下四横指，胫骨外侧一横指处",
        "simple_method_en": "Four finger-widths below the outer knee depression, one finger-width lateral to the shin bone.",
        "anatomical": "在胫骨前肌，趾长伸肌之间；有胫前动静脉；布有腓肠外侧皮神经及隐神经的皮支，深层为腓深神经",
        "indications": [
            "胃痛 (stomach pain)",
            "消化不良 (indigestion)",
            "腹泻便秘 (diarrhea, constipation)",
            "虚劳乏力 (fatigue, weakness)",
            "下肢���痹 (lower limb weakness)"
        ],
        "functions": [
            "健脾和胃 (strengthen spleen, harmonize stomach)",
            "扶正培元 (support upright qi, cultivate source)",
            "通经活络 (unblock meridians)"
        ]
    },
    "SP6": {
        "code": "SP6",
        "chinese_name": "三阴交",
        "english_name": "Sanyinjiao",
        "pinyin": "sanyinjiao",
        "meridian": "Spleen",
        "meridian_chinese": "足太阴脾经",
        "standard_location": "在小腿内侧，当足内踝尖上3寸，胫骨内侧缘后方",
        "standard_location_en": "On the medial side of the lower leg, 3 cun above the tip of the medial malleolus, posterior to the medial border of the tibia",
        "simple_method": "内踝尖向上四横指（3寸），胫骨后缘凹陷处",
        "simple_method_en": "Four finger-widths above the inner ankle bone, just behind the shin bone.",
        "anatomical": "在胫骨后缘和比目鱼肌之间；有大隐静脉，胫后动静脉；布有小腿内侧皮神经，深层后方有胫神经",
        "indications": [
            "月经不调 (irregular menstruation)",
            "痛经 (dysmenorrhea)",
            "失眠 (insomnia)",
            "消化不良 (indigestion)",
            "下肢痿痹 (lower limb weakness)"
        ],
        "functions": [
            "健脾化湿 (strengthen spleen, transform dampness)",
            "调经止带 (regulate menstruation)",
            "滋阴补肾 (nourish yin, tonify kidney)"
        ],
        "caution": "孕妇慎用 (Use with caution in pregnancy)"
    },
    "SP4": {
        "code": "SP4",
        "chinese_name": "公孙",
        "english_name": "Gongsun",
        "pinyin": "gongsun",
        "meridian": "Spleen",
        "meridian_chinese": "足太阴脾经",
        "standard_location": "在足内侧缘，当第一跖骨基底部的前下方",
        "standard_location_en": "On the medial side of the foot, in the depression distal and inferior to the base of the 1st metatarsal bone",
        "simple_method": "足大趾内侧，沿足弓向后摸到第一跖骨底部隆起，其前下方凹陷处",
        "simple_method_en": "On inner edge of foot, find the bump at base of big toe bone, then slightly forward and down into the depression.",
        "anatomical": "在拇展肌中；有足背静脉网，跗内侧动脉分支；布有隐神经及腓浅神经分支",
        "indications": [
            "胃痛 (stomach pain)",
            "呕吐 (vomiting)",
            "腹胀 (abdominal distension)",
            "泄泻 (diarrhea)",
            "心烦失眠 (irritability, insomnia)"
        ],
        "functions": [
            "健脾和胃 (strengthen spleen, harmonize stomach)",
            "理气止痛 (regulate qi, relieve pain)",
            "通调冲脉 (regulate Chong vessel)"
        ]
    },
    "HT7": {
        "code": "HT7",
        "chinese_name": "神门",
        "english_name": "Shenmen",
        "pinyin": "shenmen",
        "meridian": "Heart",
        "meridian_chinese": "手少阴心经",
        "standard_location": "在腕部，腕掌侧横纹尺侧端，尺侧腕屈肌腱的桡侧凹陷处",
        "standard_location_en": "At the wrist, on the ulnar end of the transverse crease, in the depression on the radial side of the flexor carpi ulnaris tendon",
        "simple_method": "手腕横纹小指侧，小指侧大筋（尺侧腕屈肌腱）靠拇指侧的凹陷中",
        "simple_method_en": "At wrist crease on pinky side, find the big tendon, then feel the depression just toward the thumb side of it.",
        "anatomical": "在尺侧腕屈肌腱与指浅屈肌之间；有尺动脉；布有前臂内侧皮神经，尺神经",
        "indications": [
            "心悸怔忡 (palpitations)",
            "失眠健忘 (insomnia, poor memory)",
            "癫狂 (mania)",
            "心痛 (heart pain)",
            "焦虑烦躁 (anxiety, irritability)"
        ],
        "functions": [
            "宁心安神 (calm heart, tranquilize spirit)",
            "清心火 (clear heart fire)",
            "通络止痛 (unblock collaterals, relieve pain)"
        ]
    },
    "KI1": {
        "code": "KI1",
        "chinese_name": "涌泉",
        "english_name": "Yongquan",
        "pinyin": "yongquan",
        "meridian": "Kidney",
        "meridian_chinese": "足少阴肾经",
        "standard_location": "在足底部，卷足时足前部凹陷处，约当足底第2、3跖趾缝纹头端与足跟连线的前1/3与后2/3交点上",
        "standard_location_en": "On the sole, in the depression when the foot is in plantar flexion, at the junction of the anterior 1/3 and posterior 2/3 of the line connecting the base of the 2nd and 3rd toes and the heel",
        "simple_method": "脚掌前部凹陷处，脚趾弯曲时出现的人字形纹路交点",
        "simple_method_en": "Curl your toes. The point is in the depression that forms on the sole, at the crease shaped like an inverted V.",
        "anatomical": "有趾短屈肌，趾长屈肌腱，第二蚓状肌；有足底动脉弓，足底内侧动脉；布有足底内侧神经支",
        "indications": [
            "头痛头晕 (headache, dizziness)",
            "失眠 (insomnia)",
            "癫狂 (mania)",
            "中暑 (heatstroke)",
            "小儿惊风 (infantile convulsions)"
        ],
        "functions": [
            "滋阴降火 (nourish yin, reduce fire)",
            "开窍宁神 (open orifices, calm spirit)",
            "回阳救逆 (restore yang, rescue from collapse)"
        ]
    },
    "GB20": {
        "code": "GB20",
        "chinese_name": "风池",
        "english_name": "Fengchi",
        "pinyin": "fengchi",
        "meridian": "Gallbladder",
        "meridian_chinese": "足少阳胆经",
        "standard_location": "在项部，当枕骨之下，与风府相平，胸锁乳突肌与斜方肌上端之间的凹陷中",
        "standard_location_en": "At the nape, below the occipital bone, in the depression between the upper portion of sternocleidomastoid and trapezius muscles",
        "simple_method": "后脑勺下方，颈后两侧大筋外侧的凹陷处，与耳垂齐平",
        "simple_method_en": "At the base of skull, in the hollows on either side of the two big neck tendons, level with the earlobes.",
        "anatomical": "在胸锁乳突肌与斜方肌上端附着部之间的凹陷中；有枕动静脉分支；布有枕小神经分支",
        "indications": [
            "头痛 (headache)",
            "颈项强痛 (neck stiffness and pain)",
            "目赤肿痛 (red swollen eyes)",
            "感冒 (common cold)",
            "眩晕 (dizziness)"
        ],
        "functions": [
            "疏风清热 (dispel wind, clear heat)",
            "明目聪耳 (brighten eyes, sharpen hearing)",
            "通络止痛 (unblock collaterals, relieve pain)"
        ]
    },
    "GB21": {
        "code": "GB21",
        "chinese_name": "肩井",
        "english_name": "Jianjing",
        "pinyin": "jianjing",
        "meridian": "Gallbladder",
        "meridian_chinese": "足少阳胆经",
        "standard_location": "在肩上，前直乳中，当大椎与肩峰端连线的中点上",
        "standard_location_en": "On the shoulder, directly above the nipple, at the midpoint of the line connecting Dazhui (GV14) and the acromion",
        "simple_method": "肩膀最高点，大椎穴与肩峰连线的中点，按压有酸胀感",
        "simple_method_en": "At the highest point of the shoulder, midway between the neck and the shoulder tip. Press and feel soreness.",
        "anatomical": "在斜方肌上缘中部；有颈横动静脉分支；布有锁骨上神经后支，副神经",
        "indications": [
            "肩背痛 (shoulder and back pain)",
            "颈项强痛 (neck stiffness)",
            "头痛 (headache)",
            "乳痈 (mastitis)",
            "难产 (difficult labor)"
        ],
        "functions": [
            "疏通经络 (unblock meridians)",
            "活血化瘀 (promote blood circulation)",
            "消肿散结 (reduce swelling, dissipate masses)"
        ],
        "caution": "孕妇禁用 (Contraindicated in pregnancy)"
    },
    "SI3": {
        "code": "SI3",
        "chinese_name": "后溪",
        "english_name": "Houxi",
        "pinyin": "houxi",
        "meridian": "Small Intestine",
        "meridian_chinese": "手太阳小肠经",
        "standard_location": "在手掌尺侧，微握拳，当小指本节（第5掌指关节）后的远侧掌横纹头赤白肉际",
        "standard_location_en": "On the ulnar side of the hand, proximal to the 5th metacarpophalangeal joint, at the end of the transverse crease, at the junction of the red and white skin",
        "simple_method": "握拳，小指根部关节后方，掌纹尽头处，红白肉交界处",
        "simple_method_en": "Make a loose fist. Find the point at the end of the crease just below the pinky knuckle, where palm skin meets back-of-hand skin.",
        "anatomical": "在小指展肌起点外缘；有指背动静脉，手背静脉网；布有尺神经手背支",
        "indications": [
            "头项强痛 (headache, neck stiffness)",
            "目赤 (red eyes)",
            "耳聋 (deafness)",
            "咽喉肿痛 (sore throat)",
            "腰背痛 (low back pain)"
        ],
        "functions": [
            "疏风清热 (dispel wind, clear heat)",
            "通督脉 (regulate Du vessel)",
            "舒筋活络 (relax sinews, activate collaterals)"
        ]
    },
    "SJ5": {
        "code": "SJ5",
        "chinese_name": "外关",
        "english_name": "Waiguan",
        "pinyin": "waiguan",
        "meridian": "San Jiao",
        "meridian_chinese": "手少阳三焦经",
        "standard_location": "在前臂背侧，当阳池与肘尖的连线上，腕背横纹上2寸，尺骨与桡骨之间",
        "standard_location_en": "On the dorsal side of the forearm, 2 cun above the dorsal wrist crease, between the ulna and radius",
        "simple_method": "手腕背面横纹向上三横指（2寸），两骨之间",
        "simple_method_en": "Three finger-widths above the back of the wrist crease, between the two forearm bones.",
        "anatomical": "在指总伸肌与拇长伸肌之间；有前臂背侧骨间动静脉；布有前臂背侧皮神经，深层为前臂骨间背侧神经",
        "indications": [
            "热病 (febrile diseases)",
            "头痛 (headache)",
            "目赤肿痛 (red swollen eyes)",
            "耳鸣耳聋 (tinnitus, deafness)",
            "肩臂痛 (shoulder and arm pain)"
        ],
        "functions": [
            "清热解毒 (clear heat, resolve toxins)",
            "疏风通络 (dispel wind, unblock collaterals)",
            "开窍聪耳 (open orifices, sharpen hearing)"
        ]
    },
    "BL2": {
        "code": "BL2",
        "chinese_name": "攒竹",
        "english_name": "Zanzhu",
        "pinyin": "zanzhu",
        "meridian": "Bladder",
        "meridian_chinese": "足太阳膀胱经",
        "standard_location": "在面部，当眉头陷中，眶上切迹处",
        "standard_location_en": "On the face, in the depression at the medial end of the eyebrow, at the supraorbital notch",
        "simple_method": "眉毛内侧端，眉头凹陷处",
        "simple_method_en": "At the inner end of the eyebrow, in the small depression.",
        "anatomical": "有额肌及皱眉肌；有额动静脉；布有额神经内侧支",
        "indications": [
            "头痛 (headache)",
            "眉棱骨痛 (supraorbital pain)",
            "目视不明 (blurred vision)",
            "流泪 (tearing)",
            "眼睑动 (eyelid twitching)"
        ],
        "functions": [
            "祛风明目 (dispel wind, brighten eyes)",
            "清热止痛 (clear heat, relieve pain)"
        ]
    },
    "EX-HN3": {
        "code": "EX-HN3",
        "chinese_name": "印堂",
        "english_name": "Yintang",
        "pinyin": "yintang",
        "meridian": "Extra",
        "meridian_chinese": "经外奇穴",
        "standard_location": "在额部，当两眉头之中间",
        "standard_location_en": "On the forehead, at the midpoint between the two eyebrows",
        "simple_method": "两眉头连线的正中点",
        "simple_method_en": "Exactly midway between the inner ends of the eyebrows.",
        "anatomical": "在降眉间肌中；有额动静脉分支；布有滑车上神经分支",
        "indications": [
            "头痛 (headache)",
            "眩晕 (dizziness)",
            "鼻渊 (nasal congestion)",
            "失眠 (insomnia)",
            "小儿惊风 (infantile convulsions)"
        ],
        "functions": [
            "清头明目 (clear head, brighten eyes)",
            "通鼻开窍 (unblock nose, open orifices)",
            "宁心安神 (calm heart, tranquilize spirit)"
        ]
    },
    "EX-HN5": {
        "code": "EX-HN5",
        "chinese_name": "太阳",
        "english_name": "Taiyang",
        "pinyin": "taiyang",
        "meridian": "Extra",
        "meridian_chinese": "经外奇穴",
        "standard_location": "在颞部，当眉梢与目外眦之间，向后约一横指的凹陷处",
        "standard_location_en": "In the temporal region, in the depression about one finger-breadth posterior to the midpoint between the lateral end of the eyebrow and the outer canthus",
        "simple_method": "眉梢和眼角中间，向后一横指的凹陷（太阳穴）",
        "simple_method_en": "In the temple area: find the point between eyebrow tip and outer eye corner, then one finger-width back into the depression.",
        "anatomical": "在颞筋膜和颞肌之间；有颞浅动静脉；布有耳颞神经及面神经的颧支",
        "indications": [
            "头痛 (headache)",
            "偏头痛 (migraine)",
            "目赤肿痛 (red swollen eyes)",
            "目眩 (dizziness)",
            "牙痛 (toothache)"
        ],
        "functions": [
            "清肝明目 (clear liver, brighten eyes)",
            "疏风止痛 (dispel wind, relieve pain)"
        ]
    },
    "AURICULAR_SHENMEN": {
        "code": "Auricular Shenmen",
        "chinese_name": "耳神门",
        "english_name": "Ear Shenmen",
        "pinyin": "ershenmen",
        "meridian": "Auricular",
        "meridian_chinese": "耳穴",
        "standard_location": "在耳轮脚分叉处稍上方的三角窝内",
        "standard_location_en": "In the triangular fossa of the ear, at the apex of the triangular fossa, slightly above where the helix crus bifurcates",
        "simple_method": "耳朵上方三角形凹陷区域的顶端",
        "simple_method_en": "In the upper triangular hollow of the ear, at its apex.",
        "anatomical": "耳廓软骨，耳大神经分布区",
        "indications": [
            "失眠 (insomnia)",
            "多梦 (excessive dreaming)",
            "焦虑 (anxiety)",
            "高血压 (hypertension)",
            "戒断症状 (withdrawal symptoms)"
        ],
        "functions": [
            "镇静安神 (sedate and calm spirit)",
            "止痛 (relieve pain)",
            "抗过敏 (anti-allergic)"
        ]
    }
}


def generate_image_urls(acupoint_data: dict) -> List[dict]:
    """Generate image source URLs for an acupoint"""
    code = acupoint_data["code"]
    chinese_name = acupoint_data["chinese_name"]
    english_name = acupoint_data["english_name"]
    pinyin = acupoint_data["pinyin"]
    meridian = acupoint_data["meridian"]

    urls = []
    for source in IMAGE_SOURCES:
        try:
            url = source["url_pattern"].format(
                code=code,
                code_lower=code.lower(),
                chinese_name=chinese_name,
                english_name=english_name,
                name_lower=english_name.lower(),
                pinyin_lower=pinyin.lower(),
                meridian_lower=meridian.lower().replace(" ", "-")
            )
            urls.append({
                "name": source["name"],
                "url": url,
                "type": source["type"]
            })
        except KeyError:
            continue

    return urls


def find_acupoint(code: str) -> Optional[dict]:
    """Find acupoint information and generate image URLs"""
    code_upper = code.upper()

    if code_upper not in ACUPOINT_DATA:
        return None

    data = ACUPOINT_DATA[code_upper]
    image_urls = generate_image_urls(data)

    result = {
        **data,
        "image_sources": image_urls
    }

    return result


def format_output(acupoint: dict) -> str:
    """Format acupoint info for display"""
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"穴位: {acupoint['code']} - {acupoint['chinese_name']} ({acupoint['english_name']})")
    output.append(f"经络: {acupoint['meridian_chinese']} ({acupoint['meridian']})")
    output.append(f"{'='*60}")

    output.append(f"\n📍 标准定位:")
    output.append(f"   {acupoint['standard_location']}")
    output.append(f"   {acupoint['standard_location_en']}")

    output.append(f"\n👆 简便取穴法:")
    output.append(f"   {acupoint['simple_method']}")
    output.append(f"   {acupoint['simple_method_en']}")

    output.append(f"\n🔬 解剖位置:")
    output.append(f"   {acupoint['anatomical']}")

    output.append(f"\n💊 主治 (Indications):")
    for ind in acupoint['indications']:
        output.append(f"   • {ind}")

    output.append(f"\n⚡ 功效 (Functions):")
    for func in acupoint['functions']:
        output.append(f"   • {func}")

    output.append(f"\n🖼️ 图片资源 (Image Sources):")
    for i, src in enumerate(acupoint['image_sources'], 1):
        output.append(f"   {i}. [{src['name']}] ({src['type']})")
        output.append(f"      {src['url']}")

    return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python acupoint_locator.py <ACUPOINT_CODE>")
        print("Example: python acupoint_locator.py GB30")
        print("\nAvailable acupoints:", ", ".join(ACUPOINT_DATA.keys()))
        return

    code = sys.argv[1]
    result = find_acupoint(code)

    if result:
        print(format_output(result))

        # Also save to JSON
        output_file = f"acupoint_{code.upper()}_info.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ JSON saved to: {output_file}")
    else:
        print(f"❌ Acupoint '{code}' not found in database.")
        print(f"Available: {', '.join(ACUPOINT_DATA.keys())}")


if __name__ == "__main__":
    main()
