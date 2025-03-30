Page({
  data: {
    applications: [] // 存储待处理申请列表
  },

  onLoad: function() {
    this.loadApplications();
  },

  // 加载待处理申请列表
  loadApplications: function() {
    // 假设从后端获取申请数据
    const applicationsData = [
      { id: 1, studentId: '123456', studentName: '张三' },
      { id: 2, studentId: '654321', studentName: '李四' }
      // 添加更多申请数据
    ];
    this.setData({ applications: applicationsData });
  },

  // 通过申请
  approveApplication: function(e) {
    const applicationId = e.currentTarget.dataset.id;
    this.sendDecision(applicationId, 'approve');
  },

  // 拒绝申请
  rejectApplication: function(e) {
    const applicationId = e.currentTarget.dataset.id;
    this.sendDecision(applicationId, 'reject');
  },

  // 发送处理决定
  sendDecision: function(applicationId, decision) {
    // 模拟发送请求，实际中应与后端交互
    wx.showToast({
      title: decision === 'approve' ? '已通过申请' : '已拒绝申请',
      icon: 'success',
      duration: 2000
    });

    // 从申请列表中移除已处理的申请
    this.removeApplication(applicationId);
  },

  // 移除申请
  removeApplication: function(applicationId) {
    const updatedApplications = this.data.applications.filter(item => item.id !== applicationId);
    this.setData({ applications: updatedApplications });
  },

  // 查看详情
  viewDetails: function(e) {
    const applicationId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/applicationDetails/applicationDetails?id=${applicationId}`
    });
  }
});
