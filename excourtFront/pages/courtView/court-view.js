// pages/court-view/court-view.js
Page({
    /**
     * 页面的初始数据
     */
    data: {
        student_id:'',
        days:[],
        daystrings:[],
        courtNames:[],
        weekCourtSlots:[],
        hours:[],
        exchangeable_courtid:[],
        teamupable_courtid:[],
        receivable_courtid:[],
        placeName:'',
        statColor:{
          '接受送场':'#FFCC00',
          '组队拼场':'#CC99CC',
          '我的场地':'#99CCFF',
          '交换场地':'#FF9999'
        },
        curDay: 0,
        statusOptions: ['接受送场', '组队拼场', '我的场地', '交换场地'],
        selectedStatus: '', // 当前选中的状态
        filteredCourtSlots: [], // 根据状态筛选后的场地数据
        overlayImage: '',
    },
  
    /**
     * 生命周期函数--监听页面加载
     */
    onLoad(options) {
      wx.getStorage({key: 'student_id',success: (res) => {
        this.initSlot();
        console.log('获取到学号:', res.data);
        this.setData({student_id: res.data});
        this.setData({placeName:'嘉定羽毛球场'});
        this.initDays();
        this.getExchangeablecourts();
        this.getTeamupablecourts();
        this.getReceiveablecourts();
        this.updateCourtGrid(new Date());
        console.log(this.data.weekCourtSlots)
      },
      fail: () => {wx.showToast({title: '未登录或学号未找到',icon: 'none'});}});

    },
    initDays() {
      const currentDate = new Date();
      const days = [];
      const weekdays = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
      const daystrings = [];
      for (let i = 0; i < 7; i++) {
        const nextDate = new Date(currentDate);
        nextDate.setDate(currentDate.getDate() + i);
        const year = nextDate.getFullYear();
        const month = (nextDate.getMonth() + 1).toString().padStart(2, '0'); // 月份从0开始
        const day = nextDate.getDate().toString().padStart(2, '0');
        const weekDay = weekdays[nextDate.getDay()];
        days.push({
          day: weekDay,
          date: month+'/'+day,
          active: i===0
        });
        daystrings.push(
          year+'/'+month+'/'+day
        );
      }
      this.setData({ days,daystrings });
    },
    selectDay(e) {
      const index = e.currentTarget.dataset.index;
      const days = this.data.days.map((day, i) => {
        day.active = i === index;
        return day;
      });
      this.setData({ days });
      this.updateCourtGrid(new Date(new Date().setDate(new Date().getDate() + index)));
    },
    updateCourtGrid(date) {
      const that = this;
      //const selectedDate = date.toISOString().split('T')[0]; // 选择的日期，格式为 YYYY-MM-DD
        wx.request({
            url: 'http://123.60.86.239:8000/student/owned-courts', // 替换为实际的后端接口地址
            method: 'POST',
            data: {
                student_id: this.data.student_id, 
            },
            success:(res)=> {
              //console.log(student_id)
                if (res.statusCode === 200) {
                  let courts = res.data.owned_courts;
                  console.log(courts)
                  const courtNames = ["场地1", "场地2", "场地3", "场地4", "场地5","场地6"];
                  const weekCourtSlots=this.data.weekCourtSlots
                  const hours = [];
                  for(let hour = 9;hour<=21;hour++){
                    if(hour==9)hours.push(`0${hour}:00`);
                    else hours.push(`${hour}:00`);
                  }
                  //console.log(weekCourtSlots)
                  for(let i = 0;i<courts.length;i++){
                    for(let j = 0;j<courtNames.length;j++){
                      if(courtNames[j]==courts[i].Court_no)courts[i].courtId=j;
                    }
                    courts[i].timeId=courts[i].Court_time;
                    courts[i].status='我的场地';
                    weekCourtSlots[courts[i].dayId].push(courts[i])
                  }
                  //console.log(weekCourtSlots)
                  this.setData({
                    hours:hours,
                    courtNames:courtNames,
                    weekCourtSlots:weekCourtSlots
                  })
                } else {
                    wx.showToast({
                        title: '获取场地数据失败',
                        icon: 'none'
                    });
                }
            },
            fail:()=> {
                wx.showToast({
                    title: '请求失败，请稍后再试',
                    icon: 'none'
                });
            }
        });
    },
    changeNav(event){
      const newIndex = event.currentTarget.dataset.index;
      //console.log(newIndex);
      this.setData({curDay:newIndex});
    },
    BlockClick:function(event){
      const status = event.currentTarget.dataset.status;
      const slotdata = event.currentTarget.dataset;
      console.log(slotdata)
      if (!status) {
        wx.showToast({
          title: '无法选择',
          icon: 'none',
        });
        return;
      }
      switch(status){
        case '接受送场':
          // 弹出对话框，选择是否跳转到送场交易页面
          wx.showModal({
            title: '接受送场',
            content: '是否接受送场？',
            success (res) {
              if (res.confirm) {
                wx.navigateTo({
                url: '/pages/acceptOffer/acceptOffer?courtname='
                +slotdata.courtname+'&schoolname='+slotdata.schoolname
                +'&date='+slotdata.datestring+'&ownername='+slotdata.ownername
                +'&timeid='+slotdata.timeid+'&courtid='+slotdata.courtid
                })
              } else if (res.cancel) {
              // 用户点击取消
                wx.showToast({
                  title: '取消接受送场操作',
                  icon: 'none'
                });
              }
            }
          });
          break;
        case '组队拼场':
          // 弹出对话框，选择是否跳转到加入交易页面
          wx.showModal({
            title: '组队拼场',
            content: '是否加入该场次？',
            success (res) {
              if (res.confirm) {
                wx.navigateTo({
                  url: '/pages/joinIn/joinIn',
                  url: '/pages/joinIn/joinIn?courtname='
                +slotdata.courtname+'&schoolname='+slotdata.schoolname
                +'&date='+slotdata.datestring+'&ownername='+slotdata.ownername
                +'&timeid='+slotdata.timeid+'&courtid='+slotdata.courtid
                })
              } else if (res.cancel) {
                // 用户点击取消
                wx.showToast({
                  title: '取消加入操作',
                  icon: 'none'
                });
              }
            }
          });
          break;
        case '我的场地':
          // 弹出对话框，询问是否跳转到场地信息页面
          wx.showModal({
            title: '我的场地',
            content: '是否查看已预约场地信息？',
            success (res) {
              if (res.confirm) {
                // 用户点击确定，跳转到场地信息页面
                wx.navigateTo({
                  url: '/pages/3-teamUp/teamUp?Court_id='+slotdata.courtid // 这里填写场地信息页面的路径
                });
              } else {
                wx.showToast({
                  title: '取消查看场地信息',
                  icon: 'none'
                });
              }
            }
          });
          break;
        case '交换场地':
          // 弹出对话框，询问是否跳转到交换交易页面
          wx.showModal({
            title: '交换场地',
            content: '是否与该场次预约方交换场次？',
            success (res) {
              if (res.confirm) {
                // 用户点击确定，跳转到交换交易页面
                wx.navigateTo({
                  url: '/pages/2-exchange/index?Court_id='+slotdata.courtid // 这里填写交换交易页面的路径
                });
              } else {
                wx.showToast({
                  title: '取消交换操作',
                  icon: 'none'
                });
              }
            }
          });
          break;
        default:
          wx.showToast({
            title: '未知状态',
            icon: 'none'
          });
          break;
      }
    },
    /*处理单选项变化*/
    onStatusChange(e) {
      const selectedStatus = e.detail.value; // 获取用户选择的状态
      this.setData({ selectedStatus });
      let overlayImage = '';
      switch (selectedStatus) {
        case '接受送场':
          overlayImage = '/images/SendLogo.png';
          break;
        case '组队拼场':
          overlayImage = '/images/JoinLogo.png';
          break;
        case '我的场地':
          overlayImage = '/images/MyCourt.png';
          break;
        case '交换场地':
          overlayImage = '/images/ChangeLogo.png';
          break;
        default:
          overlayImage = ''; // 默认不显示图片
      }
    
      this.setData({ overlayImage });
      this.updateFilteredCourtSlots(selectedStatus);
    },    
    /*更新筛选后的场地数据*/
    updateFilteredCourtSlots(selectedStatus) {
      const { weekCourtSlots, curDay } = this.data;
    
      if (!selectedStatus) {
        // 如果未选择状态，则显示全部白色
        this.setData({ filteredCourtSlots: weekCourtSlots[curDay].map(item => ({ ...item, status: '' })) });
        return;
      }
    
      // 筛选出选中状态的场次
      const filteredSlots = weekCourtSlots[curDay].map(item => {
        return {
          ...item,
          status: item.status === selectedStatus ? selectedStatus : '', // 其他状态设为空
        };
      });
    
      this.setData({ filteredCourtSlots: filteredSlots });
    },
    getExchangeablecourts(){
      wx.request({
        url: 'http://123.60.86.239:8000/student/get_exchangecourt', // 替换为实际的后端接口地址
        method: 'POST',
        data: {
            my_id: this.data.student_id, 
        },
        success:(res)=> {
            if (res.statusCode === 200) {
              this.data.exchangeable_courtid = res.data.court_ids_list;
              //console.log(this.data.exchangeable_courtid)
              this.courtid2weekslot(this.data.exchangeable_courtid,"交换场地")
            } else {
                wx.showToast({
                    title: '获取可交换场地数据失败',
                    icon: 'none'
                });
            }
        },
        fail:()=> {
            wx.showToast({
                title: '请求失败，请稍后再试',
                icon: 'none'
            });
        }
    });
    },
    getTeamupablecourts(){
      wx.request({
        url: 'http://123.60.86.239:8000/student/get_teamupcourt', // 替换为实际的后端接口地址
        method: 'POST',
        data: {
            my_id: this.data.student_id, 
        },
        success:(res)=> {
            if (res.statusCode === 200) {
              this.data.teamupable_courtid = res.data.court_ids_list;
              //console.log(this.data.teamupable_courtid)
              this.courtid2weekslot(this.data.teamupable_courtid,"组队拼场")
            } else {
                // wx.showToast({
                //     title: '获取可加入场数据失败',
                //     icon: 'none'
                //  });
            }
        },
        fail:()=> {
            wx.showToast({
                title: '请求失败，请稍后再试',
                icon: 'none'
            });
        }
    });
    },
    getReceiveablecourts(){
      wx.request({
        url: 'http://123.60.86.239:8000/student/get_offercourt', // 替换为实际的后端接口地址
        method: 'POST',
        data: {
            my_id: this.data.student_id, 
        },
        success:(res)=> {
            if (res.statusCode === 200) {
              this.data.receiveable_courtid = res.data.court_ids_list;
              //console.log(this.data.receiveable_courtid)
              this.courtid2weekslot(this.data.receiveable_courtid,"接受送场")
            } else {
                // wx.showToast({
                //     title: '获取可加入场数据失败',
                //     icon: 'none'
                // });
            }
        },
        fail:()=> {
            wx.showToast({
                title: '请求失败，请稍后再试',
                icon: 'none'
            });
        }
      });
    },
    /**
     * 生命周期函数--监听页面初次渲染完成
     */
    onReady() {
  
    },
  
    /**
     * 生命周期函数--监听页面显示
     */
    onShow() {
  
    },
  
    /**
     * 生命周期函数--监听页面隐藏
     */
    onHide() {
  
    },
  
    /**
     * 生命周期函数--监听页面卸载
     */
    onUnload() {
  
    },
  
    /**
     * 页面相关事件处理函数--监听用户下拉动作
     */
    onPullDownRefresh() {
  
    },
  
    /**
     * 页面上拉触底事件的处理函数
     */
    onReachBottom() {
  
    },
  
    /**
     * 用户点击右上角分享
     */
    onShareAppMessage() {
  
    },
    initSlot(){
      const weekCourtSlots = [];
      for(let day = 0;day<7;day++){
        const dailyslots = []
        weekCourtSlots.push(dailyslots)
      }
      this.setData({weekCourtSlots:weekCourtSlots})
    },
    courtid2weekslot(id_list,sta){
      const weekSlots = this.data.weekCourtSlots;
      console.log(weekSlots)
      console.log('daystrings:',this.data.daystrings)
      console.log('days',this.data.days)
      for(let i =0;i<id_list.length;i++){
        const id=id_list[i].court_id
        const slot = {}
        const parts = id.split('-')
        //console.log(parts)
        const idday = parts[2]+'/'+parts[3];
        let flag=0
        for(let j=0;j<7;j++){
          if(this.data.days[j].date==idday){slot.dayId=j;flag=1}
        }
        
        if(flag){slot.Court_id = id;
        slot.timeId = Number(parts[4])
        slot.courtId = Number(parts[5])
        slot.status = sta
        console.log(slot)
        weekSlots[slot.dayId].push(slot)}
      }
      this.setData({weekCourtSlots:weekSlots})
    }
  })
 