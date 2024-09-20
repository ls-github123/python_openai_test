<template>
  <div class="chat-container">
    <h1>Microsoft_Azure_GPT4O</h1>
    <div class="chat-box">
      <div class="chat-log">
        <!-- 显示聊天日志 -->
        <p v-for="message in chatLog" :key="message.id">{{ message.text }}</p>
      </div>
      <div class="chat-input">
        <input 
          v-model="question" 
          placeholder="请输入你的问题" 
          @keyup.enter="sendQuestion" 
          :disabled="isLoading" 
        />
        <button @click="sendQuestion" :disabled="isLoading">提交</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      question: '',  // 用户输入的问题
      chatLog: [],   // 保存对话记录
      isLoading: false,  // 控制按钮禁用状态
      answerText: '',   // 存储逐字接收的回答文本
    };
  },
  methods: {
    async sendQuestion() {
      if (!this.question.trim()) {
        alert('提交的问题不能为空!');
        return;
      }

      this.isLoading = true;  // 开始加载，禁用按钮
      this.answerText = '';   // 清空之前的回答文本

      try {
        // 向后端发送POST请求，获取问题回答
        const response = await fetch('http://127.0.0.1:8000/api/chat/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ question: this.question }),
        });

        if (!response.ok) {
          throw new Error('网络响应异常');
        }

        // 通过 EventSource 逐字处理响应
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let done = false;

        while (!done) {
          const { value, done: readerDone } = await reader.read();
          done = readerDone;

          // 将逐字流式输出的字符拼接到answerText中
          const chunk = decoder.decode(value, { stream: true });

          // 去掉 "data: " 前缀并拼接内容
          const processedChunk = chunk.replace(/^data: /gm, '');

          this.answerText += processedChunk;

          // 实时更新聊天日志
          this.updateChatLog();
        }
      } catch (error) {
        console.error('Error:', error);
        alert('There was an error. Please try again.');
      } finally {
        this.isLoading = false;  // 请求结束，启用按钮
        this.question = '';  // 清空输入框
      }
    },
    updateChatLog() {
      // 清空当前聊天日志，显示当前逐字生成的文本
      this.chatLog = [{ id: 0, text: this.answerText }];
    },
  },
};
</script>

<style scoped>
.chat-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.chat-box {
  border: 1px solid #ccc;
  padding: 10px;
}

.chat-log {
  height: 300px;
  overflow-y: auto;
  border-bottom: 1px solid #ddd;
  margin-bottom: 10px;
}

.chat-log p {
  word-break: break-all;
}

.chat-input {
  display: flex;
}

.chat-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.chat-input button {
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  margin-left: 10px;
}

.chat-input button:disabled {
  background-color: #ccc;
}
</style>
