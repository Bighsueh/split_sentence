# PDF 句子提取服務

這是一個基於 FastAPI 的 PDF 文件處理服務，可以從 PDF 文件中提取句子。

## Docker 使用說明

### 1. 建立 Docker 映像

```bash
docker build -t pdf-sentence-extractor .
```

### 2. 運行 Docker 容器

```bash
docker run -d -p 8000:8000 --name pdf-processor pdf-sentence-extractor
```

參數說明：
- `-d`: 在背景運行容器
- `-p 8000:8000`: 將容器的 8000 端口映射到主機的 8000 端口
- `--name pdf-processor`: 為容器指定名稱

### 3. 查看容器狀態

```bash
# 查看運行中的容器
docker ps

# 查看容器日誌
docker logs pdf-processor

# 查看容器詳細資訊
docker inspect pdf-processor
```

### 4. 停止和移除容器

```bash
# 停止容器
docker stop pdf-processor

# 移除容器
docker rm pdf-processor
```

## API 使用說明

### 1. 健康檢查

```bash
curl http://localhost:8000/health
```

預期回應：
```json
{
    "status": "healthy",
    "version": "1.0.0"
}
```

### 2. 處理 PDF 文件

```bash
curl -X POST \
  -F "file=@/path/to/your/file.pdf" \
  http://localhost:8000/process
```

參數說明：
- `-X POST`: 指定 HTTP 方法為 POST
- `-F "file=@/path/to/your/file.pdf"`: 上傳 PDF 文件
- `http://localhost:8000/process`: API 端點

預期回應：
```json
{
    "filename": "file.pdf",
    "sentence_count": 123,
    "sentences": [
        "這是第一個句子。",
        "這是第二個句子。",
        // ... 更多句子
    ]
}
```

### 3. 錯誤處理

常見錯誤回應：

1. 檔案格式錯誤：
```json
{
    "detail": "Only PDF files are accepted."
}
```

2. 伺服器錯誤：
```json
{
    "detail": "PDF processing failed: [錯誤訊息]"
}
```

## 故障排除

1. 如果遇到 "Connection refused" 錯誤：
   - 確認 Docker 容器是否正在運行
   - 確認端口映射是否正確
   - 檢查防火牆設定

2. 如果遇到 "Not Found" 錯誤：
   - 確認 API 端點是否正確（應為 `/process`）
   - 確認 HTTP 方法是否正確（應為 POST）

3. 如果遇到檔案處理錯誤：
   - 確認上傳的檔案是否為有效的 PDF
   - 檢查檔案大小是否在限制範圍內
   - 查看容器日誌以獲取詳細錯誤資訊

## 注意事項

1. 確保 Docker 容器有足夠的記憶體和 CPU 資源
2. 大型 PDF 文件處理可能需要較長時間
3. 建議在生產環境中設定適當的超時時間
4. 定期檢查容器日誌以監控服務狀態
