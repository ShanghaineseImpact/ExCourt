Page({
  data: {
    Student_id: '',
    joinCourtRequests: [], // 保存拼场申请的记录
  },

  onLoad: function() {
    wx.getStorage({
      key: 'student_id',
      success: (res) => {
        this.setData({ Student_id: res.data });
        this.loadJoinCourtRequests();
      },
      fail: () => {
        wx.showToast({
          title: '未登录或学号未找到',
          icon: 'none'
        });
      }
    });
  },

  loadJoinCourtRequests: function () {
    if (!this.data.Student_id) {
      wx.showToast({
        title: '用户ID不存在',
        icon: 'none'
      });
      return;
    }
  
    wx.request({
      url: 'http://123.60.86.239:8000/teamup/get_records', // 调用 /get_records 接口
      method: 'POST',
      data: { Student_id: this.data.Student_id },
      success: (res) => {
        if (res.data.status === 'success') {
          // 展平数组，将嵌套的数组结构展平成一个统一的数组
          const flattenedRecords = res.data.data.flat(); 
  
          // 映射数据为前端需要的格式
          const requests = flattenedRecords.map((item) => {
            // item 格式: [id, requester_id, uploader_id, court_id, state]
            const [id, requester_id, uploader_id, court_id, state] = item;
  
            // 根据状态设置颜色
            let statusColor = '#FFFFFF'; // 默认白色
            if (state === 'responsed') {
              statusColor = '#D4EDDA'; // 绿色
            } else if (state === 'retrieved') {
              statusColor = '#F8D7DA'; // 红色
            } else if (state === 'not_responsed') {
              statusColor = '#FFF3CD'; // 黄色
            }
  
            return {
              id, // 唯一标识
              Teamup_requester_id: requester_id,
              Teamup_uploader_id: uploader_id,
              Teamup_court_id: court_id,
              state,
              statusColor, // 添加状态颜色
              showOptions: false, // 默认隐藏操作按钮
            };
          });
  
          this.setData({
            joinCourtRequests: requests,
          });
        } else {
          wx.showToast({
            title: res.data.message || '没有找到拼场申请记录',
            icon: 'none',
          });
        }
      },
      fail: (err) => {
        console.error('Request failed:', err);
        wx.showToast({
          title: '请求失败，请稍后重试',
          icon: 'none',
        });
      },
    });
  },
  

  // 显示或隐藏操作按钮
  toggleOptions: function(e) {
    console.log(e.currentTarget.dataset)
    const id = e.currentTarget.dataset.id;
    const responser = e.currentTarget.dataset.responser
    const updatedRequests = this.data.joinCourtRequests.map(item => {
      if (item.Teamup_court_id === id && item.Teamup_requester_id === responser) {
        return { ...item, showOptions: !item.showOptions };  // 切换当前项的操作按钮显示状态
      }
      return item;
    });
    this.setData({
      joinCourtRequests: updatedRequests
    });
  },

  // 同意申请
  acceptRequest: function(e) {
    const id = e.currentTarget.dataset.id;  // 从事件对象获取ID
    const responser = e.currentTarget.dataset.responser
    const request = this.data.joinCourtRequests.find(item => item.Teamup_court_id === id && item.Teamup_requester_id === responser );  // 找到对应的请求记录
    if (!request) {
      wx.showToast({
        title: '请求记录未找到',
        icon: 'none'
      });
      return;
    }
    const Teamup_court_id = request.Teamup_court_id;  // 获取场地ID
    const Teamup_requester_id = request.Teamup_requester_id;  // 获取请求者ID

    wx.request({
      url: 'http://123.60.86.239:8000/teamup/accept',  // 发送同意请求的API
      method: 'POST',
      data: { 
        Teamup_court_id: Teamup_court_id, 
        Teamup_requester_id: Teamup_requester_id
      },
      success: (res) => {
        if (res.data.status === 'success') {
          this.loadJoinCourtRequests();  // 重新加载数据
          wx.showToast({
            title: '已同意申请',
            icon: 'success'
          });
        } else {
          wx.showToast({
            title: res.data.message || '操作失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('Failed to accept request:', err);
        wx.showToast({
          title: '操作失败，请稍后重试',
          icon: 'none'
        });
      }
    });
  },

  // 拒绝申请
  rejectRequest: function(e) {
    const id = e.currentTarget.dataset.id;  // 从事件对象获取ID
    const responser = e.currentTarget.dataset.responser
    const request = this.data.joinCourtRequests.find(item => item.Teamup_court_id === id && item.Teamup_requester_id === responser);  // 找到对应的请求记录
    if (!request) {
      wx.showToast({
        title: '请求记录未找到',
        icon: 'none'
      });
      return;
    }
    const Teamup_court_id = request.Teamup_court_id;  // 获取场地ID
    const Teamup_requester_id = request.Teamup_requester_id;  // 获取请求者ID

    wx.request({
      url: 'http://123.60.86.239:8000/teamup/refuse',  // 发送拒绝请求的API
      method: 'POST',
      data: { 
        Teamup_court_id: Teamup_court_id, 
        Teamup_requester_id: Teamup_requester_id
      },
      success: (res) => {
        if (res.data.status === 'success') {
          this.loadJoinCourtRequests();  // 重新加载数据
          wx.showToast({
            title: '已拒绝申请',
            icon: 'success'
          });
        } else {
          wx.showToast({
            title: res.data.message || '操作失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('Failed to reject request:', err);
        wx.showToast({
          title: '操作失败，请稍后重试',
          icon: 'none'
        });
      }
    });
  },
  goToChat: function (e) {
    const courtId = e.currentTarget.dataset.id;
    const responserId = e.currentTarget.dataset.responser;
    console.log(courtId)
    console.log(responserId)
    // 学生存在，发送消息
    wx.request({
      url: 'http://123.60.86.239:8000/chat/send',
      method: 'POST',
      header: {
          'Content-Type': 'application/json',
      },
      data: {
          Sender_id: this.data.Student_id,
          Receiver_id: responserId,
          Message_sent: '球友你好！听说你想要和我一起在' + courtId + '打球？' ,
      },
      success: (sendRes) => {
          if (sendRes.data.status === 'success') {
              // 跳转到聊天页面并传递参数
              wx.navigateTo({
                url: `/pages/5-conversation/conversation?sender_id=${this.data.Student_id}&receiver_id=${responserId}`,
              });
          } else {
              wx.showToast({
                  title: sendRes.data.message || '消息发送失败',
                  icon: 'none',
              });
          }
      },
      fail: () => {
          wx.showToast({
              title: '发送消息请求失败',
              icon: 'none',
          });
      },
  });
  }
});