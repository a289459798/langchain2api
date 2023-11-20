### 说明
基于LangChain和Fastapi

- 支持连续对话
- 支持基于文档提问
	- [X] word
	- [X] txt
	- [X] excel
	- [X] pdf
	- [ ] ppt

- 支持多模型
	- [X] OpenAI
	- [X] 腾讯混元
	- [X] ChatGLM
	- [ ] 百度千帆
	- [ ] 阿里通义

### 环境
python >= 3.9

docx文档识别需要安装`libreoffice`

**mac**
```
brew install --cask libreoffice
```

### 安装

1、安装依赖
```
pip install -r requirements.txt
```

2、修改参数
```
cp test.env .env
```

### 使用
```
python -m uvicorn main:app --reload 
```

浏览器访问http://127.0.0.1:8000/docs