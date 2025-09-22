"""
日志查询API服务
支持查询已完成的日志和实时日志查询
"""
import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from ..utils.logging_config import SAFE_EMOJIS as EMOJI


class LogQueryRequest(BaseModel):
    """日志查询请求模型"""
    script_id: str
    lines: Optional[int] = None  # 查询的行数，None表示全部
    from_end: bool = True  # 是否从末尾开始查询


class LogListResponse(BaseModel):
    """日志列表响应模型"""
    script_id: str
    log_files: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，保持与其他模型的一致性"""
        return self.model_dump()


class LogContentResponse(BaseModel):
    """日志内容响应模型"""
    script_id: str
    log_file: str
    content: str
    total_lines: int
    queried_lines: int
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，保持与其他模型的一致性"""
        return self.model_dump()


class LogQueryAPI:
    """日志查询API服务"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.websocket_connections = {}  # script_id -> List[WebSocket]
        self.global_websocket_connections = []  # 全局日志连接
        self.completed_tasks = set()  # 已完成的任务集合
        self.task_completion_times = {}  # script_id -> completion_time
        self.app = FastAPI()
        self._setup_routes()
    
    def _setup_routes(self):
        """设置API路由"""
        
        @self.app.get("/health")
        async def health_check():
            """健康检查"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/logs/{script_id}", response_model=LogListResponse)
        async def get_task_logs_route(script_id: str):
            """获取任务的所有日志文件列表"""
            return await self.get_task_logs(script_id)
        
        @self.app.get("/logs/{script_id}/latest", response_model=LogContentResponse)
        async def get_latest_log_route(
            script_id: str,
            lines: Optional[int] = Query(None, description="读取的行数，默认全部"),
            from_end: bool = Query(True, description="是否从末尾开始读取")
        ):
            """获取任务的最新日志内容"""
            return await self.get_latest_log(script_id, lines, from_end)
        
        @self.app.get("/logs/{script_id}/{log_filename}", response_model=LogContentResponse)
        async def get_specific_log_route(
            script_id: str,
            log_filename: str,
            lines: Optional[int] = Query(None, description="读取的行数，默认全部"),
            from_end: bool = Query(True, description="是否从末尾开始读取")
        ):
            """获取指定日志文件的内容"""
            return await self.get_specific_log(script_id, log_filename, lines, from_end)
        
        @self.app.websocket("/logs/{script_id}/realtime")
        async def realtime_log_stream_route(websocket: WebSocket, script_id: str):
            """实时日志流推送"""
            return await self.realtime_log_stream(websocket, script_id)
    
    async def get_task_logs(self, script_id: str) -> LogListResponse:
        """获取任务的所有日志文件列表"""
        try:
            log_dir = self.workspace_root / script_id / "logs"
            if not log_dir.exists():
                raise HTTPException(status_code=404, detail=f"任务 {script_id} 的日志目录不存在")
            
            log_files = []
            for log_file in log_dir.glob("*.log"):
                stat = log_file.stat()
                # 去掉.log后缀
                filename_without_ext = log_file.stem
                log_files.append({
                    "filename": filename_without_ext,
                    "size": stat.st_size,
                    "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "is_current": self._is_current_log(log_file.name)
                })
            
            # 按创建时间排序，最新的在前
            log_files.sort(key=lambda x: x["created_time"], reverse=True)
            
            return LogListResponse(
                script_id=script_id,
                log_files=log_files
            )
        
        except Exception as e:
            logging.error(f"获取任务日志列表失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取日志列表失败: {str(e)}")
    
    async def get_latest_log(self, script_id: str, lines: Optional[int] = None, from_end: bool = True) -> LogContentResponse:
        """获取任务的最新日志内容"""
        try:
            log_dir = self.workspace_root / script_id / "logs"
            if not log_dir.exists():
                raise HTTPException(status_code=404, detail=f"任务 {script_id} 的日志目录不存在")
            
            # 找到最新的日志文件
            log_files = list(log_dir.glob("*.log"))
            if not log_files:
                raise HTTPException(status_code=404, detail=f"任务 {script_id} 没有日志文件")
            
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            
            # 传入完整的文件名（带.log后缀）
            return await self._read_log_content(script_id, latest_log.name, lines, from_end)
        
        except Exception as e:
            logging.error(f"获取最新日志失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取最新日志失败: {str(e)}")
    
    async def get_specific_log(self, script_id: str, log_filename: str, lines: Optional[int] = None, from_end: bool = True) -> LogContentResponse:
        """获取指定日志文件的内容"""
        try:
            # 如果传入的filename没有.log后缀，自动添加
            if not log_filename.endswith('.log'):
                actual_filename = f"{log_filename}.log"
            else:
                actual_filename = log_filename
            
            return await self._read_log_content(script_id, actual_filename, lines, from_end)
        
        except Exception as e:
            logging.error(f"获取指定日志失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取日志失败: {str(e)}")
    
    async def realtime_log_stream(self, websocket: WebSocket, script_id: str):
        """实时日志流推送"""
        client_info = f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "unknown"
        logging.info(f"{EMOJI['connect']} WebSocket连接请求: script_id={script_id}, client={client_info}")
        
        try:
            await websocket.accept()
            logging.info(f"{EMOJI['success']} WebSocket连接已接受: script_id={script_id}, client={client_info}")
            
            # 添加到连接池
            if script_id not in self.websocket_connections:
                self.websocket_connections[script_id] = []
                self.websocket_connections[script_id].append(websocket)
            
            # 发送当前日志内容
            await self._send_current_log(websocket, script_id)
            
            # 开始实时监控
            await self._monitor_log_changes(websocket, script_id)
            
        except WebSocketDisconnect:
            logging.info(f"{EMOJI['disconnect']} WebSocket正常断开: script_id={script_id}, client={client_info}")
            self._remove_connection(script_id, websocket)
        except Exception as e:
            logging.error(f"{EMOJI['error']} 实时日志流异常: script_id={script_id}, client={client_info}, error={e}")
            try:
                await websocket.close()
            except:
                pass  # 忽略关闭WebSocket时的异常
            self._remove_connection(script_id, websocket)
    
    async def global_realtime_log_stream(self, websocket: WebSocket):
        """全局实时日志流推送 - 监控所有任务的日志"""
        client_info = f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "unknown"
        logging.info(f"{EMOJI['global']} 全局WebSocket连接请求: client={client_info}")
        
        try:
            await websocket.accept()
            logging.info(f"{EMOJI['success']} 全局WebSocket连接已接受: client={client_info}")
            
            # 添加到全局连接池
            self.global_websocket_connections.append(websocket)
            
            # 发送欢迎消息
            await websocket.send_json({
                "type": "connected",
                "message": "已连接到全局日志流",
                "timestamp": datetime.now().isoformat()
            })
            
            # 开始全局日志监控
            await self._monitor_global_log_changes(websocket)
            
        except WebSocketDisconnect:
            logging.info(f"{EMOJI['disconnect']} 全局WebSocket正常断开: client={client_info}")
            self._remove_global_connection(websocket)
        except Exception as e:
            logging.error(f"{EMOJI['error']} 全局实时日志流异常: client={client_info}, error={e}")
            try:
                await websocket.close()
            except:
                pass  # 忽略关闭WebSocket时的异常
            self._remove_global_connection(websocket)
    
    async def _read_log_content(self, script_id: str, log_filename: str, lines: Optional[int], from_end: bool) -> LogContentResponse:
        """读取日志文件内容"""
        log_file = self.workspace_root / script_id / "logs" / log_filename
        
        if not log_file.exists():
            raise HTTPException(status_code=404, detail=f"日志文件 {log_filename} 不存在")
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            
            total_lines = len(all_lines)
            
            if lines is None:
                # 读取全部内容
                content_lines = all_lines
                queried_lines = total_lines
            else:
                # 读取指定行数
                if from_end:
                    content_lines = all_lines[-lines:] if lines < total_lines else all_lines
                else:
                    content_lines = all_lines[:lines] if lines < total_lines else all_lines
                queried_lines = len(content_lines)
            
            content = ''.join(content_lines)
            
            # 返回时去掉.log后缀
            display_filename = log_filename[:-4] if log_filename.endswith('.log') else log_filename
            
            return LogContentResponse(
                script_id=script_id,
                log_file=display_filename,
                content=content,
                total_lines=total_lines,
                queried_lines=queried_lines,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"读取日志文件失败: {str(e)}")
    
    async def _send_current_log(self, websocket: WebSocket, script_id: str):
        """发送当前日志内容"""
        try:
            # 获取最新日志
            log_dir = self.workspace_root / script_id / "logs"
            if not log_dir.exists():
                await websocket.send_json({
                    "type": "error",
                    "message": f"任务 {script_id} 的日志目录不存在"
                })
                return
            
            log_files = list(log_dir.glob("*.log"))
            if not log_files:
                await websocket.send_json({
                    "type": "info",
                    "message": f"任务 {script_id} 暂无日志文件"
                })
                return
            
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            
            # 发送当前日志内容（最后50行）
            log_response = await self._read_log_content(script_id, latest_log.name, 50, True)
            await websocket.send_json({
                "type": "initial",
                "data": log_response.to_dict()
            })
            
        except Exception as e:
            logging.error(f"发送当前日志失败: {e}")
            await websocket.send_json({
                "type": "error",
                "message": f"发送日志失败: {str(e)}"
            })
    
    async def _monitor_log_changes(self, websocket: WebSocket, script_id: str):
        """监控日志文件变化"""
        log_dir = self.workspace_root / script_id / "logs"
        last_size = 0
        last_file = None
        
        while True:
            try:
                # 检查WebSocket连接状态
                if websocket.client_state.name != "CONNECTED":
                    logging.info(f"WebSocket连接已断开: {websocket.client_state.name}")
                    break
                
                # 找到最新的日志文件
                log_files = list(log_dir.glob("*.log"))
                if not log_files:
                    await asyncio.sleep(1)
                    continue
                
                current_file = max(log_files, key=lambda f: f.stat().st_mtime)
                current_size = current_file.stat().st_size
                
                # 如果文件变化或大小变化
                if current_file != last_file or current_size != last_size:
                    if current_file != last_file:
                        # 新文件，发送完整内容
                        log_response = await self._read_log_content(script_id, current_file.name, 50, True)
                        await websocket.send_json({
                            "type": "new_file",
                            "data": log_response.to_dict()
                        })
                    elif current_size > last_size:
                        # 文件增长，发送新增内容
                        await self._send_incremental_content(websocket, current_file, last_size)
                    
                    last_file = current_file
                    last_size = current_size
                
                await asyncio.sleep(0.5)  # 500ms检查一次
                
            except Exception as e:
                logging.error(f"监控日志变化异常: {e}")
                # 如果是WebSocket相关异常，退出循环
                if ("websocket" in str(e).lower() or 
                    "connection" in str(e).lower() or 
                    "send" in str(e).lower() or
                    "close" in str(e).lower()):
                    logging.info("WebSocket连接异常，退出监控循环")
                    break
                await asyncio.sleep(1)
    
    async def _send_incremental_content(self, websocket: WebSocket, log_file: Path, last_position: int):
        """发送增量日志内容"""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                f.seek(last_position)
                new_content = f.read()
            
            if new_content:
                # 去掉.log后缀
                display_filename = log_file.name[:-4] if log_file.name.endswith('.log') else log_file.name
                await websocket.send_json({
                    "type": "incremental",
                    "data": {
                        "log_file": display_filename,
                        "content": new_content,
                        "timestamp": datetime.now().isoformat()
                    }
                })
                
        except Exception as e:
            logging.error(f"发送增量内容失败: {e}")
            raise  # 重新抛出异常，让上层处理WebSocket断开
    
    async def _monitor_global_log_changes(self, websocket: WebSocket):
        """监控全局日志文件变化"""
        monitored_files = {}  # file_path -> last_size
        
        while True:
            try:
                # 检查WebSocket连接状态
                if websocket.client_state.name != "CONNECTED":
                    logging.info(f"全局WebSocket连接已断开: {websocket.client_state.name}")
                    break
                
                # 扫描所有任务的日志目录
                for task_dir in self.workspace_root.iterdir():
                    if not task_dir.is_dir():
                        continue
                    
                    script_id = task_dir.name
                    
                    # 检查任务是否已完成，如果完成超过2秒才停止监控
                    if script_id in self.task_completion_times:
                        if time.time() - self.task_completion_times[script_id] > 2.0:
                            self.completed_tasks.add(script_id)
                            del self.task_completion_times[script_id]
                            continue
                    
                    # 跳过已完成的任务
                    if script_id in self.completed_tasks:
                        continue
                    
                    log_dir = task_dir / "logs"
                    if not log_dir.exists():
                        continue
                    
                    # 检查该任务下的所有日志文件
                    for log_file in log_dir.glob("*.log"):
                        try:
                            current_size = log_file.stat().st_size
                            file_path = str(log_file)
                            
                            # 如果是新文件或文件增长了
                            if file_path not in monitored_files:
                                # 新文件，发送最后10行
                                monitored_files[file_path] = current_size
                                await self._send_global_log_update(websocket, task_dir.name, log_file, "new_file", lines=10)
                            elif current_size > monitored_files[file_path]:
                                # 文件增长，发送新增内容
                                await self._send_global_incremental_content(websocket, task_dir.name, log_file, monitored_files[file_path])
                                monitored_files[file_path] = current_size
                        except Exception as file_error:
                            logging.debug(f"处理日志文件异常: {log_file}, error={file_error}")
                
                await asyncio.sleep(0.5)  # 检查间隔
                
            except Exception as e:
                logging.error(f"全局日志监控异常: {e}")
                await asyncio.sleep(1)
    
    async def _send_global_log_update(self, websocket: WebSocket, script_id: str, log_file: Path, update_type: str, lines: int = 50):
        """发送全局日志更新"""
        try:
            log_response = await self._read_log_content(script_id, log_file.name, lines, True)
            await websocket.send_json({
                "type": update_type,
                "script_id": script_id,
                "data": log_response.to_dict(),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logging.error(f"发送全局日志更新失败: {e}")
    
    async def _send_global_incremental_content(self, websocket: WebSocket, script_id: str, log_file: Path, last_size: int):
        """发送全局增量日志内容"""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                f.seek(last_size)
                new_content = f.read()
            
            if new_content.strip():
                await websocket.send_json({
                    "type": "incremental",
                    "script_id": script_id,
                    "log_file": log_file.stem,  # 去掉.log后缀
                    "content": new_content,
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            logging.error(f"发送全局增量内容失败: {e}")
    
    def _is_current_log(self, filename: str) -> bool:
        """判断是否是当前正在写入的日志文件"""
        # 简单判断：最新的日志文件认为是当前文件
        # 实际应用中可以根据业务逻辑调整
        return True
    
    def _remove_connection(self, script_id: str, websocket: WebSocket):
        """移除WebSocket连接"""
        if script_id in self.websocket_connections:
            if websocket in self.websocket_connections[script_id]:
                self.websocket_connections[script_id].remove(websocket)
            
            # 如果没有连接了，清理空列表
            if not self.websocket_connections[script_id]:
                del self.websocket_connections[script_id] 
    
    def _remove_global_connection(self, websocket: WebSocket):
        """移除全局WebSocket连接"""
        try:
            if websocket in self.global_websocket_connections:
                self.global_websocket_connections.remove(websocket)
                logging.info("全局WebSocket连接已移除")
        except Exception as e:
            logging.error(f"移除全局WebSocket连接失败: {e}")
    
    def mark_task_completed(self, script_id: str):
        """记录任务完成时间，2秒后才停止监控其日志文件"""
        self.task_completion_times[script_id] = time.time()
        logging.info(f"任务 {script_id} 已完成，将在2秒后停止日志监控")
    
    async def broadcast_to_global_connections(self, message: dict):
        """向所有全局连接广播消息"""
        if not self.global_websocket_connections:
            return
        
        # 如果是任务完成相关的消息，标记任务为完成
        if message.get("type") in ["task_completed", "task_failed", "task_timeout", "task_error"]:
            script_id = message.get("script_id")
            if script_id:
                self.mark_task_completed(script_id)
        
        disconnected = []
        for websocket in self.global_websocket_connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)
        
        # 清理断开的连接
        for ws in disconnected:
            self._remove_global_connection(ws) 