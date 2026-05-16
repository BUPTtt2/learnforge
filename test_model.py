import os
from openai import OpenAI

# 设置API参数 - 敏感信息从环境变量获取
api_key = os.getenv("MODELSCOPE_API_KEY", "")
base_url = os.getenv("MODELSCOPE_BASE_URL", "https://api-inference.modelscope.cn/v1")

if not api_key:
    print("错误：未配置MODELSCOPE_API_KEY环境变量")
    print("请在.env文件中设置MODELSCOPE_API_KEY")
    exit(1)

client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

try:
    print("正在调用模型...")
    response = client.chat.completions.create(
        model='ZhipuAI/glm-5.1',
        messages=[
            {
                'role': 'user',
                'content': '你好，测试API连接'
            }
        ],
        stream=False
    )
    
    if response and response.choices:
        content = response.choices[0].message.content
        print("模型调用成功！")
        print("回复:", content)
    else:
        print("API调用成功但无回复")
        print("响应:", response)
        
except Exception as e:
    print("API调用失败:", str(e))