Page({
  data: {
    Student_id:'',
    historyRecords: [] // 初始为空，由后端数据填充
  },

  onLoad: function() {
    wx.getStorage({key: 'student_id',success: (res) => {
      this.setData({Student_id: res.data});
      console.log(this.data.Student_id)
      this.fetchHistoryRecords();
      
    },
    fail: () => {wx.showToast({title: '未登录或学号未找到',icon: 'none'});}});
    
  },

  fetchHistoryRecords: function() {
    const that = this;
    wx.request({
      url: 'http://123.60.86.239:8000/student/get_apply', // 替换为你的后端 API 地址
      method: 'POST',
      header: {
        'content-type': 'application/json' // 根据需要设置请求头
      },
      data: {
        my_id: this.data.Student_id // 替换为用户的实际 ID
      },
      success(res) {
        if (res.data.status === 'success') {
          console.log(res.data.data)
          const records = res.data.data.map(item => ({
            courtid_split: item.court_id.split('-'),
            source: item.source,
            status: item.status
          }));
          for(let i=0;i<records.length;i++){
            records[i].courtid_split[5]++
          }
          console.log(records)
          that.setData({ historyRecords: records });
        } else {
          wx.showToast({
            title: '获取数据失败',
            icon: 'none'
          });
        }
      },
      fail() {
        wx.showToast({
          title: '请求失败',
          icon: 'none'
        });
      }
    });
  }
});
