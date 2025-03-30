Page({
  data: {
    student_id: '',
    student_name: '',
    nick_name:'',
    student_phone: '',
    password: '',
  },

  // 学号输入框数据绑定
  bindStudentIdInput: function(e) {
    this.setData({
      student_id: e.detail.value
    });
  },

  // 姓名输入框数据绑定
  bindStudentNameInput: function(e) {
    this.setData({
      student_name: e.detail.value
    });
  },

  bindNickNameInput: function(e) {
    this.setData({
      nick_name: e.detail.value
    });
  },

  // 手机号输入框数据绑定
  bindStudentPhoneInput: function(e) {
    this.setData({
      student_phone: e.detail.value
    });
  },

  // 密码输入框数据绑定
  bindPasswordInput: function(e) {
    this.setData({
      password: e.detail.value
    });
  },

  // 注册按钮点击事件
  bindRegister: function() {
    const { student_id, student_name, password } = this.data;

    // 向Flask后端发送请求
    wx.request({
      url: 'http://123.60.86.239:5000/verify', // Flask后端的URL
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      },
      data: {
        Student_id: student_id,
        Student_name: student_name,
        Student_password: password
      },
      success:(res)=> {
        if (res.statusCode === 200) {
          wx.showToast({
            title: '注册成功',
            icon: 'success',
            duration: 4000
          });
          this.registerInSystem();
          // 注册成功后跳转到登录页面
          wx.navigateTo({ url: '/pages/6-login/Login' });
        } else if (res.statusCode === 404){
          wx.showToast({
            title: '数据匹配失败',
            icon: 'error',
            duration: 2000
          });
        }
      },
      fail:(err)=> {
        console.error(err);
        wx.showToast({
          title: '请求失败',
          icon: 'error',
          duration: 2000
        });
      }
    });
  },
  registerInSystem(){
    wx.request({
      url:'http://123.60.86.239:8000/student/register',
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      },
      data: {
        Student_id: this.data.student_id,
        Student_name: this.data.student_name,
        Student_nickname: this.data.nick_name,
        Student_phone: this.data.student_phone,
        Student_password: this.data.password
      },
    })
  }
});
