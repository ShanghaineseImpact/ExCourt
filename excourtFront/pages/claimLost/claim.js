// pages/4-claim/claim.js
// claim.js
// claim.js
Page({
  data: {
    lostItems: [],
    selectedItem: null,
    reason: ''
  },

  onLoad() {
    // 模拟获取失物信息
    this.setData({
      lostItems: [
        { id: 1, name: '书包', description: '黑色书包，包含课本', lostTime: '2024-10-21', lostLocation: '图书馆' },
        { id: 2, name: '钥匙', description: '一串钥匙，带有卡片', lostTime: '2024-10-22', lostLocation: '教学楼' }
      ]
    });
  },

  selectItem(e) {
    const index = e.currentTarget.dataset.index;
    const selectedItem = this.data.lostItems[index];
    this.setData({ selectedItem });
  },

  onInputChange(e) {
    this.setData({
      reason: e.detail.value
    });
  },

  submitClaim() {
    const { selectedItem, reason } = this.data;

    if (!selectedItem) {
      wx.showToast({
        title: '请选择要认领的物品',
        icon: 'none'
      });
      return;
    }

    if (!reason) {
      wx.showToast({
        title: '请填写认领理由',
        icon: 'none'
      });
      return;
    }

    // 提交数据的逻辑，例如调用API
    wx.showToast({
      title: '认领请求已提交',
      icon: 'success'
    });

    // 清空理由和选中项
    this.setData({ reason: '', selectedItem: null });
  }
});

