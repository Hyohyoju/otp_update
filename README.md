# 🌐 초간단 클라우드 OTA (Universal Template)

이 프로젝트는 **ESP32** 장치가 인터넷(클라우드)을 통해 펌웨어를 아주 쉽게 업데이트할 수 있도록 해주는 템플릿입니다. 복잡한 보안 설정 없이 바로 사용할 수 있습니다.

## ✨ 주요 기능
- **원격 업데이트**: USB 연결 없이 와이파이를 통해 펌웨어를 업데이트합니다.
- **초간편 사용**: 설정 파일 하나만 수정하면 바로 적용됩니다.

---

## 🚀 사용 순서 (Step-by-Step)

### 1단계: 준비물
- ESP32 보드
- VS Code & Arduino Extension (또는 Arduino IDE)

### 2단계: 설정 파일 수정 (`UserConfig.h`)
`UserConfig.h` 파일을 열어 자신의 환경에 맞게 수정합니다.

```cpp
// 1. 와이파이 설정
const char *ssid = "우리집와이파이";
const char *password = "비밀번호1234";

// 2. 펌웨어 다운로드 주소 (GitHub Raw 링크 등)
const char *firmware_url = "https://raw.githubusercontent.com/사용자명/저장소/main/update.bin";
```

### 3단계: 펌웨어 빌드
ESP32에 올릴 펌웨어 파일을 만듭니다.

1. VS Code에서 `Verify` 또는 `Build` 버튼을 눌러 컴파일합니다. (`.bin` 파일 생성)
   - 보통 `build/` 폴더 안에 `SignedOTA.bin` 같은 이름으로 생성됩니다.
2. 이 파일을 원하는 이름(예: `update.bin`)으로 바꿉니다.

### 4단계: 클라우드 업로드
생성된 `.bin` 파일을 `UserConfig.h`에 적어둔 주소(URL)에 올립니다.
- **GitHub 사용 시**: 파일을 커밋&푸시(Commit & Push)합니다.

### 5단계: 최초 업로드 및 테스트
처음에는 USB로 코드를 올려야 합니다.

1. VS Code에서 `Upload` 버튼을 눌러 ESP32에 코드를 업로드합니다.
2. 시리얼 모니터를 엽니다. (보드레이트: 115200)
3. ESP32가 부팅되며 와이파이에 연결하고, 설정된 URL에서 새 펌웨어가 있는지 확인합니다.
4. `execOTA()` 함수가 실행되면 자동으로 다운로드 및 업데이트가 진행됩니다.

---

## ⚠️ 주의사항
- **URL 주소**: GitHub 사용 시 원본 주소(Raw URL)를 사용해야 합니다. 주소에 `blob` 대신 `raw`가 들어가는지 확인하세요.
- **파티션 설정**: OTA를 위해서는 충분한 플래시 메모리 공간이 필요합니다. `Tools > Partition Scheme`에서 `Default 4MB with spiffs` 또는 `Minimal SPIFFS` 등을 선택하세요.

---

**문의사항**: 언제든지 댓글이나 이슈로 남겨주세요!
