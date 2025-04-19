Page({
  data: {
    student_id:0,
    applied: [], // 我申请过的记录
    published: [], // 我发布过的记录
    requests: [], // 其他人对我的发布的申请
    currentTab: 'applied', // 默认显示“我的申请”
  },

  onLoad: function() {
    wx.getStorage({key:'student_id',success:(res)=>{
      //console.log(res)
      this.setData({student_id:res.data})
      this.getApplication()
      this.getPublish()
      this.getApproval()
    }})
    //this.loadData();
  },

  loadData: function() {
    // 模拟数据加载
    const applied = [
      { id: 1, courtId: 'C001', status: 'Pending', showOptions: false },
      { id: 2, courtId: 'C002', status: 'Approved', showOptions: false }
    ];

    const published = [
      { id: 3, courtId: 'C003', status: 'Active', showOptions: false },
      { id: 4, courtId: 'C004', status: 'Completed', showOptions: false }
    ];

    const requests = [
      { id: 5, courtId: 'C005', requesterName: 'UserA', showOptions: false },
      { id: 6, courtId: 'C006', requesterName: 'UserB', showOptions: false }
    ];

    this.setData({
      applied,
      published,
      requests
    });
  },

  // 切换显示的部分
  switchTab: function(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({
      currentTab: tab
    });

    // 隐藏其他部分的操作按钮
    const { applied, published, requests } = this.data;
    const hideOptions = (array) => array.map(item => ({ ...item, showOptions: false }));

    // 清除所有选项按钮显示
    this.setData({
      applied: hideOptions(applied),
      published: hideOptions(published),
      requests: hideOptions(requests)
    });
  },
  getApplication(){
    wx.request({
      url: 'http://123.60.86.239:8000/student/get_apply',
      method: 'POST',
      data: {
        my_id: this.data.student_id,
      },
      success:(res)=>{
        if(res.statusCode==200){
          const applylist = res.data.data;
          console.log("app",res.data)
          for(let i = 0;i<applylist.length;i++){
            applylist[i].id=i
          }
          this.setData({applied:applylist})
        }else{print(res.data)}
      },fail:(err)=>{console.log(err)}
    })
  },
  getPublish(){
    wx.request({
      url: 'http://123.60.86.239:8000/student/get_publish',
      method: 'POST',
      data: {
        my_id: this.data.student_id,
      },
      success:(res)=>{
        if(res.statusCode==200){
          const publishlist = res.data.data;
          console.log("pub",res.data)
          for(let i = 0;i<publishlist.length;i++){
            publishlist[i].id=i
          }
          this.setData({published:publishlist})
        }else{console.log(res.data)}
      },fail:(err)=>{console.log(err)}
    })
  },
  getApproval(){
    wx.request({
      url: 'http://123.60.86.239:8000/student/get_request',
      method: 'POST',
      data: {
        my_id: this.data.student_id,
      },
      success:(res)=>{
        if(res.statusCode==200){
          const reqlist = res.data.data;
          //console.log(res.data)
          for(let i = 0;i<reqlist.length;i++){
            reqlist[i].id=i
          }
          this.setData({requests:reqlist})
        }else{console.log(res.data)}
      },fail:(err)=>{console.log(err)}
    })
  },

  // 显示或隐藏操作按钮
  toggleOptions: function(e) {
    const id = e.currentTarget.dataset.id;
    const currentTab = this.data.currentTab;

    let targetArray = null;
    if (currentTab === 'applied') {
      targetArray = this.data.applied;
    } else if (currentTab === 'published') {
      targetArray = this.data.published;
    } else if (currentTab === 'requests') {
      targetArray = this.data.requests;
    }

    if (!targetArray) return;

    const updatedArray = targetArray.map(item => {
      if (item.id === id) {
        return { ...item, showOptions: !item.showOptions }; // 切换当前项的按钮显示
      }
      return item;
    });

    // 更新对应的数组
    if (currentTab === 'applied') {
      this.setData({ applied: updatedArray });
    } else if (currentTab === 'published') {
      this.setData({ published: updatedArray });
    } else if (currentTab === 'requests') {
      this.setData({ requests: updatedArray });
    }
  },

  goToPage: function(e) {
    const action = e.currentTarget.dataset.action;

    if (action === 'sendCourt') {
      wx.navigateTo({
        url: `/pages/6.1sendCourt/sendCourt` // 假设送场页面路径是 sendCourt
      });
    } else if (action === 'joinCourt') {
      wx.navigateTo({
        url: `/pages/6.2joinCourt/joinCourt` // 假设拼场页面路径是 joinCourt
      });
    } else if (action === 'changeCourt') {
      wx.navigateTo({
        url: `/pages/6.3changeCourt/changeCourt` // 假设换场页面路径是 changeCourt
      });
    }
  },

  revokeApplication: function(e) {
    wx.request({
      url: 'http://123.60.86.239:8000/student/delete_apply',
      method: 'POST',
      data: {
        table_name: e.currentTarget.dataset.table,
        court_id:e.currentTarget.dataset.courtid,
        applier:this.data.student_id
      },
      success:(res)=>{
        console.log(res)
        if(res.statusCode==200){
          this.getApplication()
        }
      }
    })
  },
  //有bug
  revokePublication: function(e) {
    console.log(e.currentTarget.dataset.table)
    console.log(e.currentTarget.dataset.courtid)
    console.log(this.data.student_id)
    wx.request({
      url: 'http://123.60.86.239:8000/student/delete_pub',
      method: 'POST',
      data: {
        table_name: e.currentTarget.dataset.table,
        court_id:e.currentTarget.dataset.courtid,
        puber_id:this.data.student_id
      },
      success:(res)=>{
        console.log(res)
        if(res.statusCode==200){
          this.getPublish()
        }
      }
    })
  },

  acceptRequest: function(e) {
    wx.request({
      url: 'http://123.60.86.239:8000/student/update_req',
      method: 'POST',
      data: {
        table_name: e.currentTarget.dataset.table,
        court_id:e.currentTarget.dataset.courtid,
        owner_id:this.data.student_id,
        status:1
      },
      success:(res)=>{
        console.log(res)
        if(res.statusCode==200){
          this.getApproval()
        }
      }
    })
  },

  rejectRequest: function(e) {
    wx.request({
      url: 'http://123.60.86.239:8000/student/update_req',
      method: 'POST',
      data: {
        table_name: e.currentTarget.dataset.table,
        court_id:e.currentTarget.dataset.courtid,
        owner_id:this.data.student_id,
        status:0
      },
      success:(res)=>{
        console.log(res)
        if(res.statusCode==200){
          this.getApproval()
        }
      }
    })
  }
});
