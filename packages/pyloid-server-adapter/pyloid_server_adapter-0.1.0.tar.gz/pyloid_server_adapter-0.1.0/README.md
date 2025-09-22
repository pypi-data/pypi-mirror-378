# Pyloid Server Adapter

Pyloid Server Adapter는 FastAPI 애플리케이션에서 Pyloid 컨텍스트를 주입할 수 있는 어댑터입니다.

## 기능

- **자동 미들웨어**: FastAPI 앱에 어댑터를 설정하면 모든 요청에 대해 자동으로 `PyloidContext` 주입
- `X-Pyloid-Window-Id` 헤더를 통한 윈도우 ID 관리
- Pyloid 인스턴스와 윈도우 등록/조회 기능
- **다양한 사용법**: 미들웨어, 데코레이터, Depends 등 여러 방식 지원

## 설치

```bash
# 개발 의존성 포함
pip install -e ".[dev]"
```

또는

```bash
# FastAPI만 필요
pip install fastapi
```

## 사용법

### 기본 설정

```python
from fastapi import FastAPI, Request
from src.fastapi_adapter import FastAPIAdapter

app = FastAPI()

def start(app: FastAPI, host: str, port: int):
    import uvicorn
    uvicorn.Server(config=uvicorn.Config(app, host=host, port=port)).run()

fastapi_adapter = FastAPIAdapter(app=app, start_function=start)

# Pyloid 인스턴스 설정
class MockPyloid:
    def __init__(self):
        self.name = "My Pyloid App"

fastapi_adapter.set_pyloid_instance(MockPyloid())

# 윈도우 등록
class MockWindow:
    def __init__(self, window_id: str):
        self.id = window_id
        self.title = f"Window {window_id}"

window = MockWindow("main-window")
fastapi_adapter.register_window("main-window", window)
```

### ctx 사용 방법 1: 미들웨어 방식 (권장) ⭐

**자동으로 모든 요청에 대해 PyloidContext가 주입됩니다!**

```python
@app.get("/api/data")
async def get_data(request: Request):
    # request.state.pyloid_context로 접근
    ctx = request.state.pyloid_context
    return {
        "pyloid": ctx.pyloid.name if ctx.pyloid else None,
        "window": ctx.window.title if ctx.window else None
    }
```

### ctx 사용 방법 2: 데코레이터 사용

```python
from src.fastapi_adapter import PyloidContext

@app.get("/api/data2")
@fastapi_adapter.inject_context
async def get_data2(ctx: PyloidContext):
    return {
        "pyloid": ctx.pyloid.name if ctx.pyloid else None,
        "window": ctx.window.title if ctx.window else None
    }
```

### ctx 사용 방법 3: FastAPI Depends 사용

```python
from fastapi import Depends
from src.fastapi_adapter import PyloidContext

@app.get("/api/data3")
async def get_data3(ctx: PyloidContext = Depends(fastapi_adapter.get_context_dependency())):
    return {
        "pyloid": ctx.pyloid.name if ctx.pyloid else None,
        "window": ctx.window.title if ctx.window else None
    }
```

### 클라이언트 요청 예시

```bash
# X-Pyloid-Window-Id 헤더를 포함한 요청
curl -H "X-Pyloid-Window-Id: main-window" http://localhost:8000/api/data
```

## PyloidContext

`PyloidContext` 클래스는 다음과 같은 속성을 제공합니다:

- `pyloid`: Pyloid 애플리케이션 인스턴스
- `window`: 현재 윈도우 인스턴스 (X-Pyloid-Window-Id 헤더에 해당하는 윈도우)

## API 참조

### FastAPIAdapter

#### `__init__(app: FastAPI, start_function: Callable[[str, int], None])`
FastAPI 어댑터를 초기화합니다.

#### `set_pyloid_instance(pyloid: Any)`
Pyloid 인스턴스를 설정합니다.

#### `register_window(window_id: str, window: Any)`
윈도우를 등록합니다.

#### `get_window_by_id(window_id: str) -> Optional[Any]`
윈도우 ID로 윈도우를 조회합니다.

#### `get_pyloid_context(request: Request) -> PyloidContext`
요청으로부터 PyloidContext를 생성합니다.

#### `get_context_dependency() -> Callable`
FastAPI 의존성 주입을 위한 함수를 반환합니다.

#### `inject_context(func: Callable) -> Callable`
ctx 매개변수가 있는 함수에 PyloidContext를 주입하는 데코레이터입니다.

### PyloidContextMiddleware

자동으로 모든 HTTP 요청에 대해 PyloidContext를 주입하는 미들웨어입니다.

#### 속성
- `pyloid_adapter`: FastAPIAdapter 인스턴스

#### 사용법
미들웨어는 `FastAPIAdapter` 생성 시 자동으로 등록되므로 별도 설정이 필요하지 않습니다.