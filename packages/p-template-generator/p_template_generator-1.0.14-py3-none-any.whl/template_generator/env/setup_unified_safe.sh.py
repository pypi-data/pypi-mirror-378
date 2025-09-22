#!/bin/bash
echo "=== 安全统一环境设置脚本 ==="

# 获取脚本所在目录
root_dir=$(cd $(dirname $0);pwd)
echo "脚本目录: $root_dir"

# 创建备份目录
backup_dir="/tmp/nvidia_setup_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"
echo "备份目录: $backup_dir"

# 检测NVIDIA GPU和驱动版本
has_nvidia=false
nvidia_version=""
cuda_version=""
if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi | grep -q "NVIDIA"; then
        has_nvidia=true
        nvidia_version=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits | head -1)
        echo "检测到NVIDIA GPU，驱动版本: $nvidia_version"
        
        # 检测CUDA版本
        if command -v nvcc &> /dev/null; then
            cuda_version=$(nvcc --version | grep "release" | sed 's/.*release \([0-9.]*\).*/\1/')
            echo "检测到CUDA版本: $cuda_version"
        fi
    fi
fi

# 检测显示服务器
has_display=false
if [ -n "$XDG_SESSION_TYPE" ] || [ -n "$DISPLAY" ]; then
    has_display=true
    echo "检测到显示服务器"
fi

# 检测EGL支持
has_egl=false
if [ -f "/usr/lib/x86_64-linux-gnu/libEGL.so" ] || [ -f "/usr/lib/libEGL.so" ]; then
    has_egl=true
    echo "检测到EGL支持"
fi

echo "=== 环境检测结果 ==="
echo "NVIDIA GPU: $has_nvidia"
echo "NVIDIA驱动版本: $nvidia_version"
echo "CUDA版本: $cuda_version"
echo "显示服务器: $has_display"
echo "EGL支持: $has_egl"

# 版本兼容性检查函数
check_cuda_compatibility() {
    local driver_version=$1
    local cuda_version=$2
    
    if [ -z "$driver_version" ] || [ -z "$cuda_version" ]; then
        echo "⚠️  无法检测版本信息，跳过兼容性检查"
        return 0
    fi
    
    # 提取主版本号
    local driver_major=$(echo $driver_version | cut -d. -f1)
    local cuda_major=$(echo $cuda_version | cut -d. -f1)
    
    # CUDA版本与驱动版本的兼容性检查
    case $cuda_major in
        12)
            if [ $driver_major -lt 525 ]; then
                echo "❌ CUDA 12.x 需要驱动版本 >= 525，当前驱动: $driver_version"
                return 1
            fi
            ;;
        11)
            if [ $driver_major -lt 450 ]; then
                echo "❌ CUDA 11.x 需要驱动版本 >= 450，当前驱动: $driver_version"
                return 1
            fi
            ;;
        10)
            if [ $driver_major -lt 410 ]; then
                echo "❌ CUDA 10.x 需要驱动版本 >= 410，当前驱动: $driver_version"
                return 1
            fi
            ;;
    esac
    
    echo "✅ CUDA $cuda_version 与驱动 $driver_version 兼容"
    return 0
}

# 备份现有配置文件
backup_configs() {
    echo "=== 备份现有配置 ==="
    
    # 备份EGL配置文件
    if [ -d "/usr/share/glvnd/egl_vendor.d/" ]; then
        cp -r /usr/share/glvnd/egl_vendor.d/ "$backup_dir/"
        echo "✓ EGL配置文件已备份"
    fi
    
    # 备份环境变量文件
    if [ -f "/etc/environment" ]; then
        cp /etc/environment "$backup_dir/environment.backup"
        echo "✓ 环境变量文件已备份"
    fi
    
    # 备份库文件链接
    if [ -L "/usr/lib/libskycore.so" ]; then
        cp -P /usr/lib/libskycore.so "$backup_dir/"
        echo "✓ libskycore.so链接已备份"
    fi
}

# 安全安装函数
safe_install() {
    local package=$1
    local description=$2
    
    echo "安装 $description: $package"
    if apt-get install "$package" -y; then
        echo "✅ $description 安装成功"
        return 0
    else
        echo "❌ $description 安装失败"
        return 1
    fi
}

# 基础环境设置
echo "=== 设置基础环境 ==="
apt-get update
safe_install "libc++1" "C++标准库"

# 安装基础OpenGL库（所有环境都需要）
echo "=== 安装基础OpenGL库 ==="
safe_install "libgles2-mesa-dev mesa-utils libgl1-mesa-dev mesa-common-dev libglu1-mesa-dev" "Mesa OpenGL库"
safe_install "libegl1 libegl1-mesa-dev" "EGL库"
safe_install "libglvnd-dev libglvnd0" "GLVND库"

# 安装编解码器
echo "=== 安装编解码器 ==="
safe_install "libx264-dev libbz2-dev" "编解码器库"

# 安装虚拟显示支持（headless环境需要）
echo "=== 安装虚拟显示支持 ==="
safe_install "xvfb x11-utils" "虚拟显示支持"

# 根据检测结果安装特定组件
if [ "$has_nvidia" = true ]; then
    echo "=== 安装NVIDIA硬件加速组件 ==="
    
    # 版本兼容性检查
    if ! check_cuda_compatibility "$nvidia_version" "$cuda_version"; then
        echo "⚠️  检测到版本不兼容，建议手动安装匹配的CUDA版本"
        echo "是否继续安装其他组件？(y/N)"
        read -r continue_install
        if [ "$continue_install" != "y" ] && [ "$continue_install" != "Y" ]; then
            echo "安装已取消"
            exit 1
        fi
    fi
    
    # 备份现有配置
    backup_configs
    
    # 安全安装NVIDIA组件
    echo "安装NVIDIA EGL支持库..."
    if ! safe_install "libnvidia-egl-wayland1 libnvidia-egl-gbm1" "NVIDIA EGL库"; then
        echo "⚠️  NVIDIA EGL库安装失败，可能版本不匹配"
    fi
    
    # 检查是否需要安装CUDA Toolkit
    if [ -z "$cuda_version" ]; then
        echo "未检测到CUDA，是否安装CUDA Toolkit？(y/N)"
        read -r install_cuda
        if [ "$install_cuda" = "y" ] || [ "$install_cuda" = "Y" ]; then
            echo "⚠️  安装CUDA Toolkit可能影响现有驱动，建议手动安装匹配版本"
            safe_install "nvidia-cuda-toolkit" "NVIDIA CUDA Toolkit"
        fi
    else
        echo "✅ 已检测到CUDA $cuda_version，跳过CUDA Toolkit安装"
    fi
    
    # 安装OSMesa（离屏渲染）
    safe_install "libosmesa6-dev" "OSMesa库"
    
    echo "=== 设置NVIDIA EGL环境变量 ==="
    # 检查环境变量是否已存在
    if ! grep -q "__EGL_VENDOR_LIBRARY_FILENAMES" /etc/environment; then
        echo "export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json" >> /etc/environment
    fi
    if ! grep -q "__GL_THREADED_OPTIMIZATIONS" /etc/environment; then
        echo "export __GL_THREADED_OPTIMIZATIONS=1" >> /etc/environment
    fi
    if ! grep -q "__GL_SYNC_TO_VBLANK" /etc/environment; then
        echo "export __GL_SYNC_TO_VBLANK=0" >> /etc/environment
    fi
    if ! grep -q "CUDA_VISIBLE_DEVICES" /etc/environment; then
        echo "export CUDA_VISIBLE_DEVICES=0" >> /etc/environment
    fi
    
    # 设置NVIDIA性能优化
    if ! grep -q "__GL_SHADER_DISK_CACHE" /etc/environment; then
        echo "export __GL_SHADER_DISK_CACHE=1" >> /etc/environment
    fi
    if ! grep -q "__GL_SHADER_DISK_CACHE_PATH" /etc/environment; then
        echo "export __GL_SHADER_DISK_CACHE_PATH=/tmp/nvidia_shader_cache" >> /etc/environment
    fi
    
    # 创建NVIDIA EGL配置文件（仅在不存在时创建）
    mkdir -p /usr/share/glvnd/egl_vendor.d/
    if [ ! -f "/usr/share/glvnd/egl_vendor.d/10_nvidia.json" ]; then
        cat > /usr/share/glvnd/egl_vendor.d/10_nvidia.json << 'EOF'
{
    "file_format_version" : "1.0.0",
    "ICD" : {
        "library_path" : "/usr/lib/x86_64-linux-gnu/libEGL_nvidia.so.0"
    }
}
EOF
        echo "✓ 创建NVIDIA EGL配置文件"
    else
        echo "✓ NVIDIA EGL配置文件已存在"
    fi
    
    # 创建NVIDIA OpenGL配置文件（仅在不存在时创建）
    if [ ! -f "/usr/share/glvnd/egl_vendor.d/10_nvidia_gl.json" ]; then
        cat > /usr/share/glvnd/egl_vendor.d/10_nvidia_gl.json << 'EOF'
{
    "file_format_version" : "1.0.0",
    "ICD" : {
        "library_path" : "libGL_nvidia.so.0"
    }
}
EOF
        echo "✓ 创建NVIDIA OpenGL配置文件"
    else
        echo "✓ NVIDIA OpenGL配置文件已存在"
    fi
        
    echo "NVIDIA硬件加速组件安装完成"
else
    echo "=== 安装Mesa软件渲染组件 ==="
    
    # 备份现有配置
    backup_configs
    
    # 安装OSMesa（离屏渲染）
    safe_install "libosmesa6-dev" "OSMesa库"
    
    echo "=== 设置Mesa环境变量 ==="
    # 检查环境变量是否已存在
    if ! grep -q "MESA_GL_VERSION_OVERRIDE" /etc/environment; then
        echo "export MESA_GL_VERSION_OVERRIDE=3.3" >> /etc/environment
    fi
    if ! grep -q "MESA_GLSL_VERSION_OVERRIDE" /etc/environment; then
        echo "export MESA_GLSL_VERSION_OVERRIDE=330" >> /etc/environment
    fi
    if ! grep -q "LIBGL_ALWAYS_SOFTWARE" /etc/environment; then
        echo "export LIBGL_ALWAYS_SOFTWARE=1" >> /etc/environment
    fi
    if ! grep -q "GALLIUM_DRIVER" /etc/environment; then
        echo "export GALLIUM_DRIVER=llvmpipe" >> /etc/environment
    fi
    if ! grep -q "EGL_PLATFORM" /etc/environment; then
        echo "export EGL_PLATFORM=x11" >> /etc/environment
    fi
    if ! grep -q "MESA_GLSL_CACHE_DISABLE" /etc/environment; then
        echo "export MESA_GLSL_CACHE_DISABLE=1" >> /etc/environment
    fi
    
    # 创建Mesa EGL配置文件（仅在不存在时创建）
    mkdir -p /usr/share/glvnd/egl_vendor.d/
    if [ ! -f "/usr/share/glvnd/egl_vendor.d/50_mesa.json" ]; then
        cat > /usr/share/glvnd/egl_vendor.d/50_mesa.json << 'EOF'
{
    "file_format_version" : "1.0.0",
    "ICD" : {
        "library_path" : "libEGL_mesa.so.0"
    }
}
EOF
        echo "✓ 创建Mesa EGL配置文件"
    else
        echo "✓ Mesa EGL配置文件已存在"
    fi
    
    # 确保EGL库链接正确
    if [ -f "/usr/lib/x86_64-linux-gnu/libEGL_mesa.so.0" ]; then
        if [ ! -L "/usr/lib/libEGL.so.1" ]; then
            ln -sf /usr/lib/x86_64-linux-gnu/libEGL_mesa.so.0 /usr/lib/libEGL.so.1
            echo "✓ 创建EGL库链接"
        else
            echo "✓ EGL库链接已存在"
        fi
    fi
    
    echo "Mesa软件渲染组件安装完成"
fi

# 通用设置
echo "=== 通用设置 ==="

# 链接libskycore.so（安全版本）
if [ -f "$root_dir/../bin/skymedia/libskycore.so" ]; then
    if [ -L "/usr/lib/libskycore.so" ]; then
        rm -f /usr/lib/libskycore.so
    fi
    ln -s "$root_dir/../bin/skymedia/libskycore.so" /usr/lib/libskycore.so
    echo "✓ libskycore.so链接已创建"
else
    echo "⚠️  libskycore.so文件不存在: $root_dir/../bin/skymedia/libskycore.so"
fi

# 创建硬件加速检测脚本
cat > /usr/local/bin/check_acceleration << 'EOF'
#!/bin/bash
echo "=== 硬件加速检测 ==="

# 检查nvidia-smi
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA驱动: 已安装"
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
else
    echo "NVIDIA驱动: 未安装"
fi

# 检查CUDA
if command -v nvcc &> /dev/null; then
    echo "CUDA: 已安装"
    nvcc --version | grep "release"
else
    echo "CUDA: 未安装"
fi

# 检查EGL支持
if [ -f "/usr/lib/x86_64-linux-gnu/libEGL_nvidia.so.0" ]; then
    echo "NVIDIA EGL: 支持"
elif [ -f "/usr/lib/x86_64-linux-gnu/libEGL_mesa.so.0" ]; then
    echo "Mesa EGL: 支持"
else
    echo "EGL: 不支持"
fi

# 检查Mesa支持
if [ -f "/usr/lib/x86_64-linux-gnu/libGL.so" ]; then
    echo "Mesa GL: 支持"
else
    echo "Mesa GL: 不支持"
fi

echo "=== 检测完成 ==="
EOF

chmod +x /usr/local/bin/check_acceleration

echo "=== 验证安装 ==="
# 检查EGL库文件
if [ -f "/usr/lib/x86_64-linux-gnu/libEGL_mesa.so.0" ]; then
    echo "✓ Mesa EGL库已安装"
else
    echo "✗ Mesa EGL库未找到"
fi

if [ -f "/usr/lib/libEGL.so.1" ]; then
    echo "✓ EGL库链接已创建"
else
    echo "✗ EGL库链接未创建"
fi

if [ -f "/usr/lib/libskycore.so" ]; then
    echo "✓ libskycore.so链接已创建"
else
    echo "✗ libskycore.so链接未创建"
fi

echo "=== 安全统一环境设置完成 ==="
echo "备份文件位置: $backup_dir"
echo "可以使用 'check_acceleration' 命令检测硬件加速状态"

# 运行硬件加速检测
echo "=== 运行硬件加速检测 ==="
/usr/local/bin/check_acceleration

exit 0
