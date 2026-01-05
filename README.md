# 穴位诊断助手 (Acupressure Diagnosis Assistant)

基于中医穴位知识的智能诊断系统，用户描述症状后推荐相应穴位按摩方案并展示穴位位置图片。

## 功能特点

- **症状诊断**：输入症状关键词（头痛、失眠、腰痛等），获取穴位推荐
- **穴位图片**：每个穴位配有多张位置示意图，帮助用户准确找到穴位
- **零成本部署**：支持 GitHub Pages 纯静态托管，无需服务器
- **多端支持**：Web端 + 微信小程序 + ChatGPT插件

## 快速部署 (GitHub Pages - 免费)

**最简单的方式，零成本！**

1. Fork 或 clone 这个仓库
2. 运行 `python3 generate_static.py` 生成静态文件
3. 推送到 GitHub
4. 在 Settings > Pages 启用 GitHub Pages，选择 `docs/` 目录
5. 修改 `docs/.well-known/ai-plugin.json` 和 `docs/openapi.yaml` 中的域名为你的 GitHub Pages 地址

**示例：** `https://YOUR_USERNAME.github.io/YOUR_REPO/`

## 项目结构

```
├── docs/                      # 静态网站 (GitHub Pages)
│   ├── index.html             # 静态Web界面
│   ├── api/                   # 静态JSON API
│   │   ├── symptoms.json
│   │   ├── acupoints.json
│   │   ├── diagnose/*.json
│   │   └── images/*.json
│   ├── images/                # 穴位图片
│   └── .well-known/           # ChatGPT插件配置
│
├── src/                       # 动态API (可选)
│   ├── api.py                 # Flask API 服务器 (端口 8080)
│   ├── acupoint_locator.py    # 穴位数据库 (21个常用穴位)
│   ├── symptom_diagnosis.py   # 症状诊断逻辑
│   └── image_scraper.py       # 图片爬虫工具
│
├── web/
│   └── index.html             # 动态Web聊天界面
│
├── miniprogram/               # 微信小程序
│   ├── app.js / app.json / app.wxss
│   ├── project.config.json
│   └── pages/
│       ├── index/             # 主聊天页面
│       └── detail/            # 穴位详情页
│
├── DignoseSource/             # 数据源
│   ├── acupressure_by_symptom.json
│   ├── acupoint_images/
│   └── Chinese acuPointData/
│
└── generate_static.py         # 静态文件生成脚本
```

## 快速开始

### 1. 安装依赖

```bash
pip install flask flask-cors requests
```

### 2. 启动 API 服务

```bash
cd src
python api.py
```

服务启动于 http://localhost:8080

### 3. 访问 Web 界面

用浏览器打开 `web/index.html`，或用 VS Code Live Server 启动。

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/symptoms` | GET | 获取所有支持的症状列表 |
| `/diagnose/<symptom>` | GET | 根据症状获取穴位推荐 |
| `/acupoint/<code>` | GET | 获取穴位详情 (如 LI4, GB20) |
| `/acupoints` | GET | 获取所有穴位列表 |
| `/search?q=<query>` | GET | 搜索症状和穴位 |
| `/chat` | POST | 聊天式诊断 (支持自然语言) |
| `/images/<code>` | GET | 获取穴位图片列表 |

### 示例请求

```bash
# 聊天诊断
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "我头痛"}'

# 获取穴位图片
curl http://localhost:8080/images/LI4
```

## 微信小程序部署

1. 下载 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)

2. 注册小程序账号，获取 AppID
   - https://mp.weixin.qq.com

3. 修改配置
   - `miniprogram/project.config.json` 中替换 `appid`
   - `miniprogram/app.js` 中修改 `apiBase` 为你的服务器地址

4. 导入 `miniprogram/` 目录到开发者工具

5. 在小程序后台配置服务器域名（request 合法域名）

## ChatGPT 插件部署 (零成本)

使用 GitHub Pages 静态托管，无需服务器！

1. 按照「快速部署」步骤完成 GitHub Pages 设置
2. 修改 `docs/.well-known/ai-plugin.json` 中的域名
3. 修改 `docs/openapi.yaml` 中的 servers.url
4. 在 ChatGPT 插件商店提交审核

**示例配置：**
```json
// docs/.well-known/ai-plugin.json
{
  "api": {
    "url": "https://YOUR_USERNAME.github.io/YOUR_REPO/openapi.yaml"
  },
  "logo_url": "https://YOUR_USERNAME.github.io/YOUR_REPO/logo.png"
}
```

## 可选：动态 API 服务器

如需更多功能（自然语言处理、LLM分析），可以部署动态API：

```bash
pip install -r requirements.txt
cd src && python api.py
```

支持设置 `OPENAI_API_KEY` 或 `ANTHROPIC_API_KEY` 环境变量启用LLM智能分析。

## 数据来源

- 穴位数据：基于中医针灸学标准穴位
- 图片来源：iaees.org 及公开医学图片资源
- 症状映射：中医临床经验总结

## 支持的穴位

| 代码 | 中文名 | 主治 |
|------|--------|------|
| LI4 | 合谷 | 头痛、牙痛、感冒 |
| GB20 | 风池 | 头痛、颈椎病 |
| ST36 | 足三里 | 消化、增强体质 |
| SP6 | 三阴交 | 妇科、失眠 |
| PC6 | 内关 | 恶心、心悸 |
| HT7 | 神门 | 失眠、焦虑 |
| BL23 | 肾俞 | 腰痛、肾虚 |
| GB30 | 环跳 | 坐骨神经痛 |
| ... | ... | ... |

共 21 个常用穴位，详见 `src/acupoint_locator.py`

## 免责声明

本工具仅供健康参考，不能替代专业医疗诊断。如有严重症状请及时就医。

## License

MIT
