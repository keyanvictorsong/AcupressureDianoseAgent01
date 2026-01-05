App({
  globalData: {
    // API base URL - change to your cloud server URL when deployed
    apiBase: 'http://localhost:8080',
    // For WeChat cloud hosting, use:
    // apiBase: 'https://your-domain.com'
  },
  onLaunch() {
    console.log('穴位诊断助手启动');
  }
});
