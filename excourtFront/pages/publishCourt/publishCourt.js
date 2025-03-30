// pages/3-publishCourt/publishCourt.js
Page({
  data: {
    campusArray: ['嘉定', '四平', '沪西', '彰武'],
    courtNumberArray: ['1号', '2号', '3号', '4号', '5号'],
    maxParticipantsArray: ['1', '2', '3', '4'],
    timeArray: ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'],
    selectedCampus: '请选择校区',
    selectedCourtNumber: '请选择场地号',
    selectedMaxParticipants: '最多加入人数',
    selectedStartDate: '选择起始日期',
    selectedStartTime: '选择起始时间',
    selectedEndDate: '选择结束日期',
    selectedEndTime: '选择结束时间',
    student_id: '',
    Max_num: '',
    courtId: null, // 传递过来的场地ID
    timeId: null, // 传递过来的时间段ID
    dateString: '' // 传递过来的日期字符串
  },

  onLoad(options) {
    // 页面加载时获取传递的参数
    wx.getStorage({
      key: 'student_id',
      success: (res) => {
        this.setData({ student_id: res.data });
        this.setData({
          courtId: options.courtId,
          dateString: decodeURIComponent(options.dateString || ''),
          selectedCourtNumber: this.data.courtNumberArray[this.data.courtId] || '请选择场地号',
          selectedStartTime: this.data.timeArray[this.data.timeId] || '选择起始时间',
          selectedStartDate: this.data.dateString
        });
        console.log(this.data.student_id);
        console.log(this.data.courtId);
      },
      fail: () => {
        wx.showToast({ title: '未登录或学号未找到', icon: 'none' });
      }
    });
  },

  // 上传二维码事件
  uploadQRCode: function () {
    wx.showToast({
      title: '二维码上传功能待开发',
      icon: 'none'
    });
  },

  // 选择最多希望加入人数事件
  bindMaxParticipantsChange: function (e) {
    this.data.Max_num = this.data.maxParticipantsArray[e.detail.value];
    console.log(this.data.Max_num);
  },

  // 确定按钮事件
  submitForm: function (e) {
    // 检查最大加入人数是否已选择
    if (!this.data.Max_num) {
      wx.showToast({
        title: '请先选择最大加入人数',
        icon: 'none',
        duration: 2000
      });
      return; // 如果没有选择最大人数，直接返回
    }

    // 提交请求到后端
    wx.request({
      url: 'http://123.60.86.239:8000/teamup/upload',  // 这里替换成实际的后端 API 地址
      method: 'POST',
      data: {
        Student_id: this.data.student_id,
        Court_id: this.data.courtId,
        Max_num: this.data.Max_num
      },
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 402) {
          // 如果后端返回402，表示该用户已发布过其他上传请求，进行提示
          wx.showToast({
            title: '您已发布过该场地的上传请求',
            icon: 'none',
            duration: 2000
          });
        } else if (res.statusCode === 201) {
          // 如果请求成功，显示成功消息
          wx.showToast({
            title: '发布拼场成功',
            icon: 'success',
            duration: 2000,
            success: () => {
              // 2秒后返回组队页面
              setTimeout(() => {
                wx.navigateBack();
              }, 2000);
            }
          });
        } else {
          // 其他情况
          wx.showToast({
            title: '发布失败，请稍后重试',
            icon: 'none',
            duration: 2000
          });
        }
      },
      fail: (err) => {
        // 网络请求失败的情况
        wx.showToast({
          title: '请求失败，请检查网络连接',
          icon: 'none',
          duration: 2000
        });
      }
    });
  }
});