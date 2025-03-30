// pages/6-historyRecord/historyRecord.js
Page({
    data: {
      historyRecords: [
        // 示例数据，实际应用中应从服务器获取
        {
          campus: '嘉定',
          courtNumber: '1号',
          maxParticipants: '4',
          startDate: '2024-10-25',
          startTime: '09:00',
          endTime: '10:00',
          isTeamup: true,
          isMisclaim: false
        },
        {
            campus: '四平',
            courtNumber: '2号',
            maxParticipants: '3',
            startDate: '2024-10-23',
            startTime: '13:00',
            endTime: '14:00',
            isTeamup: false,
            isMisclaim: false
          },
        // ...更多历史记录
      ]
    },
  
    onLoad: function() {
      // 页面加载时获取历史记录数据
      // 此处省略了实际的网络请求代码
    }
  });