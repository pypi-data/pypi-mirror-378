from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import asyncio
import gzip
import base64
from datetime import datetime
import logging
from pydantic import BaseModel




class StatusResponse(BaseModel):
    """状态响应模型"""
    script_id: str
    current_status: Dict[str, Any]
    task_summary: Dict[str, Any]
    history: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，保持与其他模型的一致性"""
        return self.model_dump()


class StatusUpdateRequest(BaseModel):
    """状态更新请求模型"""
    script_id: str
    status_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，保持与其他模型的一致性"""
        return self.model_dump()


class StatusTrackingAPI:
    """状态追踪API服务"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.app = FastAPI(title="Script Generator Status Tracking API", version="1.0.0")
        self.websocket_connections: Dict[str, List[WebSocket]] = {}
        
        # 设置API路由
        self._setup_routes()
    
    def _setup_routes(self):
        """设置API路由"""
        
        @self.app.get("/health")
        async def health_check():
            """健康检查"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/status/{script_id}", response_model=StatusResponse)
        async def get_script_status(script_id: str, include_history: bool = False):
            """获取任务状态"""
            try:
                status_data = await self._read_status_file(script_id)
                if not status_data:
                    raise HTTPException(status_code=404, detail=f"Script {script_id} not found")
                
                response = StatusResponse(
                    script_id=script_id,
                    current_status=status_data.get("current_status", {}),
                    task_summary=status_data.get("task_summary", {}),
                    history=status_data.get("history", []) if include_history else None
                )
                
                return response
            
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"获取任务状态失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/status/{script_id}/progress")
        async def get_script_progress(script_id: str):
            """获取任务进度"""
            try:
                status_data = await self._read_status_file(script_id)
                if not status_data:
                    raise HTTPException(status_code=404, detail=f"Script {script_id} not found")
                
                current_status = status_data.get("current_status", {})
                task_summary = status_data.get("task_summary", {})
                
                progress_info = {
                    "script_id": script_id,
                    "progress_percent": current_status.get("progress_percent", 0.0),
                    "current_step": current_status.get("current_step", 0),
                    "total_steps": task_summary.get("total_steps", 0),
                    "completed_steps": task_summary.get("completed_steps", 0),
                    "status": current_status.get("status", "unknown"),
                    "eta_seconds": current_status.get("eta_seconds"),
                    "estimated_completion": current_status.get("estimated_completion"),
                    # 新增：支持控制流和验证状态
                    "control_flow_info": current_status.get("control_flow_info", {}),
                    "validation_status": current_status.get("validation_status", {}),
                    "expression_evaluation": current_status.get("expression_evaluation", {})
                }
                
                return progress_info
            
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"获取任务进度失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/status/{script_id}/control-flow")
        async def get_script_control_flow_status(script_id: str):
            """获取控制流状态"""
            try:
                status_data = await self._read_status_file(script_id)
                if not status_data:
                    raise HTTPException(status_code=404, detail=f"Script {script_id} not found")
                
                current_status = status_data.get("current_status", {})
                
                control_flow_info = {
                    "script_id": script_id,
                    "current_control_flow": current_status.get("control_flow_info", {}),
                    "active_branches": current_status.get("active_branches", []),
                    "loop_iterations": current_status.get("loop_iterations", {}),
                    "condition_evaluations": current_status.get("condition_evaluations", []),
                    "validation_results": current_status.get("validation_results", [])
                }
                
                return control_flow_info
            
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"获取控制流状态失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/status/{script_id}/validation")
        async def get_script_validation_status(script_id: str):
            """获取验证状态"""
            try:
                status_data = await self._read_status_file(script_id)
                if not status_data:
                    raise HTTPException(status_code=404, detail=f"Script {script_id} not found")
                
                current_status = status_data.get("current_status", {})
                
                validation_info = {
                    "script_id": script_id,
                    "validation_status": current_status.get("validation_status", {}),
                    "expression_evaluations": current_status.get("expression_evaluations", []),
                    "validation_results": current_status.get("validation_results", []),
                    "expected_results": current_status.get("expected_results", []),
                    "checkpoint_status": current_status.get("checkpoint_status", [])
                }
                
                return validation_info
            
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"获取验证状态失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/status/{script_id}/screenshots")
        async def get_script_screenshots(script_id: str, limit: int = 10):
            """获取任务截图信息"""
            try:
                status_data = await self._read_status_file(script_id)
                if not status_data:
                    raise HTTPException(status_code=404, detail=f"Script {script_id} not found")
                
                # 从历史记录中提取截图信息
                history = status_data.get("history", [])
                screenshots = []
                
                for entry in reversed(history[-limit:]):
                    if entry.get("screenshot_url") or entry.get("screenshot_path"):
                        screenshots.append({
                            "timestamp": entry.get("timestamp"),
                            "step_name": entry.get("step_name"),
                            "screenshot_url": entry.get("screenshot_url"),
                            "screenshot_path": entry.get("screenshot_path") if entry.get("screenshot_path") else None
                        })
                
                return {
                    "script_id": script_id,
                    "screenshots": screenshots,
                    "total_count": len(screenshots)
                }
            
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"获取任务截图失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/status/{script_id}/update")
        async def update_script_status(script_id: str, request: StatusUpdateRequest):
            """更新任务状态（外部调用）"""
            try:
                # 这里可以实现外部状态更新逻辑
                # 主要用于接收来自外部系统的状态更新
                
                # 广播给WebSocket连接
                await self._broadcast_to_websockets(script_id, request.status_data)
                
                return {"status": "success", "message": "Status updated successfully"}
            
            except Exception as e:
                logging.error(f"更新任务状态失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/tasks")
        async def list_tasks():
            """列出所有任务"""
            try:
                tasks = []
                
                # 扫描工作空间目录
                for task_dir in self.workspace_root.iterdir():
                    if task_dir.is_dir():
                        status_dir = task_dir / "status"
                        if status_dir.exists():
                            status_file = status_dir / "real_time_status.json"
                            if status_file.exists():
                                try:
                                    status_data = await self._read_status_file(task_dir.name)
                                    if status_data:
                                        task_summary = status_data.get("task_summary", {})
                                        current_status = status_data.get("current_status", {})
                                        
                                        tasks.append({
                                            "script_id": task_dir.name,
                                            "status": current_status.get("status", "unknown"),
                                            "progress_percent": current_status.get("progress_percent", 0.0),
                                            "start_time": task_summary.get("start_time"),
                                            "total_steps": task_summary.get("total_steps", 0),
                                            "completed_steps": task_summary.get("completed_steps", 0)
                                        })
                                except Exception as e:
                                    logging.warning(f"读取任务状态失败 {task_dir.name}: {e}")
                
                return {"tasks": tasks, "total_count": len(tasks)}
            
            except Exception as e:
                logging.error(f"列出任务失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/ws/{script_id}")
        async def websocket_endpoint(websocket: WebSocket, script_id: str):
            """WebSocket实时状态推送"""
            await websocket.accept()
            
            # 添加到连接列表
            if script_id not in self.websocket_connections:
                self.websocket_connections[script_id] = []
            self.websocket_connections[script_id].append(websocket)
            
            try:
                # 发送当前状态
                current_status = await self._read_status_file(script_id)
                if current_status:
                    await websocket.send_json({
                        "type": "current_status",
                        "data": current_status
                    })
                
                # 保持连接并处理消息
                while True:
                    try:
                        # 等待客户端消息（心跳等）
                        message = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
                        
                        # 处理心跳
                        if message.get("type") == "ping":
                            await websocket.send_json({"type": "pong"})
                    
                    except asyncio.TimeoutError:
                        # 发送心跳
                        await websocket.send_json({"type": "heartbeat", "timestamp": datetime.now().isoformat()})
            
            except WebSocketDisconnect:
                # 从连接列表中移除
                if script_id in self.websocket_connections:
                    self.websocket_connections[script_id].remove(websocket)
                    if not self.websocket_connections[script_id]:
                        del self.websocket_connections[script_id]
            
            except Exception as e:
                logging.error(f"WebSocket连接错误: {e}")
                try:
                    await websocket.close()
                except:
                    pass
        
        @self.app.websocket("/ws/all")
        async def websocket_all_tasks(websocket: WebSocket):
            """监听所有任务的WebSocket连接"""
            await websocket.accept()
            
            # 添加到全局连接列表
            if "ALL" not in self.websocket_connections:
                self.websocket_connections["ALL"] = []
            self.websocket_connections["ALL"].append(websocket)
            
            try:
                # 发送所有任务的当前状态
                tasks_status = await self._get_all_tasks_status()
                await websocket.send_json({
                    "type": "all_tasks_status",
                    "data": tasks_status
                })
                
                # 保持连接
                while True:
                    try:
                        message = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
                        if message.get("type") == "ping":
                            await websocket.send_json({"type": "pong"})
                    except asyncio.TimeoutError:
                        await websocket.send_json({"type": "heartbeat", "timestamp": datetime.now().isoformat()})
            
            except WebSocketDisconnect:
                if "ALL" in self.websocket_connections:
                    self.websocket_connections["ALL"].remove(websocket)
                    if not self.websocket_connections["ALL"]:
                        del self.websocket_connections["ALL"]
            
            except Exception as e:
                logging.error(f"全局WebSocket连接错误: {e}")
    
    async def _read_status_file(self, script_id: str) -> Optional[Dict[str, Any]]:
        """读取状态文件"""
        try:
            status_file = self.workspace_root / script_id / "status" / "real_time_status.json"
            
            if not status_file.exists():
                return None
            
            # 使用重试机制读取JSON文件，避免并发访问问题
            data = await self._read_json_file_with_retry(status_file)
            if not data:
                return None
            
            # 处理压缩数据
            if data.get("compressed"):
                compressed_data = base64.b64decode(data["data"])
                decompressed_data = gzip.decompress(compressed_data)
                data = json.loads(decompressed_data.decode('utf-8'))
            
            return data
        
        except Exception as e:
            logging.error(f"读取状态文件失败 {script_id}: {e}")
            return None
    
    async def _read_json_file_with_retry(self, file_path: Path, max_retries: int = 3, retry_delay: float = 0.1) -> Dict[str, Any]:
        """带重试机制的异步读取JSON文件，处理并发访问问题"""
        import asyncio
        
        for attempt in range(max_retries):
            try:
                # 使用线程池执行文件读取，避免阻塞事件循环
                def read_file():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:  # 文件为空
                            raise json.JSONDecodeError("Empty file", "", 0)
                        return json.loads(content)
                
                return await asyncio.get_event_loop().run_in_executor(None, read_file)
                
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    logging.debug(f"JSON读取失败（尝试 {attempt + 1}/{max_retries}）: {file_path}, 错误: {e}")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    logging.warning(f"JSON文件读取失败，已重试 {max_retries} 次: {file_path}")
                    return {}
            except FileNotFoundError:
                logging.debug(f"文件不存在: {file_path}")
                return {}
            except Exception as e:
                if attempt < max_retries - 1:
                    logging.debug(f"文件读取异常（尝试 {attempt + 1}/{max_retries}）: {file_path}, 错误: {e}")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    logging.error(f"读取JSON文件失败: {file_path}, 错误: {e}")
                    return {}
        
        return {}
    
    async def _get_all_tasks_status(self) -> List[Dict[str, Any]]:
        """获取所有任务状态"""
        tasks = []
        
        for task_dir in self.workspace_root.iterdir():
            if task_dir.is_dir():
                status_data = await self._read_status_file(task_dir.name)
                if status_data:
                    tasks.append({
                        "script_id": task_dir.name,
                        "current_status": status_data.get("current_status", {}),
                        "task_summary": status_data.get("task_summary", {})
                    })
        
        return tasks
    
    async def _broadcast_to_websockets(self, script_id: str, status_data: Dict[str, Any]):
        """广播状态更新到WebSocket连接"""
        message = {
            "type": "status_update",
            "script_id": script_id,
            "data": status_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # 发送给特定任务的连接
        if script_id in self.websocket_connections:
            disconnected = []
            for websocket in self.websocket_connections[script_id]:
                try:
                    await websocket.send_json(message)
                except:
                    disconnected.append(websocket)
            
            # 清理断开的连接
            for ws in disconnected:
                                    self.websocket_connections[script_id].remove(ws)
        
        # 发送给全局连接
        if "ALL" in self.websocket_connections:
            disconnected = []
            for websocket in self.websocket_connections["ALL"]:
                try:
                    await websocket.send_json(message)
                except:
                    disconnected.append(websocket)
            
            # 清理断开的连接
            for ws in disconnected:
                self.websocket_connections["ALL"].remove(ws)


# 创建API实例的工厂函数
def create_status_tracking_api(workspace_root: Path) -> FastAPI:
    """创建状态追踪API实例"""
    api = StatusTrackingAPI(workspace_root)
    return api.app