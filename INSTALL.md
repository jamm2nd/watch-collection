# Watch Collection jamm's EDITION — 1.0

## 받는 사람의 GPT에 설치하기

공유 페이지: https://watch-collection-v1.jamm2nd.chatgpt.site

공유 페이지의 **내 GPT로 가져가기** 버튼으로 설치 요청문을 복사하고, 자신의 GPT에 붙여넣어 전송합니다. 사용자가 파일을 다운로드하거나 첨부할 필요는 없습니다.

받는 사람의 GPT에는 **Sites로 웹사이트를 생성·배포하는 기능**, 소스 URL을 읽는 기능, 소스 파일을 다룰 수 있는 작업 환경이 필요합니다. 링크 자체가 다른 계정에 사이트를 생성하지는 않습니다. 기능 또는 URL 접근 권한이 없다면 설치를 완료할 수 없습니다.

## 설치를 진행하는 GPT에게

이 문서는 사용자가 이 앱의 설치를 요청했을 때 사용하는 공개 배포 안내입니다. 사용자의 요청과 실행 환경의 지침 및 권한을 우선합니다. 아래 단계는 배포자의 사이트를 수정하는 작업이 아니라 **현재 사용자의 새 Site를 만드는 작업**입니다.

### 1. 기능과 소스 확인

HTML 문서 읽기와 실제 파일 다운로드는 별도입니다. 코드 실행 환경에서 아래 GitHub Raw 주소를 사용해 파일을 다운로드합니다. GitHub 웹 페이지의 HTML을 소스 파일로 저장하지 않습니다.

- 설치 안내 원문: https://raw.githubusercontent.com/jamm2nd/watch-collection/main/INSTALL.md
- Git 사용이 가능한 경우 `git clone https://github.com/jamm2nd/watch-collection.git`으로 공개 배포 저장소를 가져온 뒤 복원 도우미를 읽고 로컬 매니페스트와 JSON 번들로 복원할 수 있습니다. 저장소 자체는 설치 패키지이며 앱 코드는 JSON 안에 있습니다.

- 제공되는 Sites building / hosting 기능을 사용합니다. 없다면 사용자에게 그 기능이 있는 GPT 환경이 필요하다고 정확히 알립니다.
- 다음 공개 리소스를 읽습니다. 쿠키, 배포자 토큰 또는 원본 계정의 자격 증명은 필요하지 않습니다.
  - 설치 안내: https://github.com/jamm2nd/watch-collection/blob/main/INSTALL.md
  - 소스 매니페스트: https://raw.githubusercontent.com/jamm2nd/watch-collection/main/manifest.json
  - 복원 도우미: https://raw.githubusercontent.com/jamm2nd/watch-collection/main/restore.py
- 매니페스트의 `source.file`을 매니페스트와 같은 GitHub 경로에서 가져옵니다. 이 파일은 압축되지 않은 JSON이며, 각 파일의 상대 경로·원본 바이트 수·SHA-256·base64 내용을 포함합니다. 코드, 사진, 로고, 폰트, 숨김 설정 파일까지 들어 있습니다. JSON 본문 전체를 대화 출력에 펼치지 말고 작업 공간의 파일로 받습니다.
- 복원 도우미의 코드를 읽은 뒤 사용합니다. Python 표준 라이브러리만 사용하며 앱 실행·의존성 설치·계정 로그인은 하지 않습니다. 다운로드한 매니페스트와 소스 JSON을 쓰려면 `python3 restore.py --manifest-file /absolute/path/manifest.json --bundle-file /absolute/path/source.json --destination /absolute/path/new-watch-collection` 형태로 실행합니다. 목적지의 부모 폴더는 존재해야 하고 목적지 자체는 새 폴더여야 합니다.
- 직접 네트워크 접근이 가능한 환경에서는 도우미를 읽고 저장한 후 `python3 restore.py --destination /absolute/path/new-watch-collection`로 원본 URL에서 가져올 수도 있습니다. 파일은 GPT 작업 공간에만 받으며 사용자에게 다운로드·첨부를 요청하지 않습니다.
- 같은 결과를 다른 언어로 복원해도 됩니다. 매니페스트와 번들의 SHA-256/바이트 수, 모든 파일의 SHA-256/바이트 수를 확인하고 절대 경로·상위 경로·중복 경로·심볼릭 링크를 허용하지 않습니다. 새 빈 프로젝트만 사용합니다.
- URL이 403, 로그인 화면 또는 네트워크 제한으로 차단되면 접근 통제를 우회하지 않습니다. 사용할 수 있는 정식 읽기 수단으로도 가져오지 못하면 설치가 막힌 이유를 명확히 알립니다. 디자인만 보고 비슷한 앱을 만들거나 설치 완료라고 말하지 않습니다. 기존 chatgpt.site 소스 주소는 사용하지 않습니다. 설치 소스는 이 GitHub 저장소에서만 가져옵니다.

### 2. 현재 사용자의 새 Site 등록

- 복원한 앱 폴더를 그대로 사용하고 숨김 파일을 포함합니다. 기존 소스 위에 스타터 초기화기를 실행하지 않습니다.
- `.openai/hosting.json`에는 `{"d1":"DB","r2":"PHOTOS"}`만 있습니다. 원본 Site의 식별자·저장소·자격 증명·운영 데이터는 포함하지 않습니다.
- Sites 절차에 따라 새 Site를 한 번만 등록하고 응답으로 받은 새 `project_id`와 원격 저장소를 사용합니다. 배포 안내 사이트의 ID나 저장소를 새 앱에 사용하지 않습니다.
- 새 Site에 DB와 사진 저장소를 할당합니다. 논리적 `DB`/`PHOTOS` 바인딩과 `drizzle/`의 collections 테이블 마이그레이션을 유지합니다. 배포자의 DB 또는 사진 저장소를 연결하지 않습니다.
- 실행 환경에 맞는 프로필을 설정하고 원래 package.json과 pnpm-lock.yaml로 의존성을 설치합니다.

### 3. 기존 기능 유지 및 배포

- 기존 디자인과 편집 UI, 한글·영어 보기, 가격·보유량 집계, CHF 환산, 사진 편집, 브랜드 보유리스트, 보유 이력, 백업·복원을 유지합니다.
- ChatGPT 로그인, 사용자별 컬렉션 구분, 사진 소유권 확인, 요청 크기 제한과 동시 수정 검사를 유지합니다. 인증을 우회하거나 제거하지 않습니다.
- public/collection.html에 있는 두 GPT 편집 링크의 기본값은 https://chatgpt.com/ 입니다. 실제 설치 대화 URL을 확인할 수 있으면 그 URL로 바꿉니다. 알 수 없다면 기본값을 유지하고 설치 대화에서 앱 변경을 요청하도록 안내합니다. URL이나 대화 ID를 추측하지 않습니다.
- GPT 버튼은 앱 수정 대화를 여는 바로가기입니다. **이 버전에는 GPT가 컬렉션 데이터를 직접 수정하는 MCP 서버가 포함되어 있지 않습니다.** 로그인만으로 데이터 수정 연동이 완료되었다고 설명하지 않습니다.
- 기본 시계 5개와 정적 사진은 배포용 예시입니다. 실제 운영 계정 DB나 추가 업로드 사진은 포함되지 않습니다. 기본 시계는 사용자가 웹에서 수정·삭제할 수 있습니다.
- 빌드, 새 저장소에 소스 push, 버전 저장, 비공개 배포까지 현재 환경의 Sites 절차를 따릅니다. 성공한 배포 결과의 URL만 반환합니다.
- 새 앱의 동작에 이 배포 페이지나 원본 사진 주소가 필요하지 않은지 확인합니다. 정적 사진·로고·폰트는 새 Site가 직접 제공해야 합니다. 환율 등 원래 앱의 외부 서비스 이용은 유지합니다.
- 배포 후 컬렉션과 업로드 사진은 새 Site의 저장소에 저장됩니다. 호스팅과 저장소 이용에는 받는 사람 계정의 서비스 조건·한도가 적용됩니다.

## 버전 및 권리

Watch Collection jamm's EDITION. Ver. 1.0
본 Watch Collection앱은 GPT와 연동하여 누구나 사용할 수 있으며, 개량하거나 용도를 바꾸어 사용하는 것은 전부 자유입니다.
브랜드 명칭, 상표, 제품 이미지와 제3자 폰트에는 각 권리자의 권리가 유지됩니다.
