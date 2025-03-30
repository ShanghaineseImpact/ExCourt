Page({
  data: {
    friends: [],
    searchId: '',
    student_id: '', // 当前用户学号，实际应用中从登录接口获取
  },
  onLoad() {
    wx.getStorage({key: 'student_id',success: (res) => {
      console.log('获取到学号:', res.data);
      this.setData({student_id: res.data});
      this.getFriends();
    },
    fail: () => {wx.showToast({title: '未登录或学号未找到',icon: 'none'});}});
  },
  // 输入学号
  onInput(e) {
    this.setData({ searchId: e.detail.value });
  },
  // 获取好友列表
  getFriends() {
    wx.showLoading({ title: '加载中...' });
    console.log(this.data.student_id)
    wx.request({
      url: 'http://123.60.86.239:8000/friend/getall', // 替换为你的后端实际地址
      method: 'POST',
      data: { student_id: this.data.student_id },
      header: {
        'content-type': 'application/json',
      },
      success: (res) => {
        wx.hideLoading();
        if (res.data.status === 'success') {
          this.setData({ friends: res.data.data });
        } else {
          wx.showToast({
            title: res.data.message || '获取好友失败',
            icon: 'none',
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        wx.showToast({
          title: '网络错误',
          icon: 'none',
        });
        console.error('获取好友列表失败:', err);
      },
    });
  },
  // 添加好友
  addFriend() {
    if (!this.data.searchId) {
      wx.showToast({
        title: '请输入好友学号',
        icon: 'none',
      });
      return;
    }
    wx.request({
      url: 'http://123.60.86.239:8000/student/find',
      method: 'POST',
      header: {
          'Content-Type': 'application/json',
      },
      data: {
          search_id: this.data.searchId,
      },
      success: (checkRes) => {
          if (checkRes.data.status === 'success') {
              // 学生存在，添加好友
              wx.showLoading({ title: '添加中...' });
              wx.request({
                url: 'http://123.60.86.239:8000/friend/add', // 替换为你的后端实际地址
                method: 'POST',
                data: { my_id: this.data.student_id, search_id: this.data.searchId },
                header: {
                  'content-type': 'application/json',
                },
                success: (res) => {
                  wx.hideLoading();
                  if (res.data.status === 'success') {
                    wx.showToast({ title: '添加好友成功', icon: 'success' });
                    this.setData({ searchId: '' });
                    this.getFriends();
                  } else {
                    wx.showToast({
                      title: res.data.message || '添加失败',
                      icon: 'none',
                    });
                  }
                },
                fail: (err) => {
                  wx.hideLoading();
                  wx.showToast({
                    title: '网络错误',
                    icon: 'none',
                  });
                  console.error('添加好友失败:', err);
                },
              });
          } else {
              // 学生不存在，提示用户
              wx.showToast({
                  title: '学生不存在，请检查学号',
                  icon: 'none',
              });
          }
      },
      fail: () => {
          wx.showToast({
              title: '检查学生请求失败',
              icon: 'none',
          });
      },
    });
  },
  // 删除好友
  deleteFriend(e) {
    const searchId = e.currentTarget.dataset.id;
    const myId = this.data.student_id;
    wx.showModal({
      title: '确认删除',
      content: '确定要删除该好友吗？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '删除中...' });
          wx.request({
            url: 'http://123.60.86.239:8000/friend/delete', // 替换为你的后端实际地址
            method: 'POST',
            data: { my_id: myId, search_id: searchId },
            header: {
              'content-type': 'application/json',
            },
            success: (res) => {
              wx.hideLoading();
              if (res.data.status === 'success') {
                wx.showToast({ title: '删除好友成功', icon: 'success' });
                this.getFriends();
              } else {
                wx.showToast({
                  title: res.data.message || '删除失败',
                  icon: 'none',
                });
              }
            },
            fail: (err) => {
              wx.hideLoading();
              wx.showToast({
                title: '网络错误',
                icon: 'none',
              });
              console.error('删除好友失败:', err);
            },
          });
        }
      },
    });
  },
  // 点击好友跳转到聊天页面
  goToConversation(e) {
    const receiverId = e.currentTarget.dataset.id; // 获取好友的学号
    const receiverName = e.currentTarget.dataset.name; // 获取好友昵称（可选）
    wx.navigateTo({
      url: `/pages/5-conversation/conversation?sender_id=${this.data.student_id}&receiver_id=${receiverId}&receiver_name=${receiverName}`,
    });
  },
});

