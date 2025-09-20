## 🐍 pyhwpx: 파이썬-아래아한글 자동화 모듈

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/martiniifun/pyhwpx)

![introduction](https://raw.githubusercontent.com/martiniifun/pyhwpx/master/docs/assets/introduce.gif
)

**pyhwpx**는 `pywin32` 패키지를 활용하여 아래아한글(HWP) 문서를 자동화할 수 있는 Python 모듈입니다.  

현재 **`Hwp`** 클래스가 포함되어 있으며, **HwpAutomation에서 제공하는 모든 저수준 API 메서드의 사용법, 파라미터 및 예시 코드**를 추가하는 작업이 진행 중입니다.  

👉 한글 문서 업무 자동화에 많이 사용되는 **패턴들을 추가**하며, 보다 **실용적인 오픈소스 라이브러리**로 발전시킬 계획입니다.  
💡 유용한 **단축 메서드**도 지속적으로 업데이트할 예정입니다.

---

## **📌 주요 기능**
- **아래아한글 문서 조작**: 텍스트 삽입, 저장, 문서 편집 자동화
- **HwpAutomation API 래핑**: `pywin32`를 사용하여 Hwp 명령 실행
- **직관적인 인스턴스**: 기존 `win32com` 방식보다 쉬운 사용법 제공
- **단축 기능 추가 예정**: 문서 서식 설정, 표 삽입 등 기능 확장 가능  

---

## **🚀 설치 방법**
pyhwpx는 **PyPI(Python Package Index)**에 등록되어 있으며, 아래 명령에서 간편하게 설치할 수 있습니다.

```bash
pip install pyhwpx
```

> ⚠️ **주의:** pyhwpx는 **Windows** 환경에서 작동하며, **한/글이 설치되어 있어야** 합니다.  
> 💡 `pywin32`가 필요하며, `pip install pywin32`로 별도로 설치할 수도 있습니다.
> ✨ **Python 3.9 이상이 필요합니다.**

설치가 완료되면 Python에서 `import`하여 사용할 수 있습니다.

---

## **💡 사용법 예제**
```python
from pyhwpx import Hwp

hwp = Hwp()  # 보안모듈 자동 등록

# 텍스트 삽입
hwp.insert_text("Hello world!")

# win32com 방식으로도 실행 가능
pset = hwp.HParameterSet.HInsertText
pset.Text = "Hello world!"
hwp.HAction.Execute("InsertText", pset.HSet)

# 문서 저장
hwp.save_as("./helloworld.hwp")

# 한/글 종료
hwp.quit()
```

[CHANGELOG 보기](https://github.com/martiniifun/pyhwpx/blob/master/CHANGELOG.md)

---

## **📋 API Reference와 User Guide 는 [공식문서](https://martiniifun.github.io/pyhwpx/)에서 확인 가능합니다.**

