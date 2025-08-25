"""
Service Layer - Xử lý logic nghiệp vụ chính của hệ thống RAG
Chứa tất cả logic xử lý RAG, khởi tạo và tìm kiếm
"""

import os
import json
from typing import Optional, List
from lightrag import LightRAG, QueryParam
from ingestion import initialize_rag, index_file
from util.text_search_util import TextSearchUtil


class RAGService:
    """
    Lớp dịch vụ để quản lý các hoạt động của hệ thống RAG
    Đây là "bộ não" chính xử lý tất cả logic nghiệp vụ
    """
    
    def __init__(self, data_path: str = "../../data/data.txt", data_path_json: str = "../../data/data.json"):
        self.data_path = data_path           # Đường dẫn đến file dữ liệu text
        self.data_path_json = data_path_json # Đường dẫn đến file dữ liệu JSON
        self.data_files = [data_path, data_path_json]  # Danh sách tất cả files cần index
        self.rag = None                      # Đối tượng RAG (ban đầu chưa có)
        self.raw_text: Optional[str] = None  # Văn bản dự phòng nếu RAG lỗi
        self.indexing_complete: bool = False # Trạng thái đánh chỉ mục

    async def initialize(self, force_reindex: bool = False):
        """
        Khởi tạo và đánh chỉ mục dữ liệu từ nhiều files không đồng bộ. 
        Sử dụng hàm index_file với thử lại nhiều lần,
        và dự phòng lưu văn bản thô nếu đánh chỉ mục thất bại.
        """
        # Bước 1: Kiểm tra tất cả files dữ liệu có tồn tại không
        missing_files = []
        for file_path in self.data_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            raise FileNotFoundError(f"Data files not found: {missing_files}")

        # Bước 2: Kiểm tra files có rỗng không
        empty_files = []
        for file_path in self.data_files:
            if os.path.getsize(file_path) == 0:
                empty_files.append(file_path)
        
        if empty_files:
            raise ValueError(f"Data files are empty: {empty_files}")

        # Bước 3: Khởi tạo RAG nếu chưa có hoặc bắt buộc tạo lại
        if self.rag is None or force_reindex:
            print("Initializing RAG system...")
            # Thử khởi tạo hệ thống RAG
            try:
                self.rag = await initialize_rag()
            except Exception as e:
                print(f"initialize_rag failed: {e}")
                # Giữ self.rag = None và tiếp tục chuẩn bị dự phòng
                self.rag = None

            # Bước 4: Đánh chỉ mục tất cả files
            print(f"Indexing data from {len(self.data_files)} files...")
            if self.rag is not None:
                indexed_files = []
                failed_files = []
                
                for file_path in self.data_files:
                    print(f"Indexing {file_path}...")
                    last_exc = None
                    
                    # Thử 3 lần cho mỗi file
                    for attempt in range(1, 4):
                        try:
                            print(f"  Attempt {attempt}/3 for {os.path.basename(file_path)}...")
                            
                            # Xử lý file theo định dạng
                            if file_path.endswith('.json'):
                                await self._index_json_file(self.rag, file_path)
                            else:
                                await index_file(self.rag, file_path)
                            
                            print(f"  ✅ Successfully indexed {os.path.basename(file_path)}")
                            indexed_files.append(file_path)
                            last_exc = None
                            break
                        except Exception as e:
                            print(f"  ❌ Attempt {attempt} failed for {os.path.basename(file_path)}: {e}")
                            last_exc = e

                    # Nếu file thất bại sau tất cả attempts
                    if last_exc:
                        print(f"Failed to index {file_path} after retries: {last_exc}")
                        failed_files.append(file_path)

                # Báo cáo kết quả indexing
                print(f"Indexing summary:")
                print(f"  ✅ Successfully indexed: {len(indexed_files)} files")
                print(f"  ❌ Failed to index: {len(failed_files)} files")
                
                if indexed_files:
                    print("Successfully indexed files:")
                    for file_path in indexed_files:
                        print(f"  - {os.path.basename(file_path)}")
                
                if failed_files:
                    print("Failed files:")
                    for file_path in failed_files:
                        print(f"  - {os.path.basename(file_path)}")
                    
                    # Chuẩn bị văn bản dự phòng từ tất cả files có thể đọc được
                    self._prepare_fallback_text()

                    # Thử chèn trực tiếp văn bản dự phòng
                    try:
                        if self.rag is not None and self.raw_text:
                            await self.rag.ainsert(self.raw_text)
                            print("Fallback raw indexing complete!")
                            self.indexing_complete = True
                    except Exception as e2:
                        print(f"Fallback ainsert also failed: {e2}. Will use local text search fallback.")
                        self.indexing_complete = False
                else:
                    # Tất cả files đều indexed thành công
                    self.indexing_complete = True
                    print("🎉 All files indexed successfully!")
            else:
                # Không thể khởi tạo RAG; tải văn bản thô để tìm kiếm cục bộ
                self._prepare_fallback_text()
                print("Loaded raw text from all files for local fallback search.")
                self.indexing_complete = False

        # Đánh dấu hoàn thành đánh chỉ mục nếu rag tồn tại và không có lỗi
        if self.rag is not None and self.indexing_complete is False:
            # Nếu rag tồn tại và chưa đặt indexing_complete, đặt True
            self.indexing_complete = True
        return self.rag

    async def _index_json_file(self, rag: LightRAG, file_path: str) -> None:
        """
        Đánh chỉ mục file JSON bằng cách chuyển đổi thành text readable
        
        Args:
            rag: LightRAG instance
            file_path: Đường dẫn đến file JSON
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        
            # Sử dụng ainsert để index text đã convert
            await rag.ainsert(input=json_data, file_paths=[file_path])
            
        except Exception as e:
            print(f"Error indexing JSON file {file_path}: {e}")
            raise e

    def _prepare_fallback_text(self):
        """
        Chuẩn bị văn bản dự phòng từ tất cả files để tìm kiếm cục bộ
        """
        all_text = []
        
        for file_path in self.data_files:
            try:
                if file_path.endswith('.json'):
                    # Xử lý file JSON
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    readable_text = self._convert_json_to_readable_text(json_data)
                    all_text.append(f"=== Data từ {os.path.basename(file_path)} ===\n{readable_text}\n")
                else:
                    # Xử lý file text thường
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    all_text.append(f"=== Data từ {os.path.basename(file_path)} ===\n{content}\n")
                    
            except Exception as e:
                print(f"Failed to load {file_path} for fallback: {e}")
        
        self.raw_text = "\n\n".join(all_text) if all_text else None

    async def get_answer(self, question: str, mode: str = "mix", top_k: int = 5, force_reindex: bool = False) -> str:
        """
        Xử lý câu hỏi và trả về câu trả lời
        Đây là hàm chính để trả lời câu hỏi của người dùng
        """
        # Bước 1: Thử khởi tạo RAG (có thể đặt self.raw_text nếu dùng dự phòng)
        try:
            await self.initialize(force_reindex=force_reindex)
        except Exception as e:
            print(f"RAG initialization failed in get_answer: {e}")

        # Bước 2: Nếu RAG có sẵn, thử sử dụng nó
        if self.rag is not None:
            query_param = QueryParam(
                mode=mode,              # Chế độ tìm kiếm
                top_k=top_k,           # Số kết quả tối đa
                enable_rerank=False    # Không sắp xếp lại kết quả
            )
            try:
                return await self.rag.aquery(question, param=query_param)
            except Exception as e:
                print(f"RAG query failed: {e}")

        # Bước 3: Dự phòng: tìm kiếm cục bộ trên văn bản thô
        print("Using local fallback search...")
        if not self.raw_text:
            self._prepare_fallback_text()
            if not self.raw_text:
                return "Sorry, I'm not able to provide an answer to that question.[no-data]"

        # Sử dụng utility class để tìm kiếm
        text_search = TextSearchUtil()
        return text_search.local_search(self.raw_text, question, top_k)

    def get_status(self) -> dict:
        """
        Lấy trạng thái hiện tại của hệ thống RAG
        """
        return {
            "rag_initialized": self.rag is not None,
            "indexing_complete": self.indexing_complete,
            "data_files": self.data_files,
            "data_files_count": len(self.data_files),
            "data_path": self.data_path,  # Backward compatibility
            "has_fallback_text": self.raw_text is not None
        }
