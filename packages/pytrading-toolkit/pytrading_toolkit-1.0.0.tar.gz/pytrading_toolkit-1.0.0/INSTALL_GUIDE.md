# 📦 PyTrading Toolkit 패키지 설치 가이드

이 가이드는 `pytrading-toolkit` 패키지를 설치하고 사용하는 방법을 단계별로 설명합니다.

## 🎯 **개요**

`pytrading-toolkit`은 암호화폐 트레이딩 봇 개발을 위한 **오픈소스 공통 모듈 패키지**입니다.

### 📋 패키지 특징
- **오픈소스**: MIT 라이선스 하에 배포
- **범용성**: 다양한 암호화폐 거래 프로젝트에서 재사용 가능
- **독립성**: 다른 프로젝트와 독립적으로 사용 가능
- **공통 기능**: 업비트, 바이비트 등 거래소에서 공통으로 사용하는 기능 제공

### 🏗️ 프로젝트 내 위치
```
crypto-auto-trader/
├── packages/
│   └── pytrading-toolkit/  # ← 현재 위치 (오픈소스 패키지)
└── trader/                 # 개인 전용 거래 시스템 (이 패키지 사용)
```

## 🚀 **설치 방법**

### **방법 1: 개발 모드 설치 (권장 - 코드 수정 시 즉시 반영)**

```bash
# 1. trader 디렉토리로 이동 (패키지를 사용할 프로젝트)
cd trader

# 2. 설치 스크립트 실행 권한 부여
chmod +x install_pytrading_toolkit.sh

# 3. 설치 스크립트 실행 (../packages/pytrading-toolkit을 editable 모드로 설치)
./install_pytrading_toolkit.sh
```

**장점**: 코드를 수정하면 즉시 반영됨 (재설치 불필요)
**단점**: 패키지가 개발 모드로 설치됨

---

### **방법 2: 일반 설치 (안정적인 운영용)**

```bash
# 1. pytrading-toolkit 패키지 디렉토리로 이동
cd packages/pytrading-toolkit

# 2. 패키지 설치
pip install .

# 3. 설치 확인
python -c "import pytrading_toolkit; print('설치 성공!')"
```

**장점**: 안정적인 운영 환경
**단점**: 코드 수정 시 재설치 필요

---

### **방법 3: 의존성과 함께 설치**

```bash
# 1. pytrading-toolkit 패키지 디렉토리로 이동
cd packages/pytrading-toolkit

# 2. 의존성 먼저 설치
pip install -r requirements.txt

# 3. 패키지 설치
pip install .

# 4. 설치 확인
pip show pytrading-toolkit
```

## 🔧 **상세 설치 과정 (방법 1 권장)**

### **1단계: 디렉토리 확인**
```bash
# 프로젝트 루트에서
ls -la
# packages/pytrading-toolkit 디렉토리가 있어야 함

cd trader
ls -la
# install_pytrading_toolkit.sh 파일이 있어야 함
# requirements.txt 파일이 있어야 함 (pytrading-toolkit 의존성 포함)
```

### **2단계: 가상환경 확인**
```bash
# 가상환경이 활성화되어 있는지 확인
echo $VIRTUAL_ENV

# 가상환경이 없다면 활성화 (trader 디렉토리에서)
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate     # Windows
```

### **3단계: 설치 실행**
```bash
# 실행 권한 부여
chmod +x install_pytrading_toolkit.sh

# 설치 실행
./install_pytrading_toolkit.sh
```

### **4단계: 설치 확인**
```bash
# Python에서 import 테스트
python -c "
import pytrading_toolkit
print('✅ 패키지 import 성공!')
print(f'버전: {pytrading_toolkit.get_version()}')
print(f'정보: {pytrading_toolkit.get_info()}')
"
```

## 🚨 **문제 해결**

### **문제 1: "ModuleNotFoundError: No module named 'pytrading_toolkit'"**
```bash
# 해결 방법: 재설치
cd trader
./install_pytrading_toolkit.sh
```

### **문제 2: "Permission denied"**
```bash
# 해결 방법: 실행 권한 부여
chmod +x install_pytrading_toolkit.sh
```

### **문제 3: 가상환경 문제**
```bash
# 가상환경 재생성 (trader 디렉토리에서)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# pip install --upgrade pip
```

### **문제 4: 의존성 충돌**
```bash
# 기존 설치 제거 후 재설치
pip uninstall pytrading-toolkit -y
cd trader
./install_pytrading_toolkit.sh
```

## 📚 **사용법 테스트**

### **기본 import 테스트**
```python
# test_import.py 파일 생성
from pytrading_toolkit import (
    BaseConfigLoader,
    UpbitConfigLoader,
    TelegramNotifier,
    setup_logger
)

print("✅ 모든 모듈 import 성공!")

# 설정 로더 테스트
try:
    upbit_config = UpbitConfigLoader()
    print("✅ UpbitConfigLoader 생성 성공!")
except Exception as e:
    print(f"❌ 설정 로더 생성 실패: {e}")
```

### **실행**
```bash
python test_import.py
```

## 🎯 **권장 설치 순서**

1. **개발 단계**: 방법 1 (개발 모드)
2. **테스트 단계**: 방법 1 (개발 모드)
3. **운영 단계**: 방법 2 (일반 설치)

## 📁 **패키지 구조**

```
pytrading-toolkit/
├── config/                 # 설정 관리
│   ├── base.py            # 기본 설정 클래스
│   └── exchange/          # 거래소별 설정
│       ├── upbit.py       # 업비트 설정
│       └── bybit.py       # 바이비트 설정
├── indicators/             # 기술지표 계산
├── notifications/          # 알림 시스템
├── logging/                # 로깅 시스템
├── health/                 # 헬스체크 및 모니터링
└── utils/                  # 유틸리티 함수들
```

## 🔄 **기존 코드에서 사용법**

### **기존 방식 (권장하지 않음)**
```python
import sys
sys.path.insert(0, '...')
from pytrading_toolkit import ...
```

### **새로운 방식 (권장)**
```python
from pytrading_toolkit import (
    UpbitConfigLoader,
    TelegramNotifier,
    setup_logger
)

# 업비트 설정 사용
config_loader = UpbitConfigLoader()
config = config_loader.load_config()

# 텔레그램 알림 사용
notifier = TelegramNotifier(bot_token, chat_id)
notifier.send_message("테스트 메시지")
```

## 📝 **주의사항**

1. **가상환경 사용**: 프로젝트별로 가상환경을 사용하여 의존성 충돌 방지
2. **설치 순서**: 의존성 → 패키지 순서로 설치
3. **권한 문제**: Linux/Mac에서는 `chmod +x` 명령으로 실행 권한 부여
4. **경로 확인**: 올바른 디렉토리에서 설치 명령 실행

## 🆘 **도움말**

설치 과정에서 문제가 발생하면:

1. 가상환경이 활성화되어 있는지 확인
2. Python 버전 확인 (`python --version`)
3. pip 버전 확인 (`pip --version`)
4. 에러 메시지를 정확히 확인하고 위의 문제 해결 섹션 참조

---

**마지막 업데이트**: 2024년 12월
**작성자**: Crypto Auto Trader Team
