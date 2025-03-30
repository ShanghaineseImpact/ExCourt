// pages/4-misclaim/misclaim.js
// misclaim.js
Page({
  data: {
    itemName: '',
    description: '',
    contactInfo: ''
  },

  onInputChange(e) {
    const { field } = e.currentTarget.dataset;
    this.setData({
      [field]: e.detail.value
    });
  },

  submitMisclaim() {
    const { itemName, description, contactInfo } = this.data;

    if (!itemName || !contactInfo) {
      wx.showToast({
        title: '请填写必填项',
        icon: 'none'
      });
      return;
    }

    // 这里可以添加提交数据的逻辑，例如调用API
    wx.showToast({
      title: '申诉成功',
      icon: 'success'
    });

    // 重置表单
    this.setData({
      itemName: '',
      description: '',
      contactInfo: ''
    });
  }
});
