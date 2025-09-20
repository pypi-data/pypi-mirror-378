"""
API客户端模块

提供登录和运行功能的API客户端类。
"""

import requests
import json
import base64
import os
import io
from pathlib import Path
from typing import Optional, Dict, Any, Union, List, TypedDict
import logging
from dataclasses import dataclass

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# 设置日志
logger = logging.getLogger(__name__)

@dataclass
class RunResult:
    success: bool
    answer: Optional[str]
    token: Optional[float]

class Client:
    """
    Aditor API客户端类
    
    提供登录认证和API调用功能。
    """
    
    def __init__(self, base_url: str = "https://fenshen.top:33", memory_file: str = "aditor_memory.json"):
        """
        初始化客户端
        Args:
            base_url (str): API基础URL，默认为本地服务器
            memory_file (str): 记忆文件路径，默认为"aditor_memory.json"
        """
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.session = requests.Session()
        
        # 记忆管理
        self.memory_file = Path(memory_file)
        self.memory_data: List[str] = []
        self._load_memory()
        
        # 设置默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Aditor-Python-Client/0.1.0'
        })
    
    def login(self, username: str, password: str) -> bool:
        """
        用户登录
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            bool: 登录是否成功
            
        Raises:
            requests.RequestException: 网络请求异常
            ValueError: 登录参数无效
            
        Example:
            >>> client = AditorClient()
            >>> success = client.login("13800138000", "your_secret")
            >>> if success:
            ...     print("登录成功!")
        """
        if not username or not password:
            raise ValueError("用户名和密码不能为空")
        
        login_url = f"{self.base_url}/plug/login"
        login_data = {
            "phone": username,
            "secret": password
        }
        
        try:
            logger.info(f"正在登录到 {login_url}")
            response = self.session.post(login_url, json=login_data, timeout=30)
            
            # 检查HTTP状态码
            if response.status_code == 200:
                result = response.json()
                logger.info(f"登录响应: {result}")
                
                # 检查登录结果 - 根据您的API响应格式
                if result.get("success") == True:
                    self.token = result.get("token")
                    
                    if self.token:
                        # 更新请求头，添加认证token
                        self.session.headers.update({
                            'Authorization': f'Bearer {self.token}'
                        })
                        logger.info("登录成功，已获取token")
                        return True
                    else:
                        logger.error("登录响应中未找到token")
                        return False
                else:
                    error_msg = result.get("message") or result.get("msg") or "登录失败"
                    logger.error(f"登录失败: {error_msg}")
                    return False
            else:
                logger.error(f"登录请求失败，状态码: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.error("无法连接到服务器，请检查网络连接和服务器地址")
            return False
        except requests.exceptions.Timeout:
            logger.error("登录请求超时")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"登录请求异常: {e}")
            return False
        except json.JSONDecodeError:
            logger.error("服务器响应格式错误")
            return False
        except Exception as e:
            logger.error(f"登录过程中发生未知错误: {e}")
            return False
    
    def _detect_image_type(self, image_input: Union[str, bytes]) -> str:
        """
        检测图片类型
        
        Returns:
            str: 'url', 'local', 'base64', 'bytes'
        """
        if isinstance(image_input, bytes):
            return 'bytes'
        
        if isinstance(image_input, str):
            if image_input.startswith(('http://', 'https://')):
                return 'url'
            elif image_input.startswith('data:image/') or image_input.startswith('/9j/') or image_input.startswith('iVBOR'):
                return 'base64'
            else:
                return 'local'
        
        raise ValueError("不支持的图片格式")
    
    def _compress_image_base64(self, image_base64: str, max_size: tuple = (1024, 1024), quality: int = 85) -> str:
        """
        压缩base64图片
        
        Args:
            image_base64: base64编码的图片
            max_size: 最大尺寸 (width, height)，默认1024x1024
            quality: JPEG质量 (1-100)，默认85
            
        Returns:
            str: 压缩后的base64图片
        """
        if not PIL_AVAILABLE:
            logger.warning("Pillow库未安装，跳过图片压缩")
            return image_base64
        
        try:
            # 解码base64为字节
            image_bytes = base64.b64decode(image_base64)
            original_size = len(image_bytes)
            
            # 打开图片
            with Image.open(io.BytesIO(image_bytes)) as img:
                # 获取原始信息
                original_format = img.format or 'JPEG'
                original_dimensions = img.size
                
                # 转换为RGB模式（确保兼容性）
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 有透明度的图片转换为RGB，白色背景
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 计算新尺寸（保持比例）
                new_size = self._calculate_new_size(img.size, max_size)
                
                # 如果需要调整尺寸
                if new_size != img.size:
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 压缩并保存到字节流
                output_buffer = io.BytesIO()
                img.save(output_buffer, format='JPEG', quality=quality, optimize=True)
                
                # 转换回base64
                compressed_bytes = output_buffer.getvalue()
                compressed_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
                
                # 计算压缩率
                compressed_size = len(compressed_bytes)
                compression_ratio = (1 - compressed_size / original_size) * 100
                
                logger.info(f"图片压缩完成: {original_dimensions} -> {new_size}, "
                          f"大小: {original_size//1024}KB -> {compressed_size//1024}KB "
                          f"(压缩率: {compression_ratio:.1f}%)")
                
                return compressed_base64
                
        except Exception as e:
            logger.error(f"图片压缩失败: {e}")
            logger.info("返回原始图片")
            return image_base64
    
    def _calculate_new_size(self, original_size: tuple, max_size: tuple) -> tuple:
        """
        计算新的图片尺寸，保持宽高比
        
        Args:
            original_size: 原始尺寸 (width, height)
            max_size: 最大尺寸 (width, height)
            
        Returns:
            tuple: 新尺寸 (width, height)
        """
        width, height = original_size
        max_width, max_height = max_size
        
        # 如果图片已经小于最大尺寸，不需要调整
        if width <= max_width and height <= max_height:
            return original_size
        
        # 计算缩放比例
        width_ratio = max_width / width
        height_ratio = max_height / height
        ratio = min(width_ratio, height_ratio)
        
        # 计算新尺寸
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        return (new_width, new_height)
    
    def _process_local_image(self, image_path: str, max_size: tuple = (1024, 1024), quality: int = 85) -> str:
        """
        处理本地图片：读取并压缩
        """
        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            raise ValueError(f"图片文件不存在: {image_path}")
        
        try:
            with open(image_path_obj, 'rb') as f:
                image_data = f.read()
            
            # 转换为base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 压缩图片
            compressed_base64 = self._compress_image_base64(image_base64, max_size, quality)
            
            logger.info(f"已读取并处理本地图片: {image_path}")
            return compressed_base64
            
        except Exception as e:
            raise ValueError(f"读取图片文件失败: {e}")
    
    def _process_bytes_image(self, image_bytes: bytes, max_size: tuple = (1024, 1024), quality: int = 85) -> str:
        """
        处理字节图片：转换并压缩
        """
        # 转换为base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # 压缩图片
        compressed_base64 = self._compress_image_base64(image_base64, max_size, quality)
        
        logger.info("已处理字节图片")
        return compressed_base64
    
    def _process_base64_image(self, image_base64: str, max_size: tuple = (1024, 1024), quality: int = 85) -> str:
        """
        处理base64图片：清理格式并压缩
        """
        # 清理data URL前缀
        if image_base64.startswith('data:image/'):
            clean_base64 = image_base64.split(',', 1)[1] if ',' in image_base64 else image_base64
        else:
            clean_base64 = image_base64
        
        # 压缩图片
        compressed_base64 = self._compress_image_base64(clean_base64, max_size, quality)
        
        logger.info("已处理base64图片")
        return compressed_base64
    
    def run(self, 
            app_id: Optional[int] = None,
            text: str = "", 
            image: Optional[Union[str, bytes]] = None,
            **kwargs) -> RunResult:
        """
        执行API调用 - 增强版，支持智能图片处理
        
        Args:
            app_id (int, optional): 应用ID
            text (str): 要处理的文本内容,可为空
            image (str): 要处理的图片内容,可为空
            **kwargs: 其他参数
            
        Returns:
            type: RunResult
            
        Raises:
            RuntimeError: 未登录或token无效
            ValueError: 图片格式不支持
            requests.RequestException: 网络请求异常
            
        Example:
            >>> client = Aditor()
            >>> client.login("13800138000", "your_secret")
            # URL图片 - 直接使用，性能最佳
            >>> result = client.run("分析这张图片", image="https://example.com/pic.jpg")
            
            # 本地图片
            >>> result = client.run("描述图片", image="./photo.jpg")
            
            # base64图片
            >>> result = client.run("识别文字", image="data:image/jpeg;base64,/9j/...")
            
            # 仅文本
            >>> result = client.run("你好，你是谁？")
        """
        endpoint = "/plug/run"
        image_max_size = (1400, 1400)
        image_quality = 85

        if not self.token:
            raise RuntimeError("请先登录获取token")
        
        # 构建请求数据
        request_data = {
            "text": text,
            **kwargs  # 包含其他参数
        }
        
        # 添加消息ID（保留0等有效值）
        if app_id is not None:
            try:
                request_data["id"] = int(app_id)
            except Exception:
                raise ValueError("app_id 必须为整数")
        
        # 处理图片
        if image is not None:
            try:
                image_type = self._detect_image_type(image)
                logger.info(f"检测到图片类型: {image_type}")
                
                if image_type == 'url':
                    # URL直接使用，不下载不转换
                    request_data["img"] = image
                    logger.info(f"使用URL图片: {image}")
                    
                elif image_type == 'local':
                    # 本地图片：读取 -> 压缩 -> base64
                    compressed_base64 = self._process_local_image(image, image_max_size, image_quality)
                    request_data["img"] = f"data:image/jpeg;base64,{compressed_base64}"
                    logger.info("本地图片已处理并压缩")
                    
                elif image_type == 'base64':
                    # base64图片：清理 -> 压缩 -> 使用
                    compressed_base64 = self._process_base64_image(image, image_max_size, image_quality)
                    request_data["img"] = f"data:image/jpeg;base64,{compressed_base64}"
                    logger.info("Base64图片已处理并压缩")
                    
                elif image_type == 'bytes':
                    # 字节图片：转换 -> 压缩 -> base64
                    compressed_base64 = self._process_bytes_image(image, image_max_size, image_quality)
                    request_data["img"] = f"data:image/jpeg;base64,{compressed_base64}"
                    logger.info("字节图片已处理并压缩")
                    
            except Exception as e:
                logger.error(f"图片处理失败: {e}")
                raise ValueError(f"图片处理失败: {e}")
        else:
            request_data["img"] = ""
        
        run_url = f"{self.base_url}{endpoint}"
        try:
            logger.info(f"正在调用API: {run_url}")
            logger.info(f"请求数据: {dict(request_data, **{'img': '[图片数据]' if 'img' in request_data else 'None'})}")
            response = self.session.post(run_url, json=request_data, timeout=60)  # 增加超时时间
            # 检查HTTP状态码
            if response.status_code == 200:
                result = response.json()
                # 尝试提取 answer + tokenused
                answer = None
                token_used = None
                try:
                    if isinstance(result, dict):
                        answer = result.get("answer")
                        if answer is None:
                            data = result.get("data")
                            if isinstance(data, dict):
                                answer = data.get("answer")
                        if answer is None:
                            inner = result.get("result")
                            if isinstance(inner, dict):
                                answer = inner.get("answer")
                        token_used = result.get("tokenused")
                        if token_used is None and isinstance(result.get("data"), dict):
                            token_used = result["data"].get("tokenused")
                        if token_used is None and isinstance(result.get("usage"), dict):
                            usage = result["usage"]
                            token_used = usage.get("total_tokens") or usage.get("tokens")
                        if token_used is not None:
                            try:
                                token_used = float(token_used) / 1000.0
                            except Exception:
                                token_used = None
                except Exception:
                    answer = None
                    token_used = None
                logger.info("API调用成功")
                return RunResult(success=True, answer=answer, token=token_used)

            elif response.status_code == 401:
                logger.error("token无效或已过期，请重新登录")
                self.token = None
                # 移除认证头
                if 'Authorization' in self.session.headers:
                    del self.session.headers['Authorization']
                raise RuntimeError("token无效或已过期，请重新登录")
            else:
                try:
                    masked_headers = dict(self.session.headers)
                    if 'Authorization' in masked_headers:
                        masked_headers['Authorization'] = 'Bearer ***'
                    safe_request_data = dict(request_data)
                    if 'img' in safe_request_data:
                        safe_request_data['img'] = '[图片数据]'
                    logger.error(
                        "API调用失败 | 状态码=%s | 原因=%s | URL=%s | 方法=POST",
                        response.status_code,
                        getattr(response, 'reason', ''),
                        run_url,
                    )
                    logger.error("请求头: %s", masked_headers)
                    logger.error("请求体: %s", safe_request_data)
                    logger.error("响应头: %s", dict(response.headers))
                    try:
                        logger.error("响应JSON: %s", response.json())
                    except Exception:
                        logger.error("响应文本: %s", response.text[:2000])
                except Exception as log_e:
                    logger.error("记录错误详情时异常: %s", log_e)
                return RunResult(success=False, answer=None, token=None)
                
        except requests.exceptions.ConnectionError:
            logger.error("无法连接到服务器")
            return RunResult(success=False, answer=None, token=None)
        except requests.exceptions.Timeout:
            logger.error("API请求超时")
            return RunResult(success=False, answer=None, token=None)
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求异常: {e}")
            return RunResult(success=False, answer=None, token=None)
        except json.JSONDecodeError:
            logger.error("服务器响应格式错误")
            return RunResult(success=False, answer=None, token=None)
        except Exception as e:
            logger.error(f"API调用过程中发生未知错误: {e}")
            return RunResult(success=False, answer=None, token=None)
    
    def is_authenticated(self) -> bool:
        """
        检查是否已认证
        
        Returns:
            bool: 是否已获取有效token
        """
        return self.token is not None
    
    def logout(self) -> None:
        """
        退出登录，清除token
        """
        self.token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
        logger.info("已退出登录")
    
    def get_token(self) -> Optional[str]:
        """
        获取当前token
        
        Returns:
            str: 当前token，未登录时返回None
        """
        return self.token
    
    def set_token(self, token: str) -> None:
        """
        手动设置token
        
        Args:
            token (str): 要设置的token
        """
        self.token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
        logger.info("已手动设置token")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.session.close()
        
    def __repr__(self) -> str:
        """字符串表示"""
        status = "已认证" if self.is_authenticated() else "未认证"
        memory_count = len(self.memory_data)
        return f"AditorClient(base_url='{self.base_url}', status='{status}', memory_items={memory_count})"
    
    # ==================== 记忆管理功能 ====================
    
    def _load_memory(self) -> None:
        """
        从磁盘加载记忆数据
        """
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memory_data = data.get('memories', [])
                logger.info(f"已加载 {len(self.memory_data)} 条记忆")
            else:
                self.memory_data = []
                logger.info("记忆文件不存在，创建新的记忆存储")
        except Exception as e:
            logger.error(f"加载记忆失败: {e}")
            self.memory_data = []
    
    def _save_memory(self) -> bool:
        """
        保存记忆数据到磁盘
        Returns:
            bool: 保存是否成功
        """
        try:
            from datetime import datetime
            # 创建记忆数据结构
            memory_structure = {
                'version': '1.0',
                'created_at': datetime.now().isoformat(),
                'total_count': len(self.memory_data),
                'memories': self.memory_data
            }
            
            # 确保目录存在
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存到文件
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_structure, f, ensure_ascii=False, indent=2)
            
            logger.info(f"已保存 {len(self.memory_data)} 条记忆到 {self.memory_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存记忆失败: {e}")
            return False
    
    def write_memory(self, content: str) -> bool:
        """
        写入记忆
        
        Args:
            content (str): 要记忆的内容
            
        Returns:
            bool: 写入是否成功
            
        Example:
            >>> client = AditorClient()
            >>> client.write_memory("学习了Python编程")
            >>> client.write_memory("要复习数据结构")
        """
        if not isinstance(content, str):
            raise ValueError("记忆内容必须是字符串")
        
        if not content.strip():
            logger.warning("尝试写入空的记忆内容")
            return False
        
        try:
            # 直接添加内容，不加时间戳
            memory_entry = content.strip()
            
            # 添加到记忆列表
            self.memory_data.append(memory_entry)
            
            # 持久化保存
            success = self._save_memory()
            
            if success:
                logger.info(f"已写入记忆: {content[:50]}{'...' if len(content) > 50 else ''}")
                return True
            else:
                # 如果保存失败，从内存中移除
                self.memory_data.pop()
                return False
                
        except Exception as e:
            logger.error(f"写入记忆失败: {e}")
            return False
    
    def get_all_memories(self) -> str:
        """
        获取全部记忆，以换行符拼接
        
        Returns:
            str: 所有记忆内容，用换行符分隔
            
        Example:
            >>> client = AditorClient()
            >>> memories = client.get_all_memories()
            >>> print(memories)
        """
        if not self.memory_data:
            return ""
        
        return "\n".join(self.memory_data)
    
    def get_memories_list(self) -> List[str]:
        """
        获取全部记忆列表
        
        Returns:
            List[str]: 记忆内容列表
        """
        return self.memory_data.copy()
    
    def get_memory_count(self) -> int:
        """
        获取记忆条数
        
        Returns:
            int: 记忆总数
        """
        return len(self.memory_data)
    
    def clear_memories(self) -> bool:
        """
        清空所有记忆
        
        Returns:
            bool: 清空是否成功
        """
        try:
            self.memory_data.clear()
            success = self._save_memory()
            
            if success:
                logger.info("已清空所有记忆")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"清空记忆失败: {e}")
            return False
    
    def export_memories(self, export_file: str) -> bool:
        """
        导出记忆到文件
        
        Args:
            export_file (str): 导出文件路径
            
        Returns:
            bool: 导出是否成功
        """
        try:
            from datetime import datetime
            
            export_path = Path(export_file)
            
            # 确保目录存在
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 导出为文本文件
            with open(export_path, 'w', encoding='utf-8') as f:
                for i, memory in enumerate(self.memory_data, 1):
                    f.write(f"{memory}\n")
            
            logger.info(f"已导出 {len(self.memory_data)} 条记忆到 {export_file}")
            return True
            
        except Exception as e:
            logger.error(f"导出记忆失败: {e}")
            return False
