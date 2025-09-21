import asyncio
import json
import subprocess
from mcp.server.fastmcp import FastMCP

# 创建FastMCP实例
mcp = FastMCP("docker_tool")

@mcp.tool()
async def pull_docker_image(image: str, tag: str = "latest"):
    """拉取Docker镜像的FastMCP工具"""
    print(f"正在拉取Docker镜像: {image}:{tag}")
    
    try:
        # 使用subprocess执行docker pull命令
        process = await asyncio.create_subprocess_exec(
            "docker", "pull", f"{image}:{tag}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # 检查命令执行结果
        if process.returncode == 0:
            print(f"成功拉取Docker镜像: {image}:{tag}")
            return {"success": True, "image": f"{image}:{tag}"}
        else:
            error_msg = f"拉取镜像失败: {stderr.decode('utf-8').strip()}"
            print(error_msg)
            return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"执行过程中发生错误: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}

@mcp.tool()
async def list_docker_images():
    """列出所有本地Docker镜像的FastMCP工具"""
    print("正在获取本地Docker镜像列表...")
    
    try:
        # 使用subprocess执行docker images命令
        process = await asyncio.create_subprocess_exec(
            "docker", "images", "--format", "{{json .}}", "--no-trunc",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # 检查命令执行结果
        if process.returncode == 0:
            # 解析结果
            images = []
            for line in stdout.decode('utf-8').strip().split('\n'):
                if line.strip():
                    try:
                        image_info = json.loads(line)
                        images.append(image_info)
                    except json.JSONDecodeError:
                        # 忽略无效的JSON行
                        continue
            
            print(f"成功获取{len(images)}个Docker镜像")
            return {"success": True, "images": images}
        else:
            error_msg = f"获取镜像列表失败: {stderr.decode('utf-8').strip()}"
            print(error_msg)
            return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"执行过程中发生错误: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}

@mcp.tool()
async def push_docker_image(image: str, tag: str = "latest", registry: str = "", username: str = "", password: str = ""):
    """推送Docker镜像到远程仓库的FastMCP工具"""
    # 构建完整的镜像名，包括registry（如果提供）
    full_image_name = f"{registry + '/' if registry else ''}{image}:{tag}"
    print(f"正在推送Docker镜像: {full_image_name}")
    
    try:
        # 如果提供了用户名和密码，先登录到仓库
        if username and password:
            print(f"正在登录到仓库: {registry or 'Docker Hub'}")
            login_process = await asyncio.create_subprocess_exec(
                "docker", "login", "--username", username, "--password-stdin", registry or "",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 将密码作为标准输入传递给login命令
            login_stdout, login_stderr = await login_process.communicate(input=password.encode())
            
            if login_process.returncode != 0:
                login_error = f"登录失败: {login_stderr.decode('utf-8').strip()}"
                print(login_error)
                return {"success": False, "error": login_error}
            print("登录成功")
        
        # 如果registry不为空，需要先标记镜像
        if registry:
            tag_process = await asyncio.create_subprocess_exec(
                "docker", "tag", f"{image}:{tag}", full_image_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            tag_stdout, tag_stderr = await tag_process.communicate()
            
            if tag_process.returncode != 0:
                tag_error = f"标记镜像失败: {tag_stderr.decode('utf-8').strip()}"
                print(tag_error)
                return {"success": False, "error": tag_error}
            print(f"成功标记镜像: {image}:{tag} -> {full_image_name}")
        
        # 执行推送命令
        push_process = await asyncio.create_subprocess_exec(
            "docker", "push", full_image_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        push_stdout, push_stderr = await push_process.communicate()
        
        # 检查命令执行结果
        if push_process.returncode == 0:
            print(f"成功推送Docker镜像: {full_image_name}")
            return {"success": True, "image": full_image_name}
        else:
            error_msg = f"推送镜像失败: {push_stderr.decode('utf-8').strip()}"
            print(error_msg)
            return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"执行过程中发生错误: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}

@mcp.tool()
async def rename_docker_image(old_image: str, old_tag: str = "latest", new_image: str = "", new_tag: str = "latest"):
    """重命名Docker镜像的FastMCP工具"""
    # 检查必要参数
    if not new_image:
        error_msg = "新镜像名不能为空"
        print(error_msg)
        return {"success": False, "error": error_msg}
    
    old_image_name = f"{old_image}:{old_tag}"
    new_image_name = f"{new_image}:{new_tag}"
    print(f"正在重命名Docker镜像: {old_image_name} -> {new_image_name}")
    
    try:
        # 使用subprocess执行docker tag命令来重命名镜像
        process = await asyncio.create_subprocess_exec(
            "docker", "tag", old_image_name, new_image_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # 检查命令执行结果
        if process.returncode == 0:
            print(f"成功重命名Docker镜像: {old_image_name} -> {new_image_name}")
            return {"success": True, "old_image": old_image_name, "new_image": new_image_name}
        else:
            error_msg = f"重命名镜像失败: {stderr.decode('utf-8').strip()}"
            print(error_msg)
            return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"执行过程中发生错误: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}
def main() -> None:
    mcp.run(transport="stdio")