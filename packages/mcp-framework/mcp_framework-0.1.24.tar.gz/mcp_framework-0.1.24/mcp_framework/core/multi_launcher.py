#!/usr/bin/env python3
"""
MCP 框架多传输启动器
支持同时启动HTTP和stdio等多种传输方式
"""

import asyncio
import logging
import sys
from typing import Optional, Dict, Any, List
from .base import BaseMCPServer
from .config import ServerConfig
from .transport import (
    MCPTransportManager, 
    TransportType, 
    create_http_only_manager,
    create_stdio_only_manager,
    create_dual_manager
)
from .utils import (
    parse_command_line_args,
    create_server_config_from_args,
    setup_logging_from_args,
    check_dependencies,
    create_port_based_config_manager
)

logger = logging.getLogger(__name__)


async def run_multi_transport_server(
    server_instance: BaseMCPServer,
    transports: List[str] = ["http"],
    server_name: str = "MCP Server",
    default_port: int = 8080,
    default_host: str = "localhost",
    required_dependencies: Optional[list] = None,
    custom_args: Optional[Dict[str, Any]] = None
) -> None:
    """
    多传输方式服务器启动函数
    
    Args:
        server_instance: MCP 服务器实例
        transports: 传输方式列表，可选: ["http", "stdio", "both"]
        server_name: 服务器名称
        default_port: 默认端口号（仅HTTP需要）
        default_host: 默认主机（仅HTTP需要）
        required_dependencies: 必需的依赖包列表
        custom_args: 自定义参数字典
    """
    try:
        # 解析传输方式
        transport_types = _parse_transports(transports)
        
        # 确定输出流（stdio模式下使用stderr，避免干扰JSON-RPC通信）
        output_stream = sys.stderr if TransportType.STDIO in transport_types and len(transport_types) == 1 else sys.stdout
        
        # 检查依赖
        if required_dependencies:
            for dep in required_dependencies:
                try:
                    __import__(dep)
                except ImportError:
                    print(f"❌ 缺少依赖包: {dep}", file=output_stream)
                    print(f"请运行: pip install {dep}", file=output_stream)
                    sys.exit(1)
        
        # 通用依赖检查
        if not check_dependencies():
            sys.exit(1)
        
        # 初始化服务器
        print(f"🔧 初始化 {server_name}...", file=output_stream)
        try:
            await server_instance.startup()
            print("✅ 服务器初始化成功", file=output_stream)
        except Exception as e:
            print(f"⚠️  初始化警告: {e}", file=output_stream)

        # 创建传输管理器
        transport_manager = MCPTransportManager(server_instance)
        config = None
        config_manager = None
        
        # 配置HTTP传输（如果需要）
        if TransportType.HTTP in transport_types:
            # 解析命令行参数
            args = parse_command_line_args(
                server_name=server_name,
                default_port=default_port,
                default_host=default_host
            )
            
            # 应用自定义参数
            if custom_args:
                args.update(custom_args)

            # 设置日志
            setup_logging_from_args(args)

            # 创建服务器配置
            config = create_server_config_from_args(args)
            
            # 创建配置管理器
            config_manager = create_port_based_config_manager(server_name, config.port)
            server_instance.server_config_manager = config_manager
            
            # 添加HTTP传输
            transport_manager.add_http_transport(config, config_manager)
            
        # 配置stdio传输（如果需要）
        if TransportType.STDIO in transport_types:
            transport_manager.add_stdio_transport()

        # 启动传输
        print(f"🚀 启动 {server_name} 传输层...", file=output_stream)
        active_transports = await transport_manager.start_all()
        
        # 显示启动信息
        _print_startup_info(server_instance, server_name, transport_types, config, output_stream)
        
        # 保持服务器运行
        try:
            if TransportType.STDIO in transport_types and len(transport_types) == 1:
                # 纯stdio模式，等待stdio服务器完成
                while transport_manager.is_transport_active(TransportType.STDIO):
                    await asyncio.sleep(0.1)
            else:
                # HTTP模式或混合模式，等待中断信号
                while True:
                    await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 正在停止服务器...", file=output_stream)
            
        # 停止所有传输
        await transport_manager.stop_all()
        
        # 关闭MCP服务器
        try:
            await server_instance.shutdown()
        except Exception as e:
            logger.warning(f"关闭MCP服务器时出现警告: {e}")
            
        print("✅ 服务器已安全关闭", file=output_stream)

    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        print(f"❌ 服务器启动失败: {e}", file=output_stream)
        # 确保在启动失败时也清理资源
        try:
            if 'server_instance' in locals():
                await server_instance.shutdown()
        except Exception as cleanup_error:
            logger.warning(f"清理资源时出现警告: {cleanup_error}")
        sys.exit(1)


def run_multi_transport_server_main(
    server_instance: BaseMCPServer,
    transports: List[str] = ["http"],
    server_name: str = "MCP Server",
    default_port: int = 8080,
    default_host: str = "localhost",
    required_dependencies: Optional[list] = None,
    custom_args: Optional[Dict[str, Any]] = None
) -> None:
    """
    同步版本的多传输服务器启动函数
    
    这是推荐的主函数入口点
    """
    # 解析传输方式，确定输出流
    transport_types = _parse_transports(transports)
    output_stream = sys.stderr if TransportType.STDIO in transport_types and len(transport_types) == 1 else sys.stdout
    
    try:
        asyncio.run(run_multi_transport_server(
            server_instance=server_instance,
            transports=transports,
            server_name=server_name,
            default_port=default_port,
            default_host=default_host,
            required_dependencies=required_dependencies,
            custom_args=custom_args
        ))
    except KeyboardInterrupt:
        print("\n👋 再见!", file=output_stream)
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        print(f"❌ 程序异常退出: {e}", file=output_stream)
        sys.exit(1)


# 便利函数
def run_http_server_main(
    server_instance: BaseMCPServer,
    server_name: str = "MCP Server",
    default_port: int = 8080,
    default_host: str = "localhost",
    required_dependencies: Optional[list] = None,
    custom_args: Optional[Dict[str, Any]] = None
) -> None:
    """仅HTTP服务器启动"""
    run_multi_transport_server_main(
        server_instance=server_instance,
        transports=["http"],
        server_name=server_name,
        default_port=default_port,
        default_host=default_host,
        required_dependencies=required_dependencies,
        custom_args=custom_args
    )


def run_stdio_server_main(
    server_instance: BaseMCPServer,
    server_name: str = "MCP Server",
    required_dependencies: Optional[list] = None
) -> None:
    """仅stdio服务器启动"""
    run_multi_transport_server_main(
        server_instance=server_instance,
        transports=["stdio"],
        server_name=server_name,
        required_dependencies=required_dependencies
    )


def run_dual_server_main(
    server_instance: BaseMCPServer,
    server_name: str = "MCP Server",
    default_port: int = 8080,
    default_host: str = "localhost",
    required_dependencies: Optional[list] = None,
    custom_args: Optional[Dict[str, Any]] = None
) -> None:
    """HTTP+stdio双传输服务器启动"""
    run_multi_transport_server_main(
        server_instance=server_instance,
        transports=["both"],
        server_name=server_name,
        default_port=default_port,
        default_host=default_host,
        required_dependencies=required_dependencies,
        custom_args=custom_args
    )


def _parse_transports(transports: List[str]) -> List[TransportType]:
    """解析传输方式列表"""
    transport_types = []
    
    for transport in transports:
        if transport.lower() == "http":
            transport_types.append(TransportType.HTTP)
        elif transport.lower() == "stdio":
            transport_types.append(TransportType.STDIO)
        elif transport.lower() == "both":
            transport_types.extend([TransportType.HTTP, TransportType.STDIO])
        else:
            raise ValueError(f"不支持的传输方式: {transport}")
    
    # 去重
    return list(set(transport_types))


def _print_startup_info(
    server_instance: BaseMCPServer, 
    server_name: str, 
    transport_types: List[TransportType], 
    config: Optional[ServerConfig],
    output_stream=sys.stdout
):
    """打印启动信息"""
    print(f"🎯 {server_name} 启动完成!", file=output_stream)
    print(f"🛠️  服务器版本: {server_instance.name} v{server_instance.version}", file=output_stream)
    print(f"🔧 已注册工具: {len(server_instance.tools)} 个", file=output_stream)
    print(f"📁 已注册资源: {len(server_instance.resources)} 个", file=output_stream)
    
    print(f"\n📡 活跃传输:", file=output_stream)
    for transport_type in transport_types:
        if transport_type == TransportType.HTTP and config:
            print(f"  • HTTP: http://{config.host}:{config.port}", file=output_stream)
            print(f"    - 设置页面: http://{config.host}:{config.port}/setup", file=output_stream)
            print(f"    - 测试页面: http://{config.host}:{config.port}/test", file=output_stream)
            print(f"    - 配置页面: http://{config.host}:{config.port}/config", file=output_stream)
            print(f"    - 健康检查: http://{config.host}:{config.port}/health", file=output_stream)
        elif transport_type == TransportType.STDIO:
            print(f"  • stdio: 标准输入输出", file=output_stream)
            print(f"    - 协议: JSON-RPC 2.0", file=output_stream)
            print(f"    - 格式: 每行一个JSON请求/响应", file=output_stream)
    
    if TransportType.STDIO not in transport_types:
        print("\n按 Ctrl+C 停止服务器", file=output_stream)
    else:
        print("\n发送EOF或按 Ctrl+C 停止服务器", file=output_stream)