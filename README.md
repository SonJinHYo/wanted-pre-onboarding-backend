# wanted-pre-onboarding-backend
 
안녕하세요 원티드 프리온보딩 백엔드 인턴십으로 지원한 손진효입니다.
<br/><br/><br/><br/><br/>

## 애플리케이션 실행 방법
django 컨테이너와 nginx 컨테이너를 실행합니다. nginx의 dockerfile과 설정 파일은 nginx 폴더에 있습니다.
클론 후 쉽게 어플리케이션을 실행할 수 있도록 staticfile, .env 파일을 모두 업로드 해두었습니다.

### git clone 후 로컬 실행법
- git clone 후 docker 로그인
- `docker-compose up --build` 실행
  - 만약 `exec ./build.sh: no such file or directory` 에러가 난다면 `build.sh`파일을 CELF에서 LF로 변경 뒤 저장해주시면 됩니다.
- `localhost`로 접속 (nginx 컨테이너에서 80포트를 받습니다.)

**docker-compose는 배포전 로컬 개발을 목적으로 구성했기에 디폴트 db인 sqlite3를 사용하고 있습니다.
이후 배포된 버전에서는 MySQL8.0을 사용하고 있습니다.**
<br/><br/>
### 배포한 어플리케이션 주소
- http://43.201.0.119
<br/><br/>
### 엔드포인트 호출
백엔드밖에 없고 개발이 이어지지 않지만 관례상 api, v1을 작성했습니다.
<br/><br/>
#### 유저 엔드포인트
- /api/v1/users/signup : 회원가입 엔드포인트입니다.
- /api/v1/users/signin : 회원가입 엔드포인트입니다.
#### 게시판 엔드포인트
- /api/v1/posters?page= : 게시글 목록 엔드포인트입니다. page 파라미터의 디폴트 값은 1입니다.
- /api/v1/posters/create : 게시글 생성 엔드포인트입니다.
- /api/v1/posters/<int:pk> : 특정 게시글 조회, 수정, 삭제 엔드포인트입니다.
<br/><br/><br/><br/><br/>
## 데이터베이스 구조

![img](https://github.com/SonJinHYo/image_repo/blob/main/image_server/wanted_erd.png?raw=true)

<br/><br/><br/><br/><br/>
## API 동작 데모 영상 링크
AWS로 배포한 주소로 진행했습니다. 
-  링크 : https://youtu.be/uYBaPCEVH1g

<br/><br/><br/><br/><br/>
## 구현 방법 설명
### API
게시글의 목록을 보여주고 목록을 조회를 할 때 게시글의 pk(id) 확인하여 이동하는 구조로 생각하여 api를 설계했습니다.
게시글 목록에서 게시글들의 pk를 받고, 프론트엔드에서 특정 게시글을 클릭 시 해당 게시글의 pk를 이용해 특정 게시글 api로 조회합니다.
조회 후 해당 게시글에서 수정, 삭제가 이뤄지고 
<br/><br/>
### DB Table
api 구현사항을 확인하기위해 필요한 필드만 작성했습니다.
- User : 회원가입 및 로그인을 위한 email, password 필드
- Poster(게시글) : 작성한 유저, 제목, 생성 시간, 업데이트 시간.
  - User 테이블과 일대다 구조를 가집니다.
- Content(내용) : Poster의 본문. 게시판 목록 업데이트시 내용까지 쿼리할 필요는 없지만 크기는 커서 따로 테이블을 두었습니다.
  - Poster 테이블과 일대일 구조를 가집니다.
<br/><br/>
### Nginx
django의 static파일, WAS와 Web서버의 분리를 위해 리버스 프록시 용도의 서버로 사용했습니다.
```
# [nginx.conf]

worker_processes auto;

events {
    worker_connections 512;
    multi_accept on;
    use epoll;
    accept_mutex on;
}

http {

    server {
        listen 80;
        server_name _;

        include mime.types;

        location /static/ {
            alias /data/static/;
        }

        location /api/ {
            # proxy_pass http://localhost:8000; # ECS prod
            proxy_pass http://django:8000;

            proxy_buffering off;

            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }


    }
}

```
- 리버스 프록시를 위해 static파일을 nginx 내부에 두었습니다.
  - static 파일은 django를 통해 특정 경로로 staticfiles 폴더를 생성하고, nginx의 도커파일이 해당 폴더를 COPY하는 방식으로 nginx 내부 컨테이너에 static 파일을 두었습니다.
- docker-compose에서 제시한 컨테이너명(django)으로 통신을 합니다
  - AWS ECS 환경에선 Nginx 컨테이너와 django 컨테이너를 같은 Task로 묶으면 localhost 주소를 통해 통신이 가능하여 배포시 localhost로 배포했습니다.
- /admin 페이지가 있지만 필요하지 않기에 /api/, /static/ 로케이션만 구현했습니다.
<br/><br/>
### unit test
테스트 목록입니다
- 파일 위치 : users/test.py
  - 회원가입
    - 정상 데이터
    - 패스워드 누락
    - 패스워드 길이 8자 이하
    - 이메일 형식 불만족(@ 생략)
  - 로그인
    - 정상 데이터
    - 패스워드 틀림
    - 패스워드 누락
- 파일 위치 : posters/test
  - 포스터 생성
    - 정상 데이터
    - 제목 최대 길이 초과
    - 내용 최대 길이 초과
  - 게시글 조회
    - pagination
  - 특정 게시글 조회, 수정, 삭제
    - 조회
    - 수정 : 정상데이터, 권한 x, 내용 누락
    - 삭제 : 정상 요청, 권한 x
<br/><br/>
### build.sh
- db에 마이그레이션 후 서버를 시작합니다.
- docker-compose에선 django 개발용 서버를 실행하고 프로덕션 환경에선 파이썬 미들웨어로 gunicorn을 사용합니다.
- unit test가 모두 통과하는지 확인이 필요하다면 해당 파일의 5,6 줄 사이에 `python3 manage.py test --settings=config.settings.local`를 넣어 확인할 수 있습니다.
<br/><br/><br/><br/><br/>

## API 명세
| 기능        | URL                       | MeThod           | Request                                                      | Response                                                     |
| ----------- | ------------------------- | ---------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 회원가입    | `api/v1/users/signup`     | POST             | {<br />"email":"your@email.com",<br />"password:"yourpassword"<br />} | 201 CREATE<br />"회원가입 완료"<br /><br />400 BAD_REQUEST<br />"회원가입 실패. 패스워드가 8자 미만이거나 이미 이미 존재하는 email입니다." |
| 로그인      | `api/v1/users/signin`     | POST             | {<br />"email":"your@email.com",<br />"password:"yourpassword"<br />} | 200 OK<br />{"token":"your_jwt_token"}<br /><br />400 BAD_REQUEST<br />{"error":"유효하지 않은 email과 password 조합입니다.}<br /><br />400 BAD_REQUEST<br />"email과 password를 모두 입력해주세요" |
| 게시글 목록 | `api/v1/posters?page=`    | GET              |                                                              | 200 OK<br />[<br />  {<br/>"pk":2,<br/>"user" :{<br />      "email":"author-email",<br />   },<br />   "title": "poster title",<br />   "updated_at": "updated-time"<br />   },<br />   ...<br />] |
| 게시글 생성 | `api/v1/posters/create`   | POST             | {<br />"title":"poster title",<br />"content":"poster content"<br />} | 201 CREATE<br />{"message": "게시글을 생성했습니다"}<br />400 BAD_REQUEST<br />"제목과 내용을 모두 입력해주세요"<br /><br />400 BAD_REQUEST<br />{"message": "제목의 길이를 확인해주세요.(100자 이하)"}<br /><br />400 BAD_REQUEST<br />{"message": "내용의 길이를 확인해주세요.(1000자 이하)"} |
| 게시글 조회 | `api/v1/posters/<int:pk>` | GET, DELETE, PUT | PUT<br />{<br />"content":"edited content"<br />}            | GET,PUT 200 OK<br />{<br />     "user":  {<br />         "email": "author-email"<br />     },<br />     "title":  "poster title",<br />     "content": {<br />         "text": "poster content"<br />     },<br />     "created_at": "created-time",<br />     "updated_at": "updated-time"<br /> }<br /><br />PUT, DELETE 403 FORBIDDEN<br />"권한이 없습니다"<br /><br />GET, PUT, DELETE 400 BAD_REQUEST<br />"존재하지 않는 게시글입니다."<br /><br />PUT 400 BAD_REQUEST<br />{"message":"게시물 내용의 길이를 확인해주세요. (1000자 이하)"}<br /><br />PUT 400 BAD_REQUEST<br />{"message": "내용을 작성해주세요"} |

## AWS 아키텍쳐 구조
![img](https://github.com/SonJinHYo/image_repo/blob/main/image_server/%EC%95%84%ED%82%A4%ED%85%8D%EC%B3%90.png?raw=true)

ECS와 RDS를 이용하여 간단한 구조로 배포했습니다.

- ECS 클러스터를 생성하고 내에 nginx, django 컨테이너를 포함하는 Fargate Task를 생성했습니다.
  - Task : 0.5 vCPU, 1GB Memory / Fargate 유형 / Public IP : 43.201.0.119
  - Application ELB로 serives내의 task를 관리하게하여 무중단 배포 구조를 만들 수 있지만 애플리케이션 스케일에 비해 과한 감이 있어 단일 Task로 배포하게 되었습니다. (이에 Public IP가 임의로 배정되기에 django.settings.prod에 ALLOWED_HOST를 와일드카드로 해두었습니다.)
  - Task의 이미지를 DockerHub 개인 레포지토리와 연결하여 로컬에서 업데이트 후 Task를 재배포하면 수정없이 원할한 배포가 가능합니다.
- RDS로 MySQL 데이터베이스를 생성했습니다.
  - VPC 내부에 RDS를 두고 Task를 같은 VPC에 두어 Task 내의 django만 DB와 연결이 가능한 구조를 설계했습니다.

