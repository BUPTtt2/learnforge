import requests
import os

def generate_image(prompt, model="flux", width=1024, height=1024, output_dir="generated_images"):
    """
    使用 Pollinations.ai 生成图片
    
    参数:
        prompt: 图片描述
        model: 模型选择 (flux/turbo/stable-diffusion)
        width: 图片宽度
        height: 图片高度
        output_dir: 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 构建URL
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    params = {
        "model": model,
        "width": width,
        "height": height
    }
    
    print(f"正在生成图片: {prompt}")
    print(f"使用模型: {model}")
    print(f"分辨率: {width}x{height}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        # 生成文件名
        safe_prompt = "".join(c for c in prompt if c.isalnum() or c in " -_").rstrip()[:50]
        filename = f"{safe_prompt}_{model}_{width}x{height}.jpg"
        filepath = os.path.join(output_dir, filename)
        
        # 保存图片
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        print(f"✅ 图片已保存到: {filepath}")
        return filepath
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 生成失败: {e}")
        return None

if __name__ == "__main__":
    # 测试示例
    test_prompts = [
        "a beautiful sunset over mountain landscape",
        "a cute cat astronaut floating in space",
        "modern city skyline at night with neon lights"
    ]
    
    for prompt in test_prompts:
        generate_image(prompt, model="flux", width=1024, height=1024)
        print("-" * 60)
    
    print("\n🎉 所有图片生成完成！")
