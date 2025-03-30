Page({
  data: {
    Lost_uploader_id: '',
    itemName: '',
    itemDescription: '',
    LostTime: '',
    lostLocation: '',
    Url: '',
    contactInfo: '',
  },

  onInputChange(e) {
    const { field } = e.currentTarget.dataset;
    this.setData({
      [field]: e.detail.value
    });
  },

  onDateChange(e) {
    this.setData({
      LostTime: e.detail.value
    });
  },

  uploadImage() {
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
        this.uploadIma(tempFilePath);
      }
    });
  },
  uploadIma(fp){
    wx.uploadFile({
      filePath: fp,
      name: 'photo',
      url: 'http://123.60.86.239:8000/upload/lostfind',
      success:(res)=>{console.log(res.data);
        wx.hideLoading();
        let jo = JSON.parse(res.data)
        this.setData({Url:jo.profilename})
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

  submitLostItem() {
    const { itemName, itemDescription, LostTime, lostLocation, Url, contactInfo } = this.data;

    // 必填项校验
    if (!itemName || !contactInfo || !LostTime || !lostLocation) {
      wx.showToast({
        title: '请填写所有必填项',
        icon: 'none'
      });
      return;
    }

    wx.getStorage({
      key: 'student_id',
      success: (res) => {
        this.setData({ Lost_uploader_id: res.data });
        wx.request({
          url: 'http://123.60.86.239:8000/lost_and_found/lost/create', // 替换为实际后端地址
          method: 'POST',
          header: {
            'Content-Type': 'application/json'
          },
          data: {
            Lost_uploader_id: this.data.Lost_uploader_id,
            Lost_item_name: itemName,
            Lost_description: itemDescription,
            Lost_position: lostLocation,
            Lost_time: LostTime,
            Lost_item_pic_url: Url || '',
            Lost_contact: contactInfo,
          },
          success(res) {
            if (res.statusCode === 201) {
              wx.showToast({
                title: '发布成功',
                icon: 'success'
              });
              wx.navigateBack({ delta: 1 });
            } else {
              wx.showToast({
                title: res.data.message || '发布失败',
                icon: 'none'
              });
            }
          },
          fail() {
            wx.showToast({
              title: '网络错误，请稍后再试',
              icon: 'none'
            });
          }
        });
      },
      fail: () => {
        wx.showToast({
          title: '未登录或学号未找到',
          icon: 'none'
        });
      }
    });
  }
});