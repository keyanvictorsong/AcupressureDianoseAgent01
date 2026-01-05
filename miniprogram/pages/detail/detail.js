// pages/detail/detail.js
const app = getApp();

Page({
  data: {
    acupoint: {},
    images: []
  },

  onLoad(options) {
    const code = options.code;
    if (code) {
      this.loadAcupoint(code);
    }
  },

  async loadAcupoint(code) {
    const apiBase = app.globalData.apiBase;

    try {
      // 获取穴位详情
      const detailRes = await this.request(`${apiBase}/acupoint/${code}`);
      if (detailRes.success) {
        this.setData({ acupoint: detailRes.acupoint });
        wx.setNavigationBarTitle({ title: detailRes.acupoint.chinese_name || code });
      }

      // 获取图片
      const imgRes = await this.request(`${apiBase}/images/${code}`);
      if (imgRes.images) {
        this.setData({
          images: imgRes.images.map(img => `${apiBase}${img}`)
        });
      }
    } catch (e) {
      console.error('加载穴位详情失败:', e);
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  request(url) {
    return new Promise((resolve, reject) => {
      wx.request({
        url,
        success: res => resolve(res.data),
        fail: reject
      });
    });
  },

  onImageTap(e) {
    const src = e.currentTarget.dataset.src;
    wx.previewImage({
      current: src,
      urls: this.data.images
    });
  }
});
