# ProcessGPT Agent Framework
## A2A SDK 연동을 위한 경량 에이전트 서버 프레임워크

Supabase 기반의 프로세스 작업(Todolist)을 폴링하고, A2A 규격 이벤트를 통해 작업 상태/결과를 기록하는 **경량 에이전트 서버 프레임워크**입니다.

### 📋 요구사항
- **런타임**: Python 3.9+ (권장: Python 3.11)
- **데이터베이스**: Supabase (PostgreSQL) + 제공된 RPC/테이블
- **이벤트 규격**: A2A `TaskStatusUpdateEvent` / `TaskArtifactUpdateEvent`

## 📊 이벤트 타입별 저장 테이블 및 특징

### 1. TaskStatusUpdateEvent (작업 상태 이벤트)
- **저장 테이블**: `events`
- **용도**: 작업 진행 상황, 사용자 입력 요청, 에러 알림 등
- **저장 데이터**: 메시지 래퍼를 제거한 순수 payload만 `data` 컬럼에 JSON으로 저장

```python
# 예시 코드
event_queue.enqueue_event(
    TaskStatusUpdateEvent(
        status={
            "state": TaskState.working,  # working, input_required, completed 등
            "message": new_agent_text_message("진행 중입니다", context_id, task_id),
        },
        final=False,
        contextId=context_id,
        taskId=task_id,
        metadata={"event_type": "task_started"}  # events.event_type에 저장
    )
)
```

**특별 규칙**:
- `state=input_required`일 때는 자동으로 `event_type=human_asked`로 저장됨
- 메시지는 `new_agent_text_message()` 유틸 함수로 생성

### 2. TaskArtifactUpdateEvent (작업 결과 이벤트)
- **저장 테이블**: `todolist` (output 컬럼)
- **용도**: 최종 작업 결과물 전송
- **저장 데이터**: 아티팩트 래퍼를 제거한 순수 payload만 `output` 컬럼에 JSON으로 저장

```python
# 예시 코드
artifact = new_text_artifact(
    name="처리결과",
    description="작업 완료 결과",
    text="실제 결과 데이터"
)
event_queue.enqueue_event(
    TaskArtifactUpdateEvent(
        artifact=artifact,
        lastChunk=True,  # 최종 결과면 True
        contextId=context_id,
        taskId=task_id,
    )
)
```

**특별 규칙**:
- `lastChunk=True` 또는 `final=True`일 때만 최종 저장됨 (`p_final=true`)
- 아티팩트는 `new_text_artifact()` 유틸 함수로 생성

## 🔄 데이터 흐름과 값 전달 방식

### 전체 흐름
1. **작업 폴링**: 서버가 Supabase `todolist` 테이블에서 새 작업을 가져옴
2. **컨텍스트 준비**: `RequestContext`에 작업 정보와 사용자 입력을 담음
3. **익스큐터 실행**: 사용자가 구현한 `AgentExecutor.execute()` 메서드 호출
4. **이벤트 전송**: 익스큐터에서 진행 상황과 결과를 이벤트로 전송
5. **데이터 저장**: 이벤트 타입에 따라 적절한 테이블에 저장

### 값 전달 과정
```python
# 1. 서버에서 작업 정보 가져오기
row = context.get_context_data()["row"]  # todolist 테이블의 한 행
context_id = row.get("root_proc_inst_id") or row.get("proc_inst_id")  # 프로세스 ID
task_id = row.get("id")  # 작업 ID
user_input = context.get_user_input()  # 사용자가 입력한 내용

# 2. 메시지/아티팩트 생성시 JSON 문자열로 변환
payload = {"result": "처리 완료"}
message_text = json.dumps(payload, ensure_ascii=False)  # 중요: JSON 문자열로!

# 3. 서버가 자동으로 래퍼 제거 후 순수 payload만 저장
# events.data 또는 todolist.output에 {"result": "처리 완료"}만 저장됨
```

## 🚀 빠른 시작 가이드

### 1단계: 설치
```bash
# 패키지 설치
pip install -e .

# 또는 requirements.txt 사용
pip install -r requirements.txt
```

### 2단계: 환경 설정
`.env` 파일 생성:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
ENV=dev
```

### 3단계: 서버 구현 방법
서버는 이렇게 만드세요:

```python
# my_server.py
import asyncio
from dotenv import load_dotenv
from processgpt_agent_sdk.processgpt_agent_framework import ProcessGPTAgentServer
from my_executor import MyExecutor  # 아래에서 구현할 익스큐터

async def main():
    load_dotenv()
    
    server = ProcessGPTAgentServer(
        agent_executor=MyExecutor(),  # 여러분이 구현할 익스큐터
        agent_type="my-agent"  # Supabase todolist.agent_orch와 매칭되어야 함
    )
    server.polling_interval = 3  # 3초마다 새 작업 확인
    
    print("서버 시작!")
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("서버 종료")
```

### 4단계: 익스큐터 구현 방법
익스큐터는 이렇게 만드세요:

```python
# my_executor.py
import asyncio
import json
from typing_extensions import override
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import TaskStatusUpdateEvent, TaskState, TaskArtifactUpdateEvent
from a2a.utils import new_agent_text_message, new_text_artifact

class MyExecutor(AgentExecutor):
    @override
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # 1. 작업 정보 가져오기
        row = context.get_context_data()["row"]
        context_id = row.get("root_proc_inst_id") or row.get("proc_inst_id")
        task_id = row.get("id")
        user_input = context.get_user_input()  # 사용자가 입력한 내용
        
        print(f"처리할 작업: {user_input}")
        
        # 2. 작업 시작 알림 (events 테이블에 저장됨)
        event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                status={
                    "state": TaskState.working,
                    "message": new_agent_text_message("작업 시작", context_id, task_id),
                },
                final=False,
                contextId=context_id,
                taskId=task_id,
                metadata={"event_type": "task_started"}
            )
        )
        
        # 3. 실제 작업 수행 (여기에 여러분의 로직 작성)
        await asyncio.sleep(2)
        result_data = {"status": "완료", "input": user_input, "output": "처리 결과"}
        
        # 4. 최종 결과 전송 (todolist.output에 저장됨)
        artifact = new_text_artifact(
            name="처리결과",
            description="작업 완료 결과",
            text=json.dumps(result_data, ensure_ascii=False)  # JSON 문자열로!
        )
        event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                artifact=artifact,
                lastChunk=True,  # 중요: 최종 결과면 True
                contextId=context_id,
                taskId=task_id,
            )
        )

    @override
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass  # 취소 로직 (필요시 구현)
```

### 5단계: 실행
```bash
python my_server.py
```

## 🤝 Human-in-the-Loop (사용자 입력 요청) 패턴

사용자 입력이 필요할 때:

```python
# 사용자 입력 요청
question_data = {
    "question": "어떤 방식으로 처리할까요?",
    "options": ["방식A", "방식B", "방식C"]
}

event_queue.enqueue_event(
    TaskStatusUpdateEvent(
        status={
            "state": TaskState.input_required,  # 이 상태가 중요!
            "message": new_agent_text_message(
                json.dumps(question_data, ensure_ascii=False),
                context_id, task_id
            ),
        },
        final=True,
        contextId=context_id,
        taskId=task_id,
        metadata={"job_id": f"job-{task_id}"}  # job_id 필수
    )
)
# 자동으로 events 테이블에 event_type=human_asked로 저장됨
```

## 📋 체크리스트 (실패 없는 통합을 위한)

### 필수 설정
- [ ] `.env`에 `SUPABASE_URL`, `SUPABASE_KEY` 설정
- [ ] `requirements.txt` 설치 완료
- [ ] Supabase에서 제공 SQL(`database_schema.sql`, `function.sql`) 적용

### 코드 구현
- [ ] 서버에서 `agent_type`이 Supabase `todolist.agent_orch`와 매칭됨
- [ ] 익스큐터에서 `contextId`, `taskId`를 올바르게 설정
- [ ] 상태 이벤트는 `new_agent_text_message()`로 생성
- [ ] 최종 결과는 `new_text_artifact()` + `lastChunk=True`로 전송
- [ ] HITL 요청시 `TaskState.input_required` 사용

## 🚨 자주 발생하는 문제

### 1. 설치 문제
**증상**: `ModuleNotFoundError`
```bash
# 해결
pip install -e .
pip install a2a-sdk==0.3.0 --force-reinstall
```

### 2. 작업이 폴링되지 않음
**원인**: Supabase 연결 문제
**해결**:
- `.env` 파일 위치 확인 (프로젝트 루트)
- URL/Key 재확인
- `agent_type`이 todolist.agent_orch와 매칭되는지 확인

### 3. 이벤트가 저장되지 않음
**원인**: 테이블/함수 누락
**해결**:
- `database_schema.sql`, `function.sql` 실행 확인
- Supabase 테이블 권한 확인

### 4. 결과가 래퍼와 함께 저장됨
**원인**: JSON 문자열 변환 누락
```python
# 올바른 방법
text=json.dumps(data, ensure_ascii=False)  # JSON 문자열로!

# 잘못된 방법  
text=data  # 딕셔너리 직접 전달 (X)
```

## 📚 샘플 코드 (간단 버전)

### 기본 서버
```python
# sample_server/minimal_server.py
import asyncio
from dotenv import load_dotenv
from processgpt_agent_sdk.processgpt_agent_framework import ProcessGPTAgentServer
from sample_server.minimal_executor import MinimalExecutor

async def main():
    load_dotenv()
    server = ProcessGPTAgentServer(
        agent_executor=MinimalExecutor(), 
        agent_type="crewai-action"
    )
    server.polling_interval = 3
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
```

### 기본 익스큐터  
```python
# sample_server/minimal_executor.py
import asyncio
import json
from typing_extensions import override
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import TaskStatusUpdateEvent, TaskState, TaskArtifactUpdateEvent
from a2a.utils import new_agent_text_message, new_text_artifact

class MinimalExecutor(AgentExecutor):
    @override
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        row = context.get_context_data()["row"]
        context_id = row.get("root_proc_inst_id") or row.get("proc_inst_id")
        task_id = row.get("id")
        user_input = context.get_user_input()

        # 진행 상태
        event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                status={
                    "state": TaskState.working,
                    "message": new_agent_text_message("처리중", context_id, task_id),
                },
                final=False,
                contextId=context_id,
                taskId=task_id,
                metadata={"event_type": "task_started"}
            )
        )

        await asyncio.sleep(1)

        # 최종 결과
        result = {"input": user_input, "output": "처리 완료"}
        artifact = new_text_artifact(
            name="결과",
            description="처리 결과",
            text=json.dumps(result, ensure_ascii=False)
        )
        event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                artifact=artifact,
                lastChunk=True,
                contextId=context_id,
                taskId=task_id,
            )
        )

    @override
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass
```

## 🔧 실행 방법

### 개발 환경에서 실행
```bash
python sample_server/minimal_server.py
```

### 실제 사용시
```bash
python my_server.py
```

---

## 📚 레퍼런스

### 주요 함수들
- `ProcessGPTAgentServer.run()`: 서버 시작
- `new_agent_text_message(text, context_id, task_id)`: 상태 메시지 생성
- `new_text_artifact(name, desc, text)`: 결과 아티팩트 생성

### 이벤트 저장 규칙
- **TaskStatusUpdateEvent** → `events` 테이블 (`data` 컬럼)
- **TaskArtifactUpdateEvent** → `todolist` 테이블 (`output` 컬럼)
- 래퍼 자동 제거 후 순수 payload만 저장
