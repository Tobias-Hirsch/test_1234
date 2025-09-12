#!/bin/bash
# prepare for docker-compose
# 创建 Nginx 目录
mkdir -p ./nginx/html

# 创建 MySQL 数据卷目录
mkdir -p ./mysql_data

# 创建 Milvus 数据卷目录
mkdir -p ./milvus_data

# 创建 Minio 数据卷目录
mkdir -p ./minio_data