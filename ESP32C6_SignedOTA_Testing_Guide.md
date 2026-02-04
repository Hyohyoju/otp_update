# ESP32-C6 Signed OTA 구동 및 테스팅 가이드

이 문서는 **ESP32-C6** 보드에서 보안 서명된 OTA(Signed OTA)를 설정하고 테스트하는 방법을 단계별로 설명합니다.

## 1. 사전 준비 (Prerequisites)

### 1.1 하드웨어 및 소프트웨어
*   **ESP32-C6 보드**: PC와 USB로 연결되어 있어야 합니다.
*   **Arduino IDE**: 최신 버전 권장.
*   **ESP32 Board Manager**: 버전 **3.0.0 이상** 필수. (Arduino IDE -> Tools -> Board -> Boards Manager에서 'esp32' 검색 및 업데이트)
*   **Python**: 3.x 버전이 설치되어 있어야 합니다. (터미널에서 `python --version` 확인)

### 1.2 필수 도구 위치 파악
ESP32 패키지에 포함된 서명 도구(`bin_signing.py`)와 업로드 도구(`espota.py`)의 위치를 미리 확인해두세요. Windows의 경우 보통 아래 경로에 있습니다:
*   `C:\Users\<사용자명>\AppData\Local\Arduino15\packages\esp32\hardware\esp32\<버전>\tools`

## 2. 보안 키 생성 (Key Generation)

1.  **Python 설치**: [Python 공식 홈페이지](https://www.python.org/downloads/)에서 Python 3.x를 다운로드하여 설치합니다. **"Add Python to PATH"** 옵션을 반드시 체크하세요!
2.  **필수 라이브러리 설치**: 터미널(CMD/PowerShell)에서 다음 명령어를 실행합니다:
    ```powershell
    pip install cryptography
    ```
3.  **키 생성 스크립트 실행**:
    Arduino ESP32 3.x 버전에서 `bin_signing.py`가 누락된 경우가 있어, 프로젝트 폴더에 `generate_keys.py`를 생성해 두었습니다. 아래 명령어를 실행하세요:

    ```powershell
    # 현재 폴더(SignedOTA)에서 실행
    python generate_keys.py
    ```
    이 스크립트는 자동으로 `private_key.pem`과 `public_key.h`를 생성합니다.

## 3. 코드 설정 및 최초 업로드

### 3.1 코드 설정
`SignedOTA.ino` 파일을 열고 다음 항목을 수정합니다:
1.  **WiFi 설정**: `ssid`와 `password`를 본인의 환경에 맞게 입력합니다.
2.  **보드 설정**:
    *   Board: `ESP32-C6 Dev Module` (또는 사용하는 보드)
    *   **Partition Scheme**: `Default 4MB with spiffs` 또는 OTA 영역이 있는 파티션 선택.
    *   **Port**: 연결된 COM 포트 선택.

### 3.2 최초 업로드 (USB)
1.  USB 케이블로 ESP32-C6를 연결합니다.
2.  Arduino IDE에서 **Upload** 버튼을 눌러 스케치를 업로드합니다.
3.  **Serial Monitor** (115200 baud)를 열어 부팅 로그를 확인합니다.
    *   "WiFi Connected!"
    *   "OTA Server Ready"
    *   "IP address: 192.168.x.x" (이 IP 주소를 메모해두세요!)

## 4. 서명된 펌웨어 생성 (Build & Sign)

이제 OTA로 업데이트할 **새로운 버전**의 펌웨어를 만들고 서명해 봅니다. 테스트를 위해 코드의 `setup()` 부분에 `Serial.println("OTA Update Successful! V2");` 같은 문구를 추가하여 변경사항을 만드세요.

1.  **컴파일 된 바이너리 추출**:
    *   Arduino IDE 메뉴 -> **Sketch** -> **Export Compiled Binary** 클릭.
    *   스케치 폴더 내 `build` 폴더에 `.bin` 파일이 생성됩니다. (보통 `SignedOTA.ino.bin`)


2.  **펌웨어 서명**:
    *   터미널에서 스케치 폴더(SignedOTA)로 이동합니다.
    *   `sign_firmware.py`를 사용하여 바이너리에 서명합니다:

```powershell
# 사용법: python sign_firmware.py <입력_바이너리> <개인키> <출력_파일>
# 경로를 본인 환경에 맞게 수정하세요. 보통 build 폴더 내에 있습니다.
python sign_firmware.py "build\esp32.esp32.esp32c6\SignedOTA.ino.bin" private_key.pem firmware_signed.bin
```

    *   `Success! Created firmware_signed.bin` 메시지가 나오면 성공입니다.




## 5. OTA 테스팅 (Cloud/HTTP OTA)

PC와 ESP32가 서로 다른 네트워크에 있어도 문제없는 **클라우드 다운로드** 방식입니다.

1.  **파일 클라우드 업로드**:
    *   PC에서 생성한 `firmware_signed.bin` 파일을 인터넷에 올리고 다운로드 링크를 얻어야 합니다.
    *   가장 간편한 `transfer.sh` 서비스를 터미널에서 이용해 봅시다:

    ```powershell
    # firmware_signed.bin 파일이 있는 폴더에서 실행
    curl --upload-file firmware_signed.bin https://transfer.sh/firmware_signed.bin
    ```

    *   실행하면 `https://transfer.sh/AbCdEf/firmware_signed.bin` 같은 **URL 주소**가 나옵니다. 이 주소를 복사하세요.

2.  **코드에 URL 입력 및 업로드**:
    *   `SignedOTA.ino` 파일의 `firmware_url` 변수에 위에서 복사한 **URL 주소**를 붙여넣습니다.
    *   **USB로 업로드**를 진행합니다.

3.  **결과 확인**:
    *   업로드가 끝나고 ESP32가 부팅되면 와이파이에 연결됩니다.
    *   5초 후 자동으로 해당 URL에서 파일을 다운로드받고 업데이트를 시작합니다.
    *   Serial Monitor에서 `Done!`, `Verified!` 메시지가 뜨고 재부팅되면 성공입니다.



## 6. 문제 해결 (Troubleshooting)

*   **COM 포트 인식 불가**: USB 케이블을 데이터 전용으로 교체하거나, 드라이버를 재설치해보세요. C6는 USB 모드(JTAG/Serial) 설정이 보드 메뉴에 있을 수 있습니다. `USB CDC On Boot`를 Enable로 설정해야 시리얼 모니터가 바로 보일 수 있습니다.
*   **업로드 실패 (Begin Failed)**: 파티션 스킴이 OTA를 지원하는지 확인하세요 (App 파티션 2개 필요).
*   **서명 검증 실패**: `private_key.pem`과 `public_key.h`가 한 쌍인지 확인하세요. 다른 키로 서명하면 절대 작동하지 않습니다.

---
**팁**: `task.json`을 사용해 VS Code 등에서 이 과정을 자동화 스크립트로 만들 수도 있습니다.
