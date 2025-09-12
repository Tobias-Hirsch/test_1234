#!/bin/bash
# Docker构建优化脚本

set -e

# 配置变量
REGISTRY="registry.your-company.com"
PROJECT_NAME="rosti-backend"
VERSION="${VERSION:-$(date +%Y%m%d-%H%M%S)}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖变化
check_dependency_changes() {
    if [ -f "backend/requirements.core.txt.md5" ]; then
        CURRENT_CORE_MD5=$(md5sum backend/requirements.core.txt | cut -d' ' -f1)
        PREVIOUS_CORE_MD5=$(cat backend/requirements.core.txt.md5)
        
        if [ "$CURRENT_CORE_MD5" != "$PREVIOUS_CORE_MD5" ]; then
            echo_warn "核心依赖发生变化，将重建核心缓存层"
            REBUILD_CORE=true
        else
            echo_info "核心依赖未变化，将使用缓存"
            REBUILD_CORE=false
        fi
    else
        echo_warn "首次构建，创建所有缓存层"
        REBUILD_CORE=true
    fi

    if [ -f "backend/requirements.extras.txt.md5" ]; then
        CURRENT_EXTRAS_MD5=$(md5sum backend/requirements.extras.txt | cut -d' ' -f1)
        PREVIOUS_EXTRAS_MD5=$(cat backend/requirements.extras.txt.md5)
        
        if [ "$CURRENT_EXTRAS_MD5" != "$PREVIOUS_EXTRAS_MD5" ]; then
            echo_warn "可变依赖发生变化，将重建可变依赖层"
            REBUILD_EXTRAS=true
        else
            echo_info "可变依赖未变化，将使用缓存"
            REBUILD_EXTRAS=false
        fi
    else
        REBUILD_EXTRAS=true
    fi
}

# 构建缓存层
build_cache_layers() {
    echo_info "开始构建缓存层..."
    
    if [ "$REBUILD_CORE" = true ]; then
        echo_info "构建核心依赖缓存层..."
        docker build \
            --target core-dependencies \
            --cache-from $REGISTRY/$PROJECT_NAME:cache-core \
            --tag $REGISTRY/$PROJECT_NAME:cache-core-$VERSION \
            --tag $REGISTRY/$PROJECT_NAME:cache-core \
            backend/
    fi
    
    if [ "$REBUILD_EXTRAS" = true ] || [ "$REBUILD_CORE" = true ]; then
        echo_info "构建可变依赖缓存层..."
        docker build \
            --target variable-dependencies \
            --cache-from $REGISTRY/$PROJECT_NAME:cache-core \
            --cache-from $REGISTRY/$PROJECT_NAME:cache-extras \
            --tag $REGISTRY/$PROJECT_NAME:cache-extras-$VERSION \
            --tag $REGISTRY/$PROJECT_NAME:cache-extras \
            backend/
    fi
}

# 构建最终镜像
build_final_image() {
    echo_info "构建最终应用镜像..."
    
    docker build \
        --cache-from $REGISTRY/$PROJECT_NAME:cache-core \
        --cache-from $REGISTRY/$PROJECT_NAME:cache-extras \
        --cache-from $REGISTRY/$PROJECT_NAME:latest \
        --tag $REGISTRY/$PROJECT_NAME:$VERSION \
        --tag $REGISTRY/$PROJECT_NAME:latest \
        backend/
}

# 推送镜像到注册表
push_images() {
    if [ "$PUSH_TO_REGISTRY" = "true" ]; then
        echo_info "推送镜像到注册表..."
        
        if [ "$REBUILD_CORE" = true ]; then
            docker push $REGISTRY/$PROJECT_NAME:cache-core
            docker push $REGISTRY/$PROJECT_NAME:cache-core-$VERSION
        fi
        
        if [ "$REBUILD_EXTRAS" = true ]; then
            docker push $REGISTRY/$PROJECT_NAME:cache-extras
            docker push $REGISTRY/$PROJECT_NAME:cache-extras-$VERSION
        fi
        
        docker push $REGISTRY/$PROJECT_NAME:$VERSION
        docker push $REGISTRY/$PROJECT_NAME:latest
    fi
}

# 更新MD5哈希
update_checksums() {
    echo_info "更新依赖文件校验和..."
    md5sum backend/requirements.core.txt > backend/requirements.core.txt.md5
    md5sum backend/requirements.extras.txt > backend/requirements.extras.txt.md5
}

# 清理临时镜像
cleanup() {
    echo_info "清理临时镜像..."
    # 删除未标记的镜像
    docker image prune -f
}

# 主执行流程
main() {
    echo_info "=== Docker优化构建开始 ==="
    echo_info "版本标签: $VERSION"
    
    # 启用Docker BuildKit
    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1
    
    # 检查依赖变化
    check_dependency_changes
    
    # 拉取现有缓存镜像
    echo_info "拉取现有缓存镜像..."
    docker pull $REGISTRY/$PROJECT_NAME:cache-core || echo_warn "核心缓存镜像不存在"
    docker pull $REGISTRY/$PROJECT_NAME:cache-extras || echo_warn "可变依赖缓存镜像不存在"
    docker pull $REGISTRY/$PROJECT_NAME:latest || echo_warn "最新镜像不存在"
    
    # 构建过程
    build_cache_layers
    build_final_image
    push_images
    update_checksums
    cleanup
    
    echo_info "=== Docker优化构建完成 ==="
    echo_info "新镜像标签: $REGISTRY/$PROJECT_NAME:$VERSION"
}

# 参数处理
while [[ $# -gt 0 ]]; do
    case $1 in
        --push)
            PUSH_TO_REGISTRY="true"
            shift
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        *)
            echo_error "未知参数: $1"
            exit 1
            ;;
    esac
done

# 执行主流程
main