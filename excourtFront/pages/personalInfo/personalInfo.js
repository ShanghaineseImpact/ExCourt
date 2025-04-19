// pages/6-PersonInfo/6-PersonInfo.js
Page({
  data: {
    student_id:0,
    Student_name:'',
    profileurl: '', // 默认头像路径
    nickname: '', // 用户昵称
    phone: '', // 手机号
    credit: 100, // 信誉分，默认值为100
    levels: ['入门', '练习者', '大佬'], // 羽毛球水平选项
    levelIndex: 0 // 默认选中第一个选项
  },
  
  onLoad(){
    wx.getStorage({key: 'student_id',success: (res) => {
      this.data.student_id=res.data
      //console.log('获取到学号:', this.data.student_id);
      this.initPerson()
    },
    fail: () => {wx.showToast({title: '未登录或学号未找到',icon: 'none'});}});
  },

  onShow(){
    wx.getStorage({key: 'student_id',success: (res) => {
      this.data.student_id=res.data
      //console.log('获取到学号:', this.data.student_id);
      //this.initPerson()
      //wx.getStorage({key:'profileurl',success:(res)=>{
      //  console.log(res.data.profileurl)
      //  this.setData({profileurl:res.data.profileurl})
      //}})
    },
    fail: () => {wx.showToast({title: '未登录或学号未找到',icon: 'none'});}});
  },

  initPerson(){
    wx.request({
      url: 'http://123.60.86.239:8000/student/find', // 替换后台API地址
      method: 'POST',
      data:{
        search_id:this.data.student_id
      },
      success: (res) => {
        if (res.data.status=='success') {
          //console.log(res.data.data)
          this.setData({
            student_id:res.data.data[0],
            Student_name:res.data.data[1],
            profileurl:res.data.data[2],
            nickname:res.data.data[3],
            credit: res.data.data[4],
            levelIndex : res.data.data[5],
            status: res.data.data[6],
            phone:res.data.data[7]
          });
          this.getUrl()
        }
      },
      fail: (err) => {
        console.error("Failed to fetch lost and found items:", err);
      }
    });
  },

  onNicknameInput: function(e) {
    this.setData({
      nickname: e.detail.value
    });
  },
  
  onPhoneInput: function(e) {
    this.setData({
      phone: e.detail.value
    });
  },
  
  onLevelChange: function(e) {
    this.setData({
      levelIndex: e.detail.value
    });
  },
  
  changeAvatar: function() {
    // 打开选择图片界面的逻辑
    wx.chooseMedia({
      count:1,
      mediaType:['image'],
      sourceType:['album','camera'],
      camera:'back',
      success: (res) => {
        const tempFilePath = res.tempFiles[0].tempFilePath;
        wx.showLoading({
          title: '正在上传图片',mask:true
        })
        this.uploadImage(tempFilePath);
      }
    });
  },

  uploadImage(fp){
    wx.uploadFile({
      filePath: fp,
      name: 'photo',
      url: 'http://123.60.86.239:8000/upload/profile',
      formData:{
        filename:this.data.student_id.toString()+'.png'
      },
      success:(res)=>{console.log(res.data);
        let jo = JSON.parse(res.data)
        this.setData({profileurl:jo.profileurl})
        wx.setStorage({
          key: 'profileurl',
          data: jo.profileurl,
          success: () => {console.log('profileurl 已存储',jo.profileurl);wx.hideLoading();}
        });
      },
      fail:(err)=>{console.log(err)
        wx.hideLoading();
        wx.showToast({
          title: '上传失败',
          icon: 'none'
        });
      }
    })
  },
  
  saveUserInfo: function() {
    console.log(this.data.student_id)
    console.log(this.data.nickname)
    console.log(this.data.profileurl)
    console.log(this.data.levelIndex)
    console.log(this.data.phone)
    wx.request({
      url: 'http://123.60.86.239:8000/student/update', // 替换后台API地址
      method: 'POST',
      data:{
        search_id:this.data.student_id,
        nickname:this.data.nickname,
        profileurl:this.data.profileurl,
        level:this.data.levelIndex,
        phone:this.data.phone
      },
      success: (res) => {
        if (res.data.status=='success') {
          console.log(res.data)
          wx.showToast({
            title: res.data.message,
            icon: 'success',
            duration: 2000});
        }else {
          wx.showModal({
            title: '更新失败',
            content: res.data.message || '未知错误',
            showCancel: false
        });
        }
      },
      fail: (err) => {
        wx.showModal({
          title: '网络错误',
          content: '无法连接到服务器，请稍后重试',
          showCancel: false});
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