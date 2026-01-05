// pages/index/index.js
const app = getApp();

Page({
  data: {
    messages: [],
    inputValue: '',
    sending: false,
    scrollToView: 'bottom',
    messageId: 0,
    quickSymptoms: [
      { text: '头痛', query: '我头痛' },
      { text: '失眠', query: '我失眠睡不着' },
      { text: '焦虑', query: '我很焦虑紧张' },
      { text: '颈椎痛', query: '我脖子僵硬' },
      { text: '腰痛', query: '我腰疼' },
      { text: '恶心', query: '我恶心想吐' },
    ]
  },

  onLoad() {
    // 初始化
  },

  onInputChange(e) {
    this.setData({ inputValue: e.detail.value });
  },

  onQuickTap(e) {
    const query = e.currentTarget.dataset.query;
    this.setData({ inputValue: query });
    this.sendMessage();
  },

  async sendMessage() {
    const message = this.data.inputValue.trim();
    if (!message || this.data.sending) return;

    const msgId = this.data.messageId + 1;

    // 添加用户消息
    const userMsg = {
      id: msgId,
      isUser: true,
      content: message
    };

    // 添加加载消息
    const loadingMsg = {
      id: msgId + 1,
      isUser: false,
      type: 'loading'
    };

    this.setData({
      messages: [...this.data.messages, userMsg, loadingMsg],
      inputValue: '',
      sending: true,
      messageId: msgId + 1,
      scrollToView: `msg-${msgId + 1}`
    });

    try {
      // 调用API
      const res = await this.callChatAPI(message);

      // 移除加载消息，添加结果
      const messages = this.data.messages.filter(m => m.type !== 'loading');

      if (!res.success) {
        messages.push({
          id: this.data.messageId + 1,
          isUser: false,
          type: 'text',
          content: res.message || '抱歉，我没有找到匹配的症状。请试试：头痛、失眠、焦虑、腰痛、颈椎等关键词。'
        });
      } else {
        // 构建诊断结果消息
        const diagnosisMsg = {
          id: this.data.messageId + 1,
          isUser: false,
          type: 'diagnosis',
          title: '',
          llmResponse: '',
          acupoints: [],
          disclaimer: ''
        };

        if (res.mode === 'llm') {
          // LLM模式
          diagnosisMsg.llmResponse = res.llm_response;
          diagnosisMsg.acupoints = await this.loadAcupointImages(res.recommended_acupoints || []);
        } else {
          // 关键词匹配模式
          const diagnosis = res.diagnosis;
          diagnosisMsg.title = `针对「${diagnosis.symptom}」推荐以下穴位：`;
          diagnosisMsg.acupoints = await this.loadAcupointImages(diagnosis.acupoints || []);
          diagnosisMsg.disclaimer = diagnosis.disclaimer || '';
        }

        messages.push(diagnosisMsg);
      }

      this.setData({
        messages,
        messageId: this.data.messageId + 1,
        scrollToView: `msg-${this.data.messageId + 1}`
      });

    } catch (err) {
      console.error('API错误:', err);
      const messages = this.data.messages.filter(m => m.type !== 'loading');
      messages.push({
        id: this.data.messageId + 1,
        isUser: false,
        type: 'text',
        content: '无法连接服务器，请检查网络连接。'
      });
      this.setData({
        messages,
        messageId: this.data.messageId + 1
      });
    }

    this.setData({ sending: false });
  },

  callChatAPI(message) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.apiBase}/chat`,
        method: 'POST',
        header: { 'Content-Type': 'application/json' },
        data: { message },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data);
          } else {
            reject(new Error(`HTTP ${res.statusCode}`));
          }
        },
        fail: reject
      });
    });
  },

  async loadAcupointImages(acupoints) {
    const apiBase = app.globalData.apiBase;
    const results = [];

    for (const point of acupoints) {
      try {
        const imgRes = await this.getImages(point.code);
        results.push({
          ...point,
          images: (imgRes.images || []).slice(0, 6).map(img => `${apiBase}${img}`)
        });
      } catch (e) {
        console.error('加载图片失败:', e);
        results.push({ ...point, images: [] });
      }
    }

    return results;
  },

  getImages(code) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.apiBase}/images/${code}`,
        method: 'GET',
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data);
          } else {
            resolve({ images: [] });
          }
        },
        fail: () => resolve({ images: [] })
      });
    });
  },

  onImageTap(e) {
    const src = e.currentTarget.dataset.src;
    // 收集当前穴位的所有图片
    const allImages = [];
    this.data.messages.forEach(msg => {
      if (msg.acupoints) {
        msg.acupoints.forEach(point => {
          if (point.images) {
            allImages.push(...point.images);
          }
        });
      }
    });

    wx.previewImage({
      current: src,
      urls: allImages.length > 0 ? allImages : [src]
    });
  },

  onAcupointTap(e) {
    const point = e.currentTarget.dataset.point;
    // 可以跳转到详情页
    // wx.navigateTo({
    //   url: `/pages/detail/detail?code=${point.code}`
    // });
  }
});
