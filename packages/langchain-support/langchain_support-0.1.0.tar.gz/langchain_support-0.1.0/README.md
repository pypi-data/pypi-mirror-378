# Langchain Support

LangChain과 LangGraph를 위한 유틸리티 패키지입니다.

## 설치

```bash
pip install langchain-support
```

## 사용법

### 그래프 시각화

```python
from langchain_support.graph import save_graph_png

# LangGraph의 CompiledStateGraph를 PNG로 저장
save_graph_png(graph, "my_graph.png")
```


## 요구사항

- Python >= 3.11
- langchain-core >= 0.3.76
- langgraph >= 0.6.7