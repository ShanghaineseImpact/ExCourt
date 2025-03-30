// Login.js
Page({
  data: {
      student_id: '', // 绑定输入框的学号数据
      password: ''    // 绑定输入框的密码数据
  },

  // 学号输入框数据绑定
  bindUsernameInput: function(e) {
      this.setData({
          student_id: e.detail.value
      });
  },

  // 密码输入框数据绑定
  bindPasswordInput: function(e) {
      this.setData({
          password: e.detail.value
      });
  },

  // 登录按钮点击事件
bindLogin: function() {
  if (this.data.student_id === '' || this.data.password === '') {
      wx.showToast({
          title: '学号或密码不能为空',
          icon: 'none'
      });
      return;
  }

  wx.request({
      url: 'http://123.60.86.239:8000/student/login', // 后端登录接口
      method: 'POST',
      data: {
          Student_id: this.data.student_id,
          Student_password: this.data.password
      },
      success: (res) => {
          if (res.statusCode === 200) {
              wx.showToast({
                  title: '登录成功',
                  icon: 'success'
              });
              // 存储 student_id 到本地存储
              wx.setStorage({
                  key: 'student_id',
                  data: res.data.Student_id,
                  success: () => {}
              });
              wx.setStorage({
                key: 'student_name',
                data: res.data.Student_name,
                success: () => {}
            });
              // 跳转到首页，并传递用户信息
              wx.switchTab({url: '/pages/index/index'});
          } else if (res.statusCode === 404) {
              wx.showToast({
                  title: '学号不存在，请检查后重试',
                  icon: 'none'
              });
          } else if (res.statusCode === 401) {
              wx.showToast({
                  title: '密码错误，请重新输入',
                  icon: 'none'
              });
          } else {
              wx.showToast({
                  title: res.data.message || '登录失败',
                  icon: 'none'
              });
          }
      },
      fail: () => {
          wx.showToast({
              title: '网络错误，请稍后再试',
              icon: 'none'
          });
      }
  });
},
  


  goToRegister: function() {
      wx.navigateTo({
          url: '/pages/6-register/register'
      });
  }
});
