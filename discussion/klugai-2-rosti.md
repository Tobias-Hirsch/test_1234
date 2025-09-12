 更新的文件列表：

  1. 后端配置文件

  - rosti_ai/backend/app/core/config.py
    - 进行了APP_NAME的更改（最终保持为"Rosti"）

  2. MinerU服务增强

  - rosti_ai/backend/app/services/mineru_service.py
    - 集成了 formula_enable=True 和 table_enable=True 参数
    - 更新了 pipeline_doc_analyze 调用以支持公式和表格识别

  3. 文档处理工具增强

  - rosti_ai/backend/app/tools/deal_document.py
    - 完整的 _extract_text_from_mineru_result
  函数用于提取MinerU结构化输出
    - _extract_text_with_pymupdf_fallback 后备功能
    - 改进的 extract_text_from_file_content 函数

  4. MinerU解析器

  - rosti_ai/backend/app/services/mineru_parser.py
    - 确认已有 formula_enable 和 table_enable 参数设置

  主要更新内容：

  功能增强：
  - ✅ 公式识别功能集成 (formula_enable=True)
  - ✅ 表格识别功能集成 (table_enable=True)
  - ✅ 文本提取增强功能
  - ✅ MinerU结构化输出处理

  配置保持：
  - ✅ 保持了项目原有的"Rosti"品牌名称
  - ✅ 验证了配置文件兼容性

  这次更新主要是将您的klugai_rag项目中的MinerU文档处理增强功能移植到
  了rosti-running-rag项目，使其具备更好的公式识别、表格处理和文本提
  取能力。