from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile, os, nltk, asyncio, logging, traceback
from typing import List, Dict, Any

# 增加對特定的PDF處理錯誤的匯入
from unstructured.partition.pdf import partition_pdf
from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError

# 設置日誌記錄
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Sentence Extractor")

# 確保 nltk 資源存在（只做一次）
asyncio.get_event_loop().run_in_executor(
    None,
    lambda: nltk.download("punkt", quiet=True)
)

@app.post("/process")
async def process_pdf(file: UploadFile = File(...)):
    # 檢查副檔名
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    tmp_path = None
    try:
        # 將上傳內容存到暫存檔
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            logger.debug(f"Read {len(content)} bytes from uploaded file")
            tmp.write(content)
            tmp_path = tmp.name
    
        logger.info(f"PDF saved to temporary file: {tmp_path}")
        
        try:
            # 使用 unstructured 進行 PDF 解析
            logger.info("Starting PDF parsing...")
            try:
                elements = partition_pdf(
                    filename=tmp_path,
                    strategy="hi_res",
                    infer_table_structure=True,
                    extract_images_in_pdf=False,
                )
            except PDFInfoNotInstalledError:
                logger.error("poppler-utils is not installed or not in PATH")
                raise HTTPException(
                    status_code=500, 
                    detail="PDF processing failed: poppler-utils is not installed or not in PATH. Please install poppler-utils package."
                )
            except PDFPageCountError:
                logger.error("Failed to get page count from PDF")
                raise HTTPException(
                    status_code=500, 
                    detail="PDF processing failed: Could not determine page count. The PDF file might be corrupted."
                )
            except Exception as e:
                logger.error(f"PDF parsing error: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"PDF processing failed: {str(e)}"
                )
                
            logger.info(f"PDF parsing completed. Extracted {len(elements)} elements.")

            sentences = []
            for element in elements:
                if hasattr(element, "text") and element.text.strip():
                    sents = nltk.sent_tokenize(element.text)
                    sentences.extend([s.strip() for s in sents if s.strip()])
            
            logger.info(f"Sentence tokenization completed. Found {len(sentences)} sentences.")

            return JSONResponse(
                {
                    "filename": file.filename,
                    "sentence_count": len(sentences),
                    "sentences": sentences,
                }
            )
        except Exception as e:
            # 捕獲所有其他未預期的異常
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, 
                detail=f"An unexpected error occurred: {str(e)}\n{traceback.format_exc()}"
            )
    finally:
        # 確保暫存檔被清理，即使出現錯誤
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
                logger.info(f"Temporary file removed: {tmp_path}")
            except Exception as e:
                logger.error(f"Error removing temporary file: {str(e)}")

@app.get("/health")
async def health_check():
    """健康檢查端點，用於驗證API是否運行正常"""
    return {"status": "healthy"}
