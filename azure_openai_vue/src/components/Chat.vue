<template>
  <div class="chat-wrapper">

    <!-- 左侧对话选择区域 -->
    <div class="chat-list">
      <button @click="startNewChat" class="new-chat-btn">新建会话</button>
      <input type="text" v-model="searchQuery" placeholder="搜索会话" class="search-input" />
      <div v-for="(chat, index) in filteredChats" :key="index" class="chat-item">
        <div @click="selectChat(chat)" :class="{'active-chat': activeChat === chat}">
          {{ chat.name }}
        </div>
        <button @click="deleteChat(index)" class="delete-btn">删除</button>
      </div>
    </div>

    <!-- 右侧聊天区域 -->
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

<script setup>
import { ref, computed } from 'vue';

// 响应式数据
const chats = ref([
  { name: '会话1', messages: ['---- 会话内容 ----'] }, // 默认会话及内容
]);

const activeChat = ref(null); // 当前激活的会话
const searchQuery = ref(''); // 搜索框的输入内容
const inputMessage = ref(''); // 用户输入的消息
const isLoading = ref(false); // 控制是否正在加载（防止重复发送）

// 根据搜索框内容过滤会话
const filteredChats = computed(() => {
  return chats.value.filter(chat => chat.name.includes(searchQuery.value));
});

// 选择会话，激活后显示该会话的聊天记录
const selectChat = (chat) => {
  activeChat.value = chat;
};

// 新建会话，创建并激活新会话
const startNewChat = () => {
  const newChat = { name: `会话${chats.value.length + 1}`, messages: ['---- 会话内容 ----'] };
  chats.value.push(newChat); // 将新会话加入会话列表
  selectChat(newChat); // 激活新会话
};

// 删除会话，从会话列表中移除指定的会话
const deleteChat = (index) => {
  if (activeChat.value === chats.value[index]) {
    activeChat.value = null; // 如果删除的是当前激活的会话，清除激活状态
  }
  chats.value.splice(index, 1); // 删除会话
};

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return; // 消息为空不发送

  // 将用户输入的消息添加到当前会话的消息记录中
  activeChat.value.messages.push(`<我>: ${inputMessage.value}`);
  isLoading.value = true;

  try {
    // 向后端发送用户输入的问题
    const response = await fetch('http://127.0.0.1:8000/api/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question: inputMessage.value }),
    });

    if (!response.ok) {
      throw new Error('发送失败');
    }

    // 使用 TextDecoder 读取逐字返回的数据
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let done = false;
    let accumulatedMessage = ''; // 累积逐字返回的消息内容

    // 循环读取服务器逐字返回的数据，直到所有数据返回完毕
    while (!done) {
      const { value, done: readerDone } = await reader.read();
      done = readerDone;

      const chunk = decoder.decode(value, { stream: true }); // 解码数据
      const processedChunk = chunk.replace(/^data: /gm, ''); // 去掉 "data: " 前缀

      accumulatedMessage += processedChunk; // 累积消息内容
      updateAssistantMessage(accumulatedMessage); // 每次有新数据时更新聊天记录
    }
  } catch (error) {
    console.error('Error:', error);
  } finally {
    isLoading.value = false; // 请求结束后启用发送按钮
    inputMessage.value = ''; // 清空输入框
  }
};

// 更新助手消息，显示逐字返回的内容
const updateAssistantMessage = (content) => {
  if (activeChat.value) {
    // 如果最后一条消息不是助手的消息，则添加新的助手消息
    if (!activeChat.value.messages[activeChat.value.messages.length - 1].startsWith('<GPT-4o>:')) {
      activeChat.value.messages.push(`<GPT-4o>: ${content}`);
    } else {
      // 如果最后一条已经是助手的消息，则更新该消息
      activeChat.value.messages[activeChat.value.messages.length - 1] = `<GPT-4o>: ${content}`;
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
  padding: 4px 10px;
  cursor: pointer;
  font-size: 12px;
  border-radius: 4px;
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