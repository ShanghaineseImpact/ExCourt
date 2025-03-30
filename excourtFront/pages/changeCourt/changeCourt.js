Page({
  data: {
    Student_id: '',
    exCourtRequests: [], // 保存换场申请的记录
  },

  onLoad: function() {
    wx.getStorage({
      key: 'student_id',
      success: (res) => {
        this.setData({ Student_id: res.data });
        this.loadExCourtRequests();
        console.log(this.data.exCourtRequests)
      },
      fail: () => {
        wx.showToast({
          title: '未登录或学号未找到',
          icon: 'none'
        });
      }
    });
  },

  loadExCourtRequests: function() {
    if (!this.data.Student_id) {
      wx.showToast({
        title: '用户ID不存在',
        icon: 'none'
      });
      return;
    }
  
    wx.request({
      url: 'http://123.60.86.239:8000/exchangecourt/get_response_records_by_student',
      method: 'POST',
      data: { student_id: this.data.Student_id },
      success: (res) => {
        if (res.data.status === 'success') {
          console.log(res)
          console.log(res.data.data)
          const requests = res.data.data.map(item => {
            // 根据状态设置颜色
            let statusColor = '#FFFFFF'; // 默认白色
            if (item.exchange_state === 'exchanged') {
              statusColor = '#D4EDDA'; // 绿色
            } else if (item.exchange_state === 'retrieved') {
              statusColor = '#F8D7DA'; // 红色
            } else if (item.exchange_state === 'not_responsed') {
              statusColor = '#FFF3CD'; // 黄色
            }

            return {
              exchange_responser_court_id: item.exchange_responser_court_id,
              exchange_uploader_court_id: item.exchange_uploader_court_id,
              Student_credit: item.responser_info.credit,
              Student_name: item.responser_info.name,
              exchange_responser_id: item.exchange_responser_id,
              statusColor: statusColor, // 添加状态颜色
              showOptions: false
            };
          });
          console.log(requests)
          this.setData({
            exCourtRequests: requests
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
    const exchange_uploader_court_id = e.currentTarget.dataset.exchange_uploader_court_id;
    const exchange_responser_court_id = e.currentTarget.dataset.exchange_responser_court_id
    const updatedRequests = this.data.exCourtRequests.map(item => {
      if (item.exchange_uploader_court_id === exchange_uploader_court_id && item.exchange_responser_court_id === exchange_responser_court_id) {
        console.log('显示')
        return { ...item, showOptions: !item.showOptions };  // 切换当前项的操作按钮显示状态
      }
      return item;
    });
    this.setData({
      exCourtRequests: updatedRequests
    });
  },

  // 同意申请
  acceptRequest: function(e) {
    console.log(e.currentTarget.dataset)
    const exchange_uploader_court_id = e.currentTarget.dataset.exchange_uploader_court_id;
    const exchange_responser_court_id = e.currentTarget.dataset.exchange_responser_court_id

    const request = this.data.exCourtRequests.find(item => item.exchange_uploader_court_id === exchange_uploader_court_id && item.exchange_responser_court_id === exchange_responser_court_id);  // 找到对应的请求记录
    if (!request) {
      wx.showToast({
        title: '请求记录未找到',
        icon: 'none'
      });
      return;
    }
    
    const exchange_responser_id = e.currentTarget.dataset.exchange_responser_id

    console.log(this.data.Student_id)
    console.log(exchange_responser_id)
    console.log(exchange_uploader_court_id)
    console.log(exchange_responser_court_id)
    wx.request({
      url: 'http://123.60.86.239:8000/exchangecourt/complete_exchange',  // 发送同意请求的API
      method: 'POST',
      data: { 
        Exchange_uploader_court_id: exchange_uploader_court_id,
        Exchange_responser_court_id: exchange_responser_court_id,
        Exchange_uploader_id: this.data.Student_id, 
        Exchange_responser_id: exchange_responser_id
      },
      success: (res) => {
        if (res.data.status === 'success') {
          this.loadExCourtRequests();  // 重新加载数据
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
    const exchange_uploader_court_id = e.currentTarget.dataset.exchange_uploader_court_id;
    const exchange_responser_court_id = e.currentTarget.dataset.exchange_responser_court_id
    const exchange_responser_id = e.currentTarget.dataset.exchange_responser_id

    const request = this.data.exCourtRequests.find(item => item.exchange_uploader_court_id === exchange_uploader_court_id && item.exchange_responser_court_id === exchange_responser_court_id);  // 找到对应的请求记录
    if (!request) {
      wx.showToast({
        title: '请求记录未找到',
        icon: 'none'
      });
      return;
    }


    wx.request({
      url: 'http://123.60.86.239:8000/exchangecourt/refuse',  // 发送拒绝请求的API
      method: 'POST',
      data: { 
        Exchange_uploader_court_id: exchange_uploader_court_id,
        Exchange_responser_court_id: exchange_responser_court_id,
        Exchange_uploader_id: this.data.Student_id, 
        Exchange_responser_id: exchange_responser_id
      },
      success: (res) => {
        if (res.data.status === 'success') {
          this.loadExCourtRequests();  // 重新加载数据
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
    const exchange_uploader_court_id = e.currentTarget.dataset.exchange_uploader_court_id;
    const exchange_responser_court_id = e.currentTarget.dataset.exchange_responser_court_id
    const exchange_responser_id = e.currentTarget.dataset.exchange_responser_id

    // 学生存在，发送消息
    wx.request({
      url: 'http://123.60.86.239:8000/chat/send',
      method: 'POST',
      header: {
          'Content-Type': 'application/json',
      },
      data: {
          Sender_id: this.data.Student_id,
          Receiver_id: exchange_responser_id,
          Message_sent: '球友你好！听说你想要用' + exchange_responser_court_id + '场地和我交换' + exchange_uploader_court_id ,
      },
      success: (sendRes) => {
          if (sendRes.data.status === 'success') {
              // 跳转到聊天页面并传递参数
              wx.navigateTo({
                url: `/pages/5-conversation/conversation?sender_id=${this.data.Student_id}&receiver_id=${exchange_responser_id}`,
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