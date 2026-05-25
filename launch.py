import os
import sys
import subprocess
import webbrowser

def main():
    print("=" * 60)
    print("        ?? ASSETCRAFT STUDIO 项目集 ??")
    print("=" * 60)
    print("1. PixelForge AI - 2D游戏素材生成工具（主项目）")
    print("2. AssetCraft Studio - AI设计资产管道（补充工具）")
    print("=" * 60)
    
    try:
        choice = input("请选择要启动的项目 (1 或 2): ").strip()
        
        if choice == "1":
            launch_pixelforge()
        elif choice == "2":
            launch_assetcraft()
        else:
            print("无效选择")
    except KeyboardInterrupt:
        print("\n已取消")
        sys.exit(0)

def launch_pixelforge():
    print("\n?? 启动 PixelForge AI...")
    os.chdir("pixelforge-ai")
    subprocess.run([sys.executable, "app.py"])

def launch_assetcraft():
    print("\n?? 启动 AssetCraft Studio...")
    os.chdir("assetcraft-studio")
    if os.path.exists("run.py"):
        subprocess.run([sys.executable, "run.py"])
    elif os.path.exists("app.py"):
        subprocess.run([sys.executable, "app.py"])
    else:
        print("找不到启动文件")

if __name__ == "__main__":
    main()
