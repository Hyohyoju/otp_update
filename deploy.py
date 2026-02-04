import os
import re
import sys
import shutil
import subprocess
import time
import glob

# ================= 설정 =================
CONFIG_FILE = "UserConfig.h"
BUILD_DIR = "build"  # 아두이노 빌드 폴더 (없으면 찾습니다)
OUTPUT_FILENAME = "update.bin"
# =======================================

def get_current_version():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'#define CURRENT_FIRMWARE_VERSION (\d+)', content)
    if match:
        return int(match.group(1))
    return None

def increment_version(current_ver):
    new_ver = current_ver + 1
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_content = re.sub(
        r'#define CURRENT_FIRMWARE_VERSION \d+',
        f'#define CURRENT_FIRMWARE_VERSION {new_ver}',
        content
    )
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    return new_ver

def find_newest_bin():
    # 1. build 폴더 확인
    search_patterns = [
        f"{BUILD_DIR}/**/*.bin",
        "*.bin", 
        "**/*.bin"
    ]
    
    candidates = []
    for pattern in search_patterns:
        candidates.extend(glob.glob(pattern, recursive=True))
    
    # OUTPUT_FILENAME은 제외
    candidates = [f for f in candidates if not f.endswith(OUTPUT_FILENAME)]
    
    if not candidates:
        return None
        
    # 가장 최근에 수정된 파일 찾기
    newest_file = max(candidates, key=os.path.getmtime)
    return newest_file

def git_push(version):
    print("\n☁️ GitHub에 업로드 중...")
    try:
        subprocess.run(["git", "add", OUTPUT_FILENAME], check=True)
        subprocess.run(["git", "add", CONFIG_FILE], check=True) # 버전 바뀐 설정파일도 함께
        subprocess.run(["git", "commit", "-m", f"Firmware Update v{version}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ 업로드 완료!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 오류 발생: {e}")
        print("Git이 설치되어 있고 저장소가 연결되어 있는지 확인해주세요.")

def main():
    print("🚀 OTA 배포 자동화를 시작합니다...")
    
    # 1. 버전 확인 및 증가
    cur_ver = get_current_version()
    if cur_ver is None:
        print(f"❌ 오류: {CONFIG_FILE}에서 버전을 찾을 수 없습니다.")
        return
        
    print(f"현재 버전: {cur_ver}")
    new_ver = increment_version(cur_ver)
    print(f"🔼 버전을 {new_ver}로 변경했습니다.")
    
    # 2. 컴파일 대기
    print("\n⏳ [행동 필요] 이제 VS Code/아두이노에서 '컴파일(Verify)' 버튼을 눌러주세요.")
    print("   컴파일이 완료되면 엔터(Enter) 키를 눌러주세요...")
    input()
    
    # 3. 파일 찾기
    print("🔎 빌드된 파일을 찾는 중...")
    bin_file = find_newest_bin()
    if not bin_file:
        print("❌ 오류: .bin 파일을 찾을 수 없습니다.")
        print("   빌드가 제대로 되었는지, build 폴더가 있는지 확인해주세요.")
        return
        
    print(f"   찾음: {bin_file}")
    
    # 4. 파일 이동 및 이름 변경
    try:
        shutil.copy2(bin_file, OUTPUT_FILENAME)
        print(f"📦 파일을 '{OUTPUT_FILENAME}'으로 복사했습니다.")
    except Exception as e:
        print(f"❌ 파일 복사 실패: {e}")
        return

    # 5. Git 푸시
    git_push(new_ver)
    
    print("\n🎉 모든 작업이 완료되었습니다!")
    print(f"   버전 {new_ver}이(가) 곧 배포됩니다.")

if __name__ == "__main__":
    main()
