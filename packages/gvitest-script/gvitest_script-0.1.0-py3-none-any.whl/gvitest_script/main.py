#!/usr/bin/env python3
"""
Script Server - 主入口文件

基于 Jinja2 模板引擎的脚本生成服务器
支持预期结果列表、实时状态追踪、独立日志文件等核心功能
"""

import os
import sys
import argparse
import asyncio
import logging
from pathlib import Path
from typing import Optional

from .api.api_service import APIService
from .api.status_tracking_api import create_status_tracking_api
from .utils.file_server import init_file_server
import uvicorn


def setup_logging(log_level: str = "INFO"):
    """设置日志配置"""
    from .utils.logging_config import setup_cross_platform_logging
    setup_cross_platform_logging(log_level)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Script Server - Jinja2模板引擎脚本生成服务器"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="服务器主机地址 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8090,
        help="服务器端口 (默认: 8090)"
    )
    
    parser.add_argument(
        "--workspace",
        type=Path,
        help="工作空间根目录路径"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别 (默认: INFO)"
    )
    
    parser.add_argument(
        "--status-tracking-port",
        type=int,
        default=8091,
        help="状态追踪API端口 (默认: 8091)"
    )
    
    parser.add_argument(
        "--enable-status-tracking",
        action="store_true",
        help="启用状态追踪API服务"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用热重载 (开发模式)"
    )
    
    parser.add_argument(
        "--file-server-url",
        type=str,
        default="http://localhost:8080",
        help="文件服务器URL (默认: http://localhost:8080)"
    )
    
    return parser.parse_args()


def get_workspace_path(args_workspace: Optional[Path] = None) -> Path:
    """获取工作空间路径，优先级：命令行 > 环境变量 > 项目目录"""
    
    if args_workspace:
        workspace = args_workspace.resolve()
    elif (env_path := os.getenv("WORKSPACE_PATH")):
        workspace = Path(env_path).resolve()
    else:
        # 默认使用项目目录下的 workspace
        workspace = Path(__file__).parent.parent.parent / "script_workspace"
    
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


async def start_status_tracking_service(workspace_root: Path, port: int):
    """启动状态追踪服务"""
    try:
        app = create_status_tracking_api(workspace_root)
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        logging.info(f"状态追踪API服务启动: http://0.0.0.0:{port}")
        await server.serve()
    except Exception as e:
        logging.error(f"状态追踪服务启动失败: {e}")


async def start_main_service(workspace_root: Path, host: str, port: int, reload: bool = False):
    """启动主API服务"""
    try:
        service = APIService(workspace_root, host, port)
        if reload:
            # 开发模式使用uvicorn的热重载
            config = uvicorn.Config(
                service.app,
                host=host,
                port=port,
                log_level="info",
                reload=True
            )
            server = uvicorn.Server(config)
            logging.info(f"主API服务启动 (热重载模式): http://{host}:{port}")
            await server.serve()
        else:
            logging.info(f"主API服务启动: http://{host}:{port}")
            await service.start_async()
    except Exception as e:
        logging.error(f"主API服务启动失败: {e}")


async def main_async():
    """异步主函数"""
    args = parse_arguments()
    
    # 设置日志
    setup_logging(args.log_level)
    
    # 获取工作空间路径
    workspace_root = get_workspace_path(args.workspace)
    logging.info(f"使用工作空间: {workspace_root}")
    
    # 初始化文件服务器（如果提供了URL）
    if args.file_server_url:
        try:
            file_server = init_file_server(args.file_server_url, workspace_root)
            # 检查文件服务器连接
            if file_server.health_check():
                logging.info(f"文件服务器连接成功: {args.file_server_url}")
                logging.info(f"图像缓存目录: {file_server.get_local_images_path()}")
            else:
                logging.warning(f"文件服务器连接失败: {args.file_server_url}")
        except Exception as e:
            logging.error(f"文件服务器初始化失败: {e}")
    else:
        logging.info("未提供文件服务器URL，跳过文件服务器初始化")
    
    # 创建任务列表
    tasks = []
    
    # 主API服务任务
    main_task = asyncio.create_task(
        start_main_service(workspace_root, args.host, args.port, args.reload)
    )
    tasks.append(main_task)
    
    # 状态追踪服务任务（如果启用）
    if args.enable_status_tracking:
        status_task = asyncio.create_task(
            start_status_tracking_service(workspace_root, args.status_tracking_port)
        )
        tasks.append(status_task)
    
    # 等待所有服务
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logging.info("收到中断信号，正在关闭服务...")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


def main():
    """主函数"""
    try:
        # 运行异步主函数
        asyncio.run(main_async())
        
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        logging.error(f"服务启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
