Page({
  data: {
    Student_id: '',
    sendCourtRequests: [], // 保存送场申请的记录
  },

  onLoad: function() {
    wx.getStorage({
      key: 'student_id',
      success: (res) => {
        this.setData({ Student_id: res.data });
        this.loadSendCourtRequests();
        console.log(this.data.sendCourtRequests)
      },
      fail: () => {
        wx.showToast({
          title: '未登录或学号未找到',
          icon: 'none'
        });
      }
    });
  },

  loadSendCourtRequests: function() {
    if (!this.data.Student_id) {
      wx.showToast({
        title: '用户ID不存在',
        icon: 'none'
      });
      return;
    }
  
    wx.request({
      url: 'http://123.60.86.239:8000/offercourt/get_offer_records',
      method: 'POST',
      data: { my_id: this.data.Student_id },
      success: (res) => {
        if (res.data.status === 'success') {
          console.log(res)
          console.log(res.data.data)
          const requests = res.data.data.map(item => {
            // 根据状态设置颜色
            let statusColor = '#FFFFFF'; // 默认白色
            if (item.Offer_state === 'offered') {
              statusColor = '#D4EDDA'; // 绿色
            } else if (item.Offer_state === 'retrieved') {
              statusColor = '#F8D7DA'; // 红色
            } else if (item.Offer_state === 'not_responsed') {
              statusColor = '#FFF3CD'; // 黄色
            }

            return {
              Offer_uploader_court_id: item.Offer_uploader_court_id,
              Offer_responser_id: item.Offer_responser_id,
              Student_credit: item.Student_credit,
              Student_name: item.Student_name,
              statusColor: statusColor, // 添加状态颜色
              showOptions: false
            };
          });
          console.log(requests)
          this.setData({
            sendCourtRequests: requests
          });
        } else {
          wx.showToast({
            title: res.data.message || '没有找到送场申请记录',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('Request failed:', err);
        wx.showToast({
          title: '请求失败，请稍后重试',
          icon: 'none'
        });
      }
    });
  },

  // 显示或隐藏操作按钮
  toggleOptions: function(e) {
    const id = e.currentTarget.dataset.id;
    const responser = e.currentTarget.dataset.responser
    console.log(e.currentTarget.dataset)
    const updatedRequests = this.data.sendCourtRequests.map(item => {
      if (item.Offer_uploader_court_id === id && item.Offer_responser_id === responser) {
        return { ...item, showOptions: !item.showOptions };  // 切换当前项的操作按钮显示状态
      }
      return item;
    });
    this.setData({
      sendCourtRequests: updatedRequests
    });
  },

  // 同意申请
  acceptRequest: function(e) {
    const id = e.currentTarget.dataset.id;  // 从事件对象获取ID
    const responser = e.currentTarget.dataset.responser
    const request = this.data.sendCourtRequests.find(item => item.Offer_uploader_court_id === id && item.Offer_responser_id === responser);  // 找到对应的请求记录
    if (!request) {
      wx.showToast({
        title: '请求记录未找到',
        icon: 'none'
      });
      return;
    }
    const Offer_uploader_court_id = request.Offer_uploader_court_id;  // 获取场地ID
    const Offer_responser_id = request.Offer_responser_id;  // 获取请求者ID

    wx.request({
      url: 'http://123.60.86.239:8000/offercourt/accept',  // 发送同意请求的API
      method: 'POST',
      data: { 
        my_id: this.data.Student_id,
        court_id: Offer_uploader_court_id, 
        recorder_id: Offer_responser_id
      },
      success: (res) => {
        if (res.data.status === 'success') {
          this.loadSendCourtRequests();  // 重新加载数据
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
    const request = this.data.sendCourtRequests.find(item => item.Offer_uploader_court_id === id && item.Offer_responser_id === responser);  // 找到对应的请求记录
    if (!request) {
      wx.showToast({
        title: '请求记录未找到',
        icon: 'none'
      });
      return;
    }
    const Offer_uploader_court_id = request.Offer_uploader_court_id;  // 获取场地ID
    const Offer_responser_id = request.Offer_responser_id;  // 获取请求者ID

    console.log(Offer_uploader_court_id)
    console.log(Offer_responser_id)
    wx.request({
      url: 'http://123.60.86.239:8000/offercourt/decline',  // 发送拒绝请求的API
      method: 'POST',
      data: { 
        my_id:this.data.Student_id,
        court_id: Offer_uploader_court_id, 
        recorder_id: Offer_responser_id
      },
      success: (res) => {
        if (res.data.status === 'success') {
          this.loadSendCourtRequests();  // 重新加载数据
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
          Message_sent: '球友你好！听说你想要我的' + courtId + '场地？' ,
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