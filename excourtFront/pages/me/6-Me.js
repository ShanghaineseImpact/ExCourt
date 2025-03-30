// pages/6-Me/6-Me.js
Page({
  data: {
    student_id:0,
    Student_name:'',
    profileurl: '',
    credit:0,
    level:'',
    status:'',
    levels:['菜鸟','初学者','高手'],
    nickname: '' // 用户昵称
  },

  onLoad() {
        wx.getStorage({key: 'student_id',success: (res) => {
          this.data.student_id=res.data
          //console.log('获取到学号:', this.data.student_id);
          this.initPerson()
        },
        fail: () => {wx.showToast({title: '未登录或学号未找到',icon: 'none'});}});
  },
  onShow() {
        wx.getStorage({key: 'student_id',success: (res) => {
          this.data.student_id=res.data
          //console.log('获取到学号:', this.data.student_id);
          this.initPerson()
        },
        fail: () => {wx.showToast({title: '未登录或学号未找到',icon: 'none'});}});
  },

  manageUserInfo(e) {
    if (e.detail.userInfo) {
      this.setData({
        avatarUrl: e.detail.userInfo.avatarUrl,
        nickname: e.detail.userInfo.nickName
      });
    } else {
      wx.showToast({
        title: '授权失败，请重新授权',
        icon: 'none'
      });
    }
    wx.navigateTo({
      url: '/pages/6-PersonInfo/6-PersonInfo'
    });
  },

  onNicknameInput(e) {
    this.setData({
      nickname: e.detail.value
    });
  },

  manageHistory() {
    wx.showToast({
      title: '历史记录',
      icon: 'none'
    }),
    wx.navigateTo({
      url: '/pages/6-historyRecord/historyRecord'
    });
  },

  manageOperation() {
    wx.showToast({
      title: '操作记录',
      icon: 'none'
    }),
    wx.navigateTo({
      url: '/pages/6-operationRecord/6-operationRecord'
    });
  },

  manageBuddies() {
    wx.showToast({
      title: '球友管理',
      icon: 'none'
    }),
    wx.navigateTo({
      url: '/pages/6-buddyManagement/buddyManagement'
    });
  },

  logout() {
    // 清空所有页面数据
    // 获取全局应用实例
    const app = getApp();
    if (!app) {
        console.error("无法获取全局 app 实例");
        return;
    }
    app.clearAllPageData();
    wx.clearStorageSync(); // 清除本地存储
    wx.reLaunch({
      url: '/pages/6-login/Login'
    });
  },
  // 导航到我的申请页面
  navigateToMyPublish: function() {
    wx.navigateTo({
      url: '/pages/6.4-MyPublish/6.4-MyPublish'
    });
  },
  
  // 导航到我的发布页面
  navigateToMyClaim: function() {
    wx.navigateTo({
      url: '/pages/6.5-MyClaim/6.5-MyClaim'
    });
  },
    initPerson(){
        wx.request({
          url: 'http://123.60.86.239:8000/student/find', // 替换后台API地址
          method: 'POST',
          data:{
            search_id:this.data.student_id
          },
          success: (res) => {
            if (res.data.status=='success') {
              console.log(res.data.data)
              //const str = res.data.data[2];
              this.setData({
                student_id:res.data.data[0],
                Student_name:res.data.data[1],
                nickname:res.data.data[3],
                credit: res.data.data[4],
                level : res.data.data[5],
                status: res.data.data[6]
              });
              this.getUrl()
            }
          },
          fail: (err) => {
            console.error("Failed to fetch lost and found items:", err);
          }
        });
      },
    getUrl(){
      console.log(this.data.student_id)
            wx.request({
              url: 'http://123.60.86.239:8000/upload/find_profile',
              method:'POST',
              data:{student_id:this.data.student_id.toString()+'.png'},
              success:(res)=>{
                if(res.statusCode==200){
                this.setData({profileurl:res.data.imageUrl})
                console.log(this.data.profileurl)}
              },
              fail:(err)=>{console.error("Failed to fetch lost and found items:", err);}
            })
          },
});