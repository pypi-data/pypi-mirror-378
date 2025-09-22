from langchain_core.runnables.graph import NodeStyles
from langgraph.graph.state import CompiledStateGraph

def save_graph_png(graph, file_path="graph.png"):
    """그래프를 PNG 파일로 저장"""
    try:
        if isinstance(graph, CompiledStateGraph):
            png_data = graph.get_graph(xray=True).draw_mermaid_png(
                background_color="white",
                node_colors=NodeStyles(),
            )
            
            with open(file_path, "wb") as f:
                f.write(png_data)
            
            print(f"✅ PNG 파일 저장 완료: {file_path}")
            return True
            
    except Exception as e:
        print(f"❌ PNG 저장 실패: {e}")
        return False