import { defineConfig } from 'vitepress'

export default defineConfig({
  // 根路径，如果部署在子路径下，例如 example.com/docs/
  // 在多语言模式下，base 通常不需要在顶层设置，而是在每个 locale 中设置
  base: '/docs/', // Set the base path for deployment
  head: [
    ['meta', { property: 'og:locale', content: 'en_US' }],
    ['meta', { property: 'og:locale:alternate', content: 'zh_CN' }],
  ],

  themeConfig: {}, // 添加一个空的顶层 themeConfig
  locales: {
    '/': { // 将 root 键名改为 '/'
      label: '简体中文',
      lang: 'zh-CN',
      title: "Rosti 产品文档",
      description: "Rosti 产品用户手册和技术说明。",
      link: '/', // 默认语言的链接，指向其语言根目录
      themeConfig: {
        i18nRouting: true, // 明确启用 i18n 路由
        nav: [
          { text: '首页', link: '/' }, // 调整为指向语言根目录
          { text: '前端功能', link: '/frontend/' },
          { text: '后端功能', link: '/backend/' },
          { text: '设置', link: '/settings/' },
          { text: '技术说明', link: '/tech-specs/' }
        ],
        sidebar: {
          '/frontend/': [
            {
              text: '前端功能',
              items: [
                { text: '概述', link: '/frontend/' },
                { text: '用户界面', link: '/frontend/user-interface' },
                { text: '数据展示', link: '/frontend/data-display' }
              ]
            },
            {
              text: '认证与用户管理',
              items: [
                { text: '账户激活', link: '/frontend/authentication/activate-account' },
                { text: '忘记密码', link: '/frontend/authentication/forgot-password' },
                { text: '用户登录', link: '/frontend/authentication/login' },
                { text: '用户注册', link: '/frontend/authentication/register' },
                { text: '重置密码', link: '/frontend/authentication/reset-password' }
              ]
            },
            {
              text: '聊天与 RAG',
              items: [
                { text: '聊天页面', link: '/frontend/chat-rag/chat-page' },
                { text: '聊天消息区域', link: '/frontend/chat-rag/chat-message-area' },
                { text: 'RAG 查询页面', link: '/frontend/chat-rag/query-rag' },
                { text: 'RAG 编辑页面', link: '/frontend/chat-rag/rag-edit' },
                { text: 'RAG 介绍页面', link: '/frontend/chat-rag/rag-intro' },
                { text: 'RAG 文件列表', link: '/frontend/chat-rag/rag-list' },
                { text: 'Rosti 聊天界面组件', link: '/frontend/chat-rag/rosti-chat-interface' },
                { text: '文件上传页面', link: '/frontend/chat-rag/upload-file' },
                { text: '文件预览组件', link: '/frontend/chat-rag/components/file-preview-drawer' },
                { text: 'RAG 嵌入组件', link: '/frontend/chat-rag/components/rag-embedding' },
                { text: 'RAG 文件列表组件', link: '/frontend/chat-rag/components/rag-file-list' },
                { text: 'RAG 表单组件', link: '/frontend/chat-rag/components/rag-form' }
              ]
            },
            {
              text: '系统设置',
              items: [
                { text: '策略管理', link: '/frontend/system-settings/policy-management' },
                { text: '系统设置', link: '/frontend/system-settings/system-settings' },
                { text: '用户资料', link: '/frontend/system-settings/user-profile' },
                { text: '权限管理', link: '/frontend/system-settings/permission-management' },
                { text: '角色管理', link: '/frontend/system-settings/role-management' },
                { text: '用户管理', link: '/frontend/system-settings/user-management' }
              ]
            },
            {
              text: '错误页面',
              items: [
                { text: '通用错误页面', link: '/frontend/error-pages/general-error' },
                { text: '404 页面未找到', link: '/frontend/error-pages/not-found' },
                { text: '权限不足页面', link: '/frontend/error-pages/permission-denied' }
              ]
            }
          ],
          '/backend/': [
            {
              text: '后端功能',
              items: [
                { text: '概述', link: '/backend/' },
                { text: 'main.py', link: '/backend/main-py' },
                { text: 'Dockerfile', link: '/backend/dockerfile' },
                { text: 'requirements.txt', link: '/backend/requirements-txt' }
              ]
            },
            {
              text: '核心模块',
              items: [
                { text: '配置', link: '/backend/core/config' },
                { text: '安全', link: '/backend/core/security' }
              ]
            },
            {
              text: '数据库模型',
              items: [
                { text: '数据库', link: '/backend/models/database' }
              ]
            },
            {
              text: '模块',
              items: [
                { text: 'MinIO 模块', link: '/backend/modules/minio-module' },
                { text: 'Milvus 模块', link: '/backend/modules/milvus-module' },
                { text: 'MongoDB 模块', link: '/backend/modules/mongodb-module' },
                { text: 'MySQL 模块', link: '/backend/modules/mysql-module' },
                { text: 'Ollama 模块', link: '/backend/modules/ollama-module' },
                { text: 'MagicPDF MinIO', link: '/backend/modules/magicpdf-minio' }
              ]
            },
            {
              text: 'RAG 知识',
              items: [
                { text: '嵌入服务', link: '/backend/rag-knowledge/embedding-service' },
                { text: '通用知识', link: '/backend/rag-knowledge/generic-knowledge' }
              ]
            },
            {
              text: 'API 路由',
              items: [
                { text: '认证', link: '/backend/routers/authentication' },
                { text: '验证码', link: '/backend/routers/captcha' },
                { text: '聊天', link: '/backend/routers/chat' },
                { text: '文件', link: '/backend/routers/files' },
                { text: 'RAG', link: '/backend/routers/rag' },
                { text: '嵌入', link: '/backend/routers/embeddings' },
                { text: '角色', link: '/backend/routers/roles' },
                { text: '权限', link: '/backend/routers/permissions' },
                { text: '用户角色', link: '/backend/routers/user-roles' },
                { text: '用户', link: '/backend/routers/users' },
                { text: '设置', link: '/backend/routers/settings' },
                { text: 'SMTP', link: '/backend/routers/smtp' },
                { text: '策略', link: '/backend/routers/policies' },
                { text: '代理聊天', link: '/backend/routers/agent-chat' },
                { text: '聊天页面', link: '/backend/routers/chatpage' }
              ]
            },
            {
              text: '数据模式',
              items: [
                { text: '通用模式', link: '/backend/schemas/schemas' },
                { text: '聊天模式', link: '/backend/schemas/chat-schemas' }
              ]
            },
            {
              text: '业务服务',
              items: [
                { text: '认证服务', link: '/backend/services/auth' },
                { text: '第三方认证', link: '/backend/services/auth-thirdparty' },
                { text: '邮件服务', link: '/backend/services/email' },
                { text: 'RAG 文件服务', link: '/backend/services/rag-file-service' },
                { text: '会话清理器', link: '/backend/services/conversation-cleaner' },
                { text: '不活跃用户清理器', link: '/backend/services/inactive-user-cleaner' },
                { text: '日志服务', link: '/backend/services/logging' },
                { text: 'MSAD LDAP', link: '/backend/services/msad-ldap' },
                { text: 'Ollama DeepSeek', link: '/backend/services/ollama-deepseek' },
                { text: 'Ollama 服务', link: '/backend/services/ollama-service' },
                { text: 'RAG 权限服务', link: '/backend/services/rag-permission-service' },
                { text: '聊天数据服务', link: '/backend/services/chat-data-service' },
                { text: 'ABAC 属性提取器', link: '/backend/services/abac-attribute-extractor' },
                { text: 'ABAC 函数', link: '/backend/services/abac-functions' },
                { text: 'ABAC 策略评估器', link: '/backend/services/abac-policy-evaluator' }
              ]
            },
            {
              text: '工具',
              items: [
                { text: 'PDF 工具', link: '/backend/tools/pdf' },
                { text: '文档处理工具', link: '/backend/tools/deal-document' },
                { text: 'Excel 工具', link: '/backend/tools/exlsx' },
                { text: 'PyMuPDF 工具', link: '/backend/tools/inpymupdf' },
                { text: '重试工具', link: '/backend/tools/retry-tools' },
                { text: '在线搜索工具', link: '/backend/tools/search-online-tools' },
                { text: '分割工具', link: '/backend/tools/split-tools' },
                { text: 'Word 工具', link: '/backend/tools/word' }
              ]
            },
            {
              text: 'LLM 相关',
              items: [
                { text: '链', link: '/backend/llm/chain' },
                { text: 'LLM 客户端', link: '/backend/llm/llm' }
              ]
            }
          ],
          '/settings/': [
            {
              text: '设置',
              items: [
                { text: '概述', link: '/settings/' },
                { text: '用户设置', link: '/settings/user-settings' }
              ]
            }
          ],
          '/tech-specs/': [
            {
              text: '技术说明',
              items: [
                { text: '概述', link: '/tech-specs/' },
                { text: '系统架构', link: '/tech-specs/architecture' }
              ]
            }
          ]
        },
        // socialLinks: [
        //   { icon: 'github', link: 'https://github.com/your-org/your-repo' }
        // ],
        footer: {
          message: '基于 MIT 许可发布。',
          copyright: '版权所有 © 2017-至今 上海德制信息科技有限公司'
        }
      }
    },
    '/en/': {
      label: 'English',
      lang: 'en-US',
      title: "Rosti Product Documentation",
      description: "Rosti Product User Manual and Technical Specifications.",
      link: '/en/',
      themeConfig: {
        i18nRouting: true, // 明确启用 i18n 路由
        nav: [
          { text: 'Home', link: '/en/' },
          { text: 'Frontend Features', link: '/en/frontend/' },
          { text: 'Backend Features', link: '/en/backend/' },
          { text: 'Settings', link: '/en/settings/' },
          { text: 'Tech Specs', link: '/en/tech-specs/' }
        ],
        sidebar: {
          '/en/frontend/': [
            {
              text: 'Frontend Features',
              items: [
                { text: 'Overview', link: '/en/frontend/' },
                { text: 'User Interface', link: '/en/frontend/user-interface' },
                { text: 'Data Display', link: '/en/frontend/data-display' }
              ]
            },
            {
              text: 'Authentication & User Management',
              items: [
                { text: 'Account Activation', link: '/en/frontend/authentication/activate-account' },
                { text: 'Forgot Password', link: '/en/frontend/authentication/forgot-password' },
                { text: 'User Login', link: '/en/frontend/authentication/login' },
                { text: 'User Registration', link: '/en/frontend/authentication/register' },
                { text: 'Reset Password', link: '/en/frontend/authentication/reset-password' }
              ]
            },
            {
              text: 'Chat & RAG',
              items: [
                { text: 'Chat Page', link: '/en/frontend/chat-rag/chat-page' },
                { text: 'Chat Message Area', link: '/en/frontend/chat-rag/chat-message-area' },
                { text: 'RAG Query Page', link: '/en/frontend/chat-rag/query-rag' },
                { text: 'RAG Edit Page', link: '/en/frontend/chat-rag/rag-edit' },
                { text: 'RAG Intro Page', link: '/en/frontend/chat-rag/rag-intro' },
                { text: 'RAG File List', link: '/en/frontend/chat-rag/rag-list' },
                { text: 'Rosti Chat Interface Component', link: '/en/frontend/chat-rag/rosti-chat-interface' },
                { text: 'File Upload Page', link: '/en/frontend/chat-rag/upload-file' },
                { text: 'File Preview Component', link: '/en/frontend/chat-rag/components/file-preview-drawer' },
                { text: 'RAG Embedding Component', link: '/en/frontend/chat-rag/components/rag-embedding' },
                { text: 'RAG File List Component', link: '/en/frontend/chat-rag/components/rag-file-list' },
                { text: 'RAG Form Component', link: '/en/frontend/chat-rag/components/rag-form' }
              ]
            },
            {
              text: 'System Settings',
              items: [
                { text: 'Policy Management', link: '/en/frontend/system-settings/policy-management' },
                { text: 'System Settings', link: '/en/frontend/system-settings/system-settings' },
                { text: 'User Profile', link: '/en/settings/user-settings' },
                { text: 'Permission Management', link: '/en/frontend/system-settings/permission-management' },
                { text: 'Role Management', link: '/en/frontend/system-settings/role-management' },
                { text: 'User Management', link: '/en/frontend/system-settings/user-management' }
              ]
            },
            {
              text: 'Error Pages',
              items: [
                { text: 'General Error Page', link: '/en/frontend/error-pages/general-error' },
                { text: '404 Page Not Found', link: '/en/frontend/error-pages/not-found' },
                { text: 'Permission Denied Page', link: '/en/frontend/error-pages/permission-denied' }
              ]
            }
          ],
          '/en/backend/': [
            {
              text: 'Backend Features',
              items: [
                { text: 'Overview', link: '/en/backend/' },
                { text: 'main.py', link: '/en/backend/main-py' },
                { text: 'Dockerfile', link: '/en/backend/dockerfile' },
                { text: 'requirements.txt', link: '/en/backend/requirements-txt' }
              ]
            },
            {
              text: 'Core Modules',
              items: [
                { text: 'Configuration', link: '/en/backend/core/config' },
                { text: 'Security', link: '/en/backend/core/security' }
              ]
            },
            {
              text: 'Database Models',
              items: [
                { text: 'Database', link: '/en/backend/models/database' }
              ]
            },
            {
              text: 'Modules',
              items: [
                { text: 'MinIO Module', link: '/en/backend/modules/minio-module' },
                { text: 'Milvus Module', link: '/en/backend/modules/milvus-module' },
                { text: 'MongoDB Module', link: '/en/backend/modules/mongodb-module' },
                { text: 'MySQL Module', link: '/en/backend/modules/mysql-module' },
                { text: 'Ollama Module', link: '/en/backend/modules/ollama-module' },
                { text: 'MagicPDF MinIO', link: '/en/backend/modules/magicpdf-minio' }
              ]
            },
            {
              text: 'RAG Knowledge',
              items: [
                { text: 'Embedding Service', link: '/en/backend/rag-knowledge/embedding-service' },
                { text: 'Generic Knowledge', link: '/en/backend/rag-knowledge/generic-knowledge' }
              ]
            },
            {
              text: 'API Routes',
              items: [
                { text: 'Authentication', link: '/en/backend/routers/authentication' },
                { text: 'Captcha', link: '/en/backend/routers/captcha' },
                { text: 'Chat', link: '/en/backend/routers/chat' },
                { text: 'Files', link: '/en/backend/routers/files' },
                { text: 'RAG', link: '/en/backend/routers/rag' },
                { text: 'Embeddings', link: '/en/backend/routers/embeddings' },
                { text: 'Roles', link: '/en/backend/routers/roles' },
                { text: 'Permissions', link: '/en/backend/routers/permissions' },
                { text: 'User Roles', link: '/en/backend/routers/user-roles' },
                { text: 'Users', link: '/en/backend/routers/users' },
                { text: 'Settings', link: '/en/backend/routers/settings' },
                { text: 'SMTP', link: '/en/backend/routers/smtp' },
                { text: 'Policies', link: '/en/backend/routers/policies' },
                { text: 'Agent Chat', link: '/en/backend/routers/agent-chat' },
                { text: 'Chat Page', link: '/en/backend/routers/chatpage' }
              ]
            },
            {
              text: 'Data Schemas',
              items: [
                { text: 'General Schemas', link: '/en/backend/schemas/schemas' },
                { text: 'Chat Schemas', link: '/en/backend/schemas/chat-schemas' }
              ]
            },
            {
              text: 'Business Services',
              items: [
                { text: 'Authentication Service', link: '/en/backend/services/auth' },
                { text: 'Third-Party Authentication', link: '/en/backend/services/auth-thirdparty' },
                { text: 'Email Service', link: '/en/backend/services/email' },
                { text: 'RAG File Service', link: '/en/backend/services/rag-file-service' },
                { text: 'Conversation Cleaner', link: '/en/backend/services/conversation-cleaner' },
                { text: 'Inactive User Cleaner', link: '/en/backend/services/inactive-user-cleaner' },
                { text: 'Logging Service', link: '/en/backend/services/logging' },
                { text: 'MSAD LDAP', link: '/en/backend/services/msad-ldap' },
                { text: 'Ollama DeepSeek', link: '/en/backend/services/ollama-deepseek' },
                { text: 'Ollama Service', link: '/en/backend/services/ollama-service' },
                { text: 'RAG Permission Service', link: '/en/backend/services/rag-permission-service' },
                { text: 'Chat Data Service', link: '/en/backend/services/chat-data-service' },
                { text: 'ABAC Attribute Extractor', link: '/en/backend/services/abac-attribute-extractor' },
                { text: 'ABAC Functions', link: '/en/backend/services/abac-functions' },
                { text: 'ABAC Policy Evaluator', link: '/en/backend/services/abac-policy-evaluator' }
              ]
            },
            {
              text: 'Tools',
              items: [
                { text: 'PDF Tool', link: '/en/backend/tools/pdf' },
                { text: 'Document Processing Tool', link: '/en/backend/tools/deal-document' },
                { text: 'Excel Tool', link: '/en/backend/tools/exlsx' },
                { text: 'PyMuPDF Tool', link: '/en/backend/tools/inpymupdf' },
                { text: 'Retry Tool', link: '/en/backend/tools/retry-tools' },
                { text: 'Online Search Tool', link: '/en/backend/tools/search-online-tools' },
                { text: 'Split Tool', link: '/en/backend/tools/split-tools' },
                { text: 'Word Tool', link: '/en/backend/tools/word' }
              ]
            },
            {
              text: 'LLM Related',
              items: [
                { text: 'Chain', link: '/en/backend/llm/chain' },
                { text: 'LLM Client', link: '/en/backend/llm/llm' }
              ]
            }
          ],
          '/en/settings/': [
            {
              text: 'Settings',
              items: [
                { text: 'Overview', link: '/en/settings/' },
                { text: 'User Settings', link: '/en/settings/user-settings' }
              ]
            }
          ],
          '/en/tech-specs/': [
            {
              text: 'Technical Specifications',
              items: [
                { text: 'Overview', link: '/en/tech-specs/' },
                { text: 'System Architecture', link: '/en/tech-specs/architecture' }
              ]
            }
          ]
        },
        // socialLinks: [
        //   { icon: 'github', link: 'https://github.com/your-org/your-repo' }
        // ],
        footer: {
          message: 'Released under the MIT License.',
          copyright: 'Copyright © 2017-present Shanghai De Manufacturing IT Co., Ltd.'
        }
      }
    }
  }
})
