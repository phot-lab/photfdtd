import whisper

model = whisper.load_model("base")  # 可以使用 "small" 或 "medium" 提高准确性
result = model.transcribe("C://Users//11487//OneDrive//文档//WeChat Files//wxid_9rezb5ffggdo22//FileStorage//File//2025-05")
print(result["text"])
