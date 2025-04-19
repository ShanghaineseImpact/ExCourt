Page({
  data: {
    lostItems: [], // 初始化为空，数据从后端获取
    searchQuery: "", // 搜索关键词
  },

  // 页面加载时获取后端数据
  onLoad() {
    this.fetchLostItems();
  },

  // 从后端获取失物数据
  fetchLostItems() {
    const that = this;
    wx.request({
      url: 'http://123.60.86.239:8000/lost_and_found/lost/getall', // 替换为实际的后端接口地址
      method: 'POST',
      success(res) {
        if (res.statusCode === 200) {
          that.setData({
            lostItems: res.data.lost_items.map(item => ({
              id: item.Lost_id,
              name: item.Lost_item_name,
              description: item.Lost_description,
              lostTime: item.Lost_time,
              lostLocation: item.Lost_position,
              image: item.Lost_item_pic_url,
              contact: item.Lost_contact,
              losttime:that.formatDate(item.Lost_time)
            })),
          });
          that.getUrl()
          //console.log(this.data.lostItems)
        } else {
          console.error("Failed to fetch lost items:", res.data.message);
        }
      },
      fail(error) {
        console.error("Error fetching lost items:", error);
      },
    });
  },
  getUrl(){
    const list = this.data.lostItems
    for(let i=0;i<list.length;i++)
    wx.request({
      url: 'http://123.60.86.239:8000/upload/find_lost',
      method:'POST',
      data:{Lost_id:list[i].id},
      success:(res)=>{
        console.log(res.data)
        list[i].image=res.data.imageUrl
        this.setData({lostItems:list})
      },
      fail:(err)=>{
        console.log(err)
      }
    })
  },

  toggleOptions(e) {
    const id = e.currentTarget.dataset.id;
    const updatedItems = this.data.lostItems.map(item => {
      if (item.id === id) {
        return { ...item, showOptions: !item.showOptions };
      }
      return item;
    });
    this.setData({ lostItems: updatedItems });
  },

  claimItem(e) {
    const id = e.currentTarget.dataset.id;
    const updatedItems = this.data.lostItems.map(item => {
      if (item.id === id) {
        return { ...item, claimed: true, showOptions: false };
      }
      return item;
    });
    this.setData({ lostItems: updatedItems });
  },

  appealItem(e) {
    const id = e.currentTarget.dataset.id;
    // 处理错领申诉逻辑
  },

  onSearchInput(event) {
    this.setData({ searchQuery: event.detail.value });
  },

  onSearch() {
    const filteredItems = this.data.lostItems.filter(item =>
      item.name.includes(this.data.searchQuery) || item.description.includes(this.data.searchQuery)
    );
    this.setData({ lostItems: filteredItems });
  },

  navigateToClaim() {
    wx.navigateTo({ url: '/pages/4-claim/claim' });
  },

  navigateToAppeal() {
    wx.navigateTo({ url: '/pages/4-misclaim/misclaim' });
  },

  navigateToPublish() {
    wx.navigateTo({ url: '/pages/4-publishLost/publishLost' });
  },
  // 格式化日期方法
  formatDate(dateTime) {
    const date = new Date(dateTime);
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
});
