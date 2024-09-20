<!--  
关键部分说明:

1. sendMessage 方法: 通过 fetch 向后端发送用户输入的问题，并使用 getReader() 方法逐字接收后端返回的内容。
将用户的问题先行显示在对话框中，然后逐字接收助手的回复内容并逐步更新。

2. updateAssistantMessage 方法: 该方法确保每次有新内容时，助手的回复内容会被更新。如果助手的回复是新消息，它会被添加到聊天记录中。如果已经存在部分助手消息，则会对其进行更新。

3. UI 样式: 会话的左侧显示为列表，右侧为选中的会话的聊天记录区域。
通过简单的样式控制布局和显示，增强了可读性。 

-->

<template>
  <div class="chat-wrapper">
    <!-- 左边对话选择区域 -->
    <div class="chat-list">
      <button @click="startNewChat" class="new-chat-btn">新建会话</button>
      <input type="text" v-model="searchQuery" placeholder="搜索会话" class="search-input"/>
      <div v-for="(chat, index) in filteredChats" :key="index" class="chat-item">
        <div @click="selectChat(chat)" :class="{'active-chat': activeChat === chat}">
          {{ chat.name }}
        </div>
        <button @click="deleteChat(index)" class="delete-btn">删除</button>
      </div>
    </div>

    <!-- 右边聊天区域 -->
    <div class="chat-content" v-if="activeChat">
      <div class="message-log">
        <div v-for="(message, index) in activeChat.messages" :key="index">
          {{ message }}
        </div>
      </div>
      <div class="message-input">
        <textarea v-model="inputMessage" placeholder="请输入消息" class="message-textarea"></textarea>
        <!-- 发送按钮，发送消息后禁用按钮，直到服务器响应 -->
        <button @click="sendMessage" :disabled="isLoading" class="send-btn">发送</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      // 保存所有会话信息，包含每个会话的名称和消息记录
      chats: [
        { name: '会话1', messages: ['---- 会话内容 ----'] }, // 默认建立的会话和消息
      ],
      activeChat: null, // 当前激活的会话
      searchQuery: '', // 搜索框的输入内容
      inputMessage: '', // 用户输入的消息
      isLoading: false // 控制是否正在加载（防止重复发送）
    };
  },
  computed: {
    // 根据搜索框的内容过滤会话列表，返回匹配的会话
    filteredChats() {
      return this.chats.filter(chat => chat.name.includes(this.searchQuery));
    }
  },
  methods: {
    // 选择会话，激活后会显示该会话的聊天记录
    selectChat(chat) {
      this.activeChat = chat;
    },

    // 新建会话，创建新会话并自动激活该会话
    startNewChat() {
      const newChat = { name: `会话${this.chats.length + 1}`, messages: ['---- 会话内容 ----'] }; // 添加默认消息
      this.chats.push(newChat); // 将旧会话添加到会话列表中
      this.selectChat(newChat); // 激活新会话
    },

    // 删除会话，从会话列表中移除指定的会话
    deleteChat(index) {
      if (this.activeChat === this.chats[index]) {
        this.activeChat = null; // 如果删除的是当前激活的会话，清除激活状态
      }
      this.chats.splice(index, 1); // 删除会话
    },

    // 发送消息
    async sendMessage() {
      if (!this.inputMessage.trim()) return; // 如果消息为空，不发送

      // 将用户输入的消息添加到当前会话的消息记录中
      this.activeChat.messages.push(`<我>: ${this.inputMessage}`);
      this.isLoading = true;

      try {
        // 向后端发送用户输入的问题
        const response = await fetch('http://127.0.0.1:8000/api/chat/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ question: this.inputMessage }), // 将问题以 JSON 格式发送
        });

        if (!response.ok) {
          throw new Error('发送失败');
        }

        // 使用 TextDecoder 读取逐字返回的数据
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let done = false;
        let accumulatedMessage = ''; // 累积逐字返回的消息内容

        // 循环读取服务器逐字返回的数据，直到所有数据都返回
        while (!done) {
          const { value, done: readerDone } = await reader.read();
          done = readerDone;

          const chunk = decoder.decode(value, { stream: true }); // 解码数据
          const processedChunk = chunk.replace(/^data: /gm, ''); // 去掉 "data: " 前缀

          accumulatedMessage += processedChunk; // 累积消息内容

          // 每次有新数据时，更新聊天记录
          this.updateAssistantMessage(accumulatedMessage);
        }
      } catch (error) {
        console.error('Error:', error);
      } finally {
        this.isLoading = false; // 请求结束后启用发送按钮
        this.inputMessage = ''; // 清空输入框
      }
    },

     // 更新助手消息，显示逐字返回的内容
    updateAssistantMessage(content) {
      if (this.activeChat) {
        // 如果最后一条消息不是助手的消息，则添加新的助手消息
        if (!this.activeChat.messages[this.activeChat.messages.length - 1].startsWith('<GPT-4o>:')) {
          this.activeChat.messages.push(`<GPT-4o>: ${content}`);
        } else {
          // 如果最后一条已经是助手的消息，则更新这条消息
          this.activeChat.messages[this.activeChat.messages.length - 1] = `<GPT-4o>: ${content}`;
        }
      }
    }
  }
};
</script>

<style scoped>
/* 主要样式定义 */
.chat-wrapper {
  display: flex;
  height: 100vh;
}

/* 左侧会话列表区域 */
.chat-list {
  width: 30%;
  background-color: #1e1e1e;
  padding: 10px;
}

.new-chat-btn {
  width: 100%;
  padding: 10px;
  background-color: #333;
  color: #fff;
  border: 1px solid #444;
  margin-bottom: 10px;
}

.search-input {
  width: 90%;
  padding: 8px;
  margin-bottom: 10px;
  border: 1px solid #444;
  background-color: #2c2c2c;
  color: #fff;
  border-radius: 4px;
}

.chat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #444;
  cursor: pointer;
}

.chat-item div {
  flex: 1;
  color: #fff;
}

.delete-btn {
  background-color: #ff4d4f;
  border: none;
  color: white;
  padding: 4px 10px;  /* 调整内边距，使按钮更小 */
  cursor: pointer;
  font-size: 12px;    /* 控制字体大小 */
  border-radius: 4px; /* 添加圆角 */
}

.active-chat {
  background-color: #333;
  border-left: 4px solid #007bff;
}

/* 右侧聊天显示区域 */
.chat-content {
  width: 70%;
  padding: 10px;
  background-color: #2c2c2c;
}

.message-log {
  height: 80%;
  overflow-y: auto;
  margin-bottom: 10px;
  background-color: #1e1e1e;
  padding: 10px;
  color: #fff;
}

.message-input {
  display: flex;
}

.message-textarea {
  flex: 1;
  padding: 10px;
  border: 1px solid #444;
  background-color: #333;
  color: #fff;
  border-radius: 4px;
}

.send-btn {
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  margin-left: 10px;
}

.send-btn:disabled {
  background-color: #ccc;
}
</style>