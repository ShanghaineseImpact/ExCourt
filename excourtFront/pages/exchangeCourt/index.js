Page({
  data: {
    courtList: [],
    student_id: '',  // 用于存储学生学号
    court_id:''
  },

  // 页面加载时获取用户的 student_id 并请求后端
  onLoad: function(ops) {
    this.setData({court_id:ops.Court_id})
    console.log(this.data.court_id)
    wx.getStorage({
      key: 'student_id',  // 获取存储的 student_id
      success: (res) => {
        const my_id = res.data;  // 获取到的 student_id
        this.setData({ student_id: my_id });  // 存储 student_id
        this.fetchAvailableCourts(my_id);  // 获取用户可用的场地
      },
      fail: () => {
        wx.showToast({
          title: '未找到用户信息，请重新登录',
          icon: 'none',
          duration: 2000
        });
      }
    });
  },

  // 请求可用的场地数据
  fetchAvailableCourts: function(my_id) {
    wx.request({
      url: 'http://123.60.86.239:8000/student/get_available_courts',  // 后端接口地址
      method: 'POST',
      data: { my_id: my_id },
      header: {
        'Content-Type': 'application/json',
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.available_courts) {
          res.data.available_courts.map(court_id => {
            this.formatCourtId(court_id);  // 格式化场地ID
          });
          console.log(this.data.courtList)
        } else {
          wx.showToast({
            title: '没有找到可用的场地',
            icon: 'none',
            duration: 2000
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '获取数据失败，请稍后再试',
          icon: 'none',
          duration: 2000
        });
      }
    });
  },

  // 格式化 court_id 显示为更友好的格式
  formatCourtId: function(court_id) {
    const parts = court_id.split('-');
    if (parts.length !== 6) return court_id;  // 如果格式不正确，则直接返回原始 court_id

    const campus = parts[0];  // 校区
    const year = parts[1];  // 年
    const month = parts[2];  // 月
    const day = parts[3];  // 日
    const timeSlot = parts[4];  // 选取时间段的第一位（0-12映射到9:00-21:00）
    const courtNumber = parts[5];  // 场地号（0-5映射到场地1-场地6）
    const timeSlots = [
      "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00"
    ];
    const formattedTime = timeSlots[Number(timeSlot)];  // 将时间段映射为具体时间
    const formattedCourtNumber = Number(courtNumber) + 1;  // 场地号（0-5映射到场地1-6）

    let slot = {
      court_info:"嘉定校区"+" "+"场地"+formattedCourtNumber+"\n"+month+'月'+day+'日'+" "+formattedTime+'-'+timeSlots[Number(timeSlot)+1],
      court_id:court_id
    }
    const list = this.data.courtList;
    list.push(slot);
    this.setData({courtList: list});
  },

  // 处理点击某一场地记录
  onCourtItemTap: function (e) {
    const index = e.currentTarget.dataset.index;
    const courtList = this.data.courtList;

    // 清除所有场地的选中状态
    courtList.forEach((item, idx) => {
      item.selected = idx === index;  // 只选择点击的记录
    });

    // 更新数据
    this.setData({
      courtList: courtList
    });
  },

  // 发布换场请求
  onSubmitRequest: function () {
    const selectedCourt = this.data.courtList.find(item => item.selected);

    if (!selectedCourt) {
      wx.showToast({
        title: '请选择一个场次',
        icon: 'none',
        duration: 2000
      });
      return;
    }

    const { student_id } = this.data;
    const exchange_responser_id = student_id;  // 响应者学号（需要根据实际逻辑设定）
    const exchange_uploader_court_id = this.data.court_id;  // 发布者选择的场地ID
    const exchange_responser_court_id = selectedCourt.court_id;  // 响应者选择的场地ID（此处假设和发布者一样）

    // 向后端提交换场请求
    wx.request({
      url: 'http://123.60.86.239:8000/exchangecourt/respond',  // 后端接口地址
      method: 'POST',
      data: {
        Exchange_responser_id: exchange_responser_id,
        Exchange_uploader_court_id: exchange_uploader_court_id,
        Exchange_responser_court_id: exchange_responser_court_id
      },
      header: {
        'Content-Type': 'application/json',
      },
      success: (res) => {
        if (res.statusCode === 201) {
          wx.showToast({
            title: '换场请求已提交',
            icon: 'success',
            duration: 2000
          });
          console.log('换场请求已提交:', res.data);
        } else {
          wx.showToast({
            title: res.data.message || '请求失败',
            icon: 'none',
            duration: 2000
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '请求失败，请稍后再试',
          icon: 'none',
          duration: 2000
        });
      }
    });
  }
});