const app = getApp();

Page({
  data: {
    account_id: 0,
    student_name: '',
    my_contacts: [], // 所有联系人
    filtered_contacts: [], // 搜索后显示的联系人
    searchQuery: '', // 搜索框输入
  },

  onLoad(options) {
    this.setData({
      account_id: Number(options.student_id),
      student_name: options.student_name,
    });
    this.getFriendList();
  },

  onShow() {
    this.getFriendList();
  },

  getFriendList() {
    wx.request({
      url: 'http://123.60.86.239:8000/chat/contacts',
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
      },
      data: {
        student_id: this.data.account_id,
      },
      success: (res) => {
        if (res.data.status === 'success') {
          this.setData({
            my_contacts: res.data.data,
            filtered_contacts: res.data.data, // 初始化过滤列表
          });
          this.getUrl()
        } else {
          wx.showToast({
            title: res.data.message || '获取联系人失败',
            icon: 'none',
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '请求失败',
          icon: 'none',
        });
      },
    });
  },
  getUrl(){
    const cont = this.data.my_contacts
    for(let i=0;i<cont.length;i++){
      wx.request({
                url: 'http://123.60.86.239:8000/upload/find_profile',
                method:'POST',
                data:{student_id:cont[i].student_id.toString()+'.png'},
                success:(res)=>{
                  if(res.statusCode==200){cont[i].profileurl=res.data.imageUrl}
                },
                fail:(err)=>{console.error("Failed to fetch lost and found items:", err);}
              })
    }
    this.setData({my_contacts:cont,filtered_contacts:cont})
  },

  startChat(e) {
    const index = e.currentTarget.dataset.index;
    const stuid = this.data.filtered_contacts[index].student_id;
    wx.navigateTo({
      url: '/pages/5-conversation/conversation?sender_id=' + this.data.account_id + '&receiver_id=' + stuid,
    });
  },

  // 输入时实时过滤
  onSearchInput(e) {
    const query = e.detail.value.toLowerCase();
    this.setData({
      searchQuery: query,
      filtered_contacts: this.data.my_contacts.filter((friend) =>
        friend.name.toLowerCase().includes(query)
      ),
    });
  },

  createChat() {
    wx.showModal({
        title: '创建聊天',
        placeholderText: '请输入学号',
        editable: true,
        success: (res) => {
            if (res.confirm && res.content.trim()) {
                const newStudentId = parseInt(res.content.trim(), 10);
                // 调用后端接口检查学生是否存在
                wx.request({
                    url: 'http://123.60.86.239:8000/student/find',
                    method: 'POST',
                    header: {
                        'Content-Type': 'application/json',
                    },
                    data: {
                        search_id: newStudentId,
                    },
                    success: (checkRes) => {
                        if (checkRes.data.status === 'success') {
                            // 学生存在，发送消息
                            wx.request({
                                url: 'http://123.60.86.239:8000/chat/send',
                                method: 'POST',
                                header: {
                                    'Content-Type': 'application/json',
                                },
                                data: {
                                    Sender_id: this.data.account_id,
                                    Receiver_id: newStudentId,
                                    Message_sent: '球友你好！',
                                },
                                success: (sendRes) => {
                                    if (sendRes.data.status === 'success') {
                                        // 消息发送成功，跳转到聊天界面
                                        wx.showToast({
                                          title: sendRes.data.message || '聊天添加成功！',
                                          icon: 'none',
                                        });
                                        wx.navigateTo({
                                            url: '/pages/5-conversation/conversation?sender_id='+ this.data.account_id + '&receiver_id=' + newStudentId,
                                        },
                                        );
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
            }
        },
    });
  }

});
