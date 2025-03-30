// pages/teamUp/teamUp.js
Page({
  data: {
    uploader_id: '',
    courtId: '',
    timeId: '',
    dateString: '',
    // 其他数据...
  },

  onLoad(options) {
    this.setData({
      courtId: options.Court_id || '',
    });
    console.log(this.data.courtId);
  },

  publishCourt: function() {
    wx.navigateTo({
      url: `/pages/3-publishCourt/publishCourt?courtId=${this.data.courtId}&timeId=${this.data.timeId}&dateString=${encodeURIComponent(this.data.dateString)}`
    });
  },

  applyCourt: function() {
    wx.showModal({
      title: '确认操作',
      content: '您确定要发布换场吗？',
      showCancel: true,
      cancelText: '取消',
      confirmText: '确认',
      success: (res) => {
        if (res.confirm) {
          console.log('用户确认发布换场');
          this.publishCourtChange();
        } else {
          console.log('用户取消了发布换场');
        }
      },
      fail: (err) => {
        console.error('弹窗调用失败', err);
      }
    });
  },

  offerCourts: function() {
    wx.showModal({
      title: '确认操作',
      content: '您确定要发布送场吗？',
      showCancel: true,
      cancelText: '取消',
      confirmText: '确认',
      success: (res) => {
        if (res.confirm) {
          console.log('用户确认发布送场');
          this.offerCourt();
        } else {
          console.log('用户取消了发布送场');
        }
      },
      fail: (err) => {
        console.error('弹窗调用失败', err);
      }
    });
  },

  publishCourtChange: function () {
    console.log('发布换场操作执行中...');
    wx.getStorage({
      key: 'student_id',
      success: (storageRes) => {
        this.data.uploader_id = storageRes.data;
        console.log(this.data.uploader_id);
        console.log(this.data.courtId);

        wx.request({
          url: 'http://123.60.86.239:8000/exchangecourt/upload',
          method: 'POST',
          data: {
            Exchange_uploader_id: this.data.uploader_id,
            Exchange_uploaded_court_id: this.data.courtId
          },
          success: (apiRes) => {
            if (apiRes.statusCode === 402) {
              wx.showToast({
                title: '您已发布过该场地的上传请求',
                icon: 'none',
                duration: 2000
              });
            } else if (apiRes.statusCode === 201) {
              wx.showToast({
                title: '换场请求已发起',
                icon: 'success',
                duration: 2000
              });
              console.log('换场成功，场地ID:', this.data.courtId);
            } else {
              wx.showToast({
                title: apiRes.data.message || '换场请求失败',
                icon: 'none'
              });
            }
          },
          fail: (err) => {
            wx.showToast({
              title: '网络错误，请稍后再试',
              icon: 'none'
            });
            console.error('请求失败:', err);
          }
        });
      },
      fail: () => {
        wx.showToast({
          title: '用户未登录，请重新登录',
          icon: 'none'
        });
      }
    });
  },

  offerCourt: function () {
    console.log('发布送场操作执行中...');
    wx.getStorage({
      key: 'student_id',
      success: (storageRes) => {
        this.data.uploader_id = storageRes.data;
        console.log(this.data.uploader_id);
        console.log(this.data.courtId);

        wx.request({
          url: 'http://123.60.86.239:8000/offercourt/upload',
          method: 'POST',
          data: {
            my_id: this.data.uploader_id,
            court_id: this.data.courtId
          },
          success: (apiRes) => {
            if (apiRes.statusCode === 402) {
              wx.showToast({
                title: '您已发布过该场地的上传请求',
                icon: 'none',
                duration: 2000
              });
            } else if (apiRes.statusCode === 201) {
              wx.showToast({
                title: '送场请求已发起',
                icon: 'success',
                duration: 2000
              });
              console.log('送场成功，场地ID:', this.data.courtId);
            } else {
              wx.showToast({
                title: apiRes.data.message || '送场请求失败',
                icon: 'none'
              });
            }
          },
          fail: (err) => {
            wx.showToast({
              title: '网络错误，请稍后再试',
              icon: 'none'
            });
            console.error('请求失败:', err);
          }
        });
      },
      fail: () => {
        wx.showToast({
          title: '用户未登录，请重新登录',
          icon: 'none'
        });
      }
    });
  },

  handleCourts: function() {
    wx.navigateTo({
      url: `/pages/3-handleCourts/handleCourts?courtId=${this.data.courtId}&timeId=${this.data.timeId}&dateString=${encodeURIComponent(this.data.dateString)}`
    });
  },

  evaluateTeam: function() {
    wx.showModal({
      title: '撤销预约',
      content: '是否撤销预约？',
      success(res) {
        if (res.confirm) {
          wx.showToast({
            title: '撤销成功',
            icon: 'none'
          });
        } else {
          wx.showToast({
            title: '取消撤销',
            icon: 'none'
          });
        }
      }
    });
  },

  evaluate: function() {
    wx.navigateTo({
      url: `/pages/evaluate/evaluate?courtId=${this.data.courtId}&timeId=${this.data.timeId}&dateString=${encodeURIComponent(this.data.dateString)}`
    });
  }
});