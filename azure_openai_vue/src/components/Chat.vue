<template>
  <div class="chat-wrapper">

    <!-- 左侧对话选择区域 -->
    <div class="chat-list">
      <button @click="startNewChat" class="new-chat-btn">新建会话</button>
      <input type="text" v-model="searchQuery" placeholder="搜索会话" class="search-input" />
      
      <!-- 新会话始终在最上面 -->
      <div v-if="newChat" @click="selectChat(newChat)" :class="{'active-chat': activeChat === newChat}" class="chat-item">
        <div>{{ newChat.name }}</div>
        <button @click="deleteNewChat" class="delete-btn">删除</button>
      </div>

      <!-- 显示已存储的会话，排在下面 -->
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
        <div v-for="(message, index) in activeChat.messages" :key="index" class="message-row">
          <span :class="message.sender === 'user' ? 'user-message' : 'assistant-message'">
            <strong>{{ message.sender === 'user' ? '<我>' : '<GPT-4O>' }}: </strong>{{ message.content }}
          </span>
        </div>
      </div>
      <div class="message-input">
        <textarea v-model="inputMessage" placeholder="请输入消息" class="message-textarea"></textarea>
        <button @click="sendMessage" :disabled="isLoading" class="send-btn">发送</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

// 响应式数据
const chats = ref([]); // 载入的已存储会话
const newChat = ref({ name: '新会话', messages: [] }); // 新建会话
const activeChat = ref(newChat.value); // 当前激活的会话，默认是新会话
const searchQuery = ref(''); // 搜索框输入内容
const inputMessage = ref(''); // 用户输入的消息
const isLoading = ref(false); // 控制是否正在加载

// 加载已有会话数据（假设从后端获取）
const loadChats = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/cates/');
    const data = await response.json();
    chats.value = data.clist.map(chat => ({
      name: chat.title || '新会话', // 如果 title 为空，显示为 '新会话'
      messages: [] // 假设 messages 为空
    }));
  } catch (error) {
    console.error('加载会话失败:', error);
  }
};

// 页面加载时自动新建会话并加载已有会话
onMounted(() => {
  loadChats(); // 加载已有的会话
});

// 根据搜索框内容过滤会话
const filteredChats = computed(() => {
  return chats.value.filter(chat => chat.name.includes(searchQuery.value));
});

// 选择会话
const selectChat = (chat) => {
  activeChat.value = chat;
};

// 新建会话，创建并激活新会话
const startNewChat = () => {
  newChat.value = { name: '新会话', messages: [] }; // 新建会话
  activeChat.value = newChat.value; // 激活新会话
};

// 删除新会话
const deleteNewChat = () => {
  if (activeChat.value === newChat.value) {
    activeChat.value = null;
  }
  newChat.value = null;
};

// 删除已存在会话
const deleteChat = async (index) => {
  const chatToDelete = chats.value[index];
  // 假设从后端删除会话
  try {
    await fetch(`http://127.0.0.1:8000/api/cates/${chatToDelete.name}/`, {
      method: 'DELETE',
    });
    chats.value.splice(index, 1); // 从前端移除会话
    if (activeChat.value === chatToDelete) {
      activeChat.value = null;
    }
  } catch (error) {
    console.error('删除会话失败:', error);
  }
};

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return; // 消息为空不发送

  // 将用户输入的消息添加到当前会话的消息记录中，并标记为 <我>
  activeChat.value.messages.push({ sender: 'user', content: inputMessage.value });
  isLoading.value = true;

  try {
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

    // 更新新会话的标题为用户输入的第一个问题的前10个字
    if (newChat.value.name === '新会话') {
      newChat.value.name = inputMessage.value.slice(0, 10);
      // 将新会话存入数据库，假设后端保存
      await fetch('http://127.0.0.1:8000/api/cates/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title: newChat.value.name }),
      });
      chats.value.unshift(newChat.value); // 将新会话加入已有会话列表
      newChat.value = null; // 清除当前新会话
    }
  } catch (error) {
    console.error('Error:', error);
  } finally {
    isLoading.value = false; // 请求结束后启用发送按钮
    inputMessage.value = ''; // 清空输入框
  }
};

// 更新助手消息，显示逐字返回的内容，并标记为 <GPT-4o>
const updateAssistantMessage = (content) => {
  if (activeChat.value) {
    const lastMessage = activeChat.value.messages[activeChat.value.messages.length - 1];
    if (!lastMessage || lastMessage.sender !== 'assistant') {
      activeChat.value.messages.push({ sender: 'assistant', content });
    } else {
      lastMessage.content = content;
    }
  }
};
</script>

<style scoped>
/* 样式保持不变 */
.chat-wrapper {
  display: flex;
  height: 100vh;
}
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
.user-message {
  color: #ffffff;
  background-color: #007bff;
  padding: 8px 12px;
  border-radius: 12px;
  margin-bottom: 10px;
  max-width: 60%;
  align-self: flex-end;
}
.assistant-message {
  color: #ffffff;
  background-color: #4e4e4e;
  padding: 8px 12px;
  border-radius: 12px;
  margin-bottom: 10px;
  max-width: 60%;
  align-self: flex-start;
}
.message-row {
  display: flex;
}
</style>