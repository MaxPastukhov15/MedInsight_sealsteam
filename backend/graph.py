"""Medical Analytics Agent - LangGraph implementation with parallel tool calls."""
import os
import re

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage

from backend.state import MedicalAgentState
from backend.config import log
from backend.tools import TOOLS, get_last_chart

# Configuration
MAX_STEPS = int(os.getenv("MAX_STEPS", "10"))
MODEL_NAME = os.getenv("MODEL_NAME", "qwen/qwen3-32b")


# ============ SYSTEM PROMPT ============

SYSTEM_PROMPT = """Ты медицинский аналитик данных. Отвечай на русском языке. НЕ ДУМАЙ ВСЛУХ.

СХЕМА БАЗЫ ДАННЫХ:
- patients:
patient_id   birth_dt   age gender        district                 region
2 1958-05-08  67.0      Ж      ПУШКИНСКИЙ        САНКТ-ПЕТЕРБУРГ
8 1957-10-28  68.0      М      ВЫБОРГСКИЙ        САНКТ-ПЕТЕРБУРГ
9 1953-05-03  72.0      Ж     КАЛИНИНСКИЙ        САНКТ-ПЕТЕРБУРГ
10 1981-05-30  44.0      М      ПРИМОРСКИЙ        САНКТ-ПЕТЕРБУРГ
Всего  379246 строчек
- prescriptions:
prescription_id patient_id diagnosis_code    drug_id                date    year  month
24419779    1226228            F06  200900018 2022-03-31 11:52:30  2022.0    3.0
17890856      62857          I11.9  201300167 2019-06-04 18:41:10  2019.0    6.0
18749669    1186134          K86.1  201300027 2019-10-29 12:35:31  2019.0   10.0
Всего 916283 строчек
diagnoses:
diagnosis_code  diagnosis_name  disease_class
A00                                             Холера  НЕКОТОРЫЕ ИНФЕКЦИОННЫЕ И ПАРАЗИТАРНЫЕ БОЛЕЗНИ
D14.1          Доброкачественное новообразование гортани  НОВООБРАЗОВАНИЯ
U85         Устойчивость к противоопухолевым средствам  НЕ ОПРЕДЕЛЕН
XXII                         КОДЫ ДЛЯ СПЕЦИАЛЬНЫХ ЦЕЛЕЙ  ВНЕШНИЕ ПРИЧИНЫ ЗАБОЛЕВАЕМОСТИ И СМЕРТНОСТИ
Всего 14801 строчек
- drugs:
drug_id        trade_name                                          full_name     dosage   price
200052200       Галоперидол                           Галоперидол, 1,5 мг № 50        1.5   12.98
200052400       Галоперидол                   Галоперидол, 5 мг № 50, таблетки          5   15.51
200059000           Манинил                    Манинил, 3,5 мг № 120, таблетки        3.5   93.42
Всего 3393 строчек.

ИНСТРУМЕНТЫ:
- search_codes: поиск кодов диагнозов/препаратов
- run_sql: выполнение SQL запроса
- forecast_trend: прогноз временных рядов
- create_chart: визуализация данных

ОБЯЗАТЕЛЬНО:
1. ВСЕГДА вызывай create_chart после run_sql - каждый анализ должен иметь график!
2. После search_codes вызывай run_sql И create_chart В ОДНОМ ОТВЕТЕ
3. sql="REUSE_SQL" использует предыдущий SQL для графика

SQL ПРИМЕРЫ:
-- Тренд по месяцам:
SELECT DATE_TRUNC('month', prescription_date) AS month, COUNT(*) AS cnt
FROM prescriptions WHERE diagnosis_code IN ({CODES}) GROUP BY month ORDER BY month

-- Топ по категориям:
SELECT district, COUNT(*) AS cnt FROM patients GROUP BY district ORDER BY cnt DESC

ПРАВИЛА:
- {CODES} заменяется на найденные коды
- include_forecast=True добавляет прогноз на график
- Финальный ответ: краткий анализ с числами"""


# ============ GRAPH ============

class MedicalGraph:
    def __init__(self):
        self.checkpointer = InMemorySaver()
        self.model = ChatOpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            model=MODEL_NAME,
            temperature=0
        ).bind_tools(TOOLS, parallel_tool_calls=True)
        self.graph = self._build_graph()
        log("Graph", f"Initialized: {MODEL_NAME}", "G")

    def _build_graph(self):
        builder = StateGraph(MedicalAgentState)
        tools_by_name = {t.name: t for t in TOOLS}

        def agent(state: MedicalAgentState) -> dict:
            messages = state["messages"]
            last_msg = messages[-1] if messages else None
            
            # Reset on new user message
            if isinstance(last_msg, HumanMessage):
                step = 1
                reset = {"final_response": None, "visualization_json": None, "found_codes": [], "last_sql": None}
            else:
                step = state.get("step_count", 0) + 1
                reset = {}
            
            log("Agent", f"Step {step}/{MAX_STEPS}", "B")
            
            if step > MAX_STEPS:
                return {"final_response": {"answer": "Достигнут лимит шагов."}, "step_count": step, **reset}
            
            # Add system prompt
            if not any(isinstance(m, SystemMessage) for m in messages):
                messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
            
            response = self.model.invoke(messages)
            
            if response.tool_calls:
                log("Agent", f"Tool calls: {[tc['name'] for tc in response.tool_calls]}", "G")
            else:
                log("Agent", f"Response: {str(response.content)[:100]}...", "C")
            
            return {"messages": [response], "step_count": step, **reset}

        def tools_node(state: MedicalAgentState) -> dict:
            last_msg = state["messages"][-1]
            tool_calls = getattr(last_msg, 'tool_calls', None) or []
            if not tool_calls:
                return {}
            
            results = []
            viz = None
            found_codes = list(state.get("found_codes", []))
            last_sql = state.get("last_sql")
            
            for tc in tool_calls:
                tool_name = tc["name"]
                tool_args = dict(tc["args"])
                log("Tool", f"{tool_name}: {str(tool_args)[:100]}", "G")
                
                # Inject codes into SQL
                if "sql" in tool_args and "{CODES}" in tool_args["sql"] and found_codes:
                    codes_str = ", ".join([f"'{c}'" for c in found_codes])
                    tool_args["sql"] = tool_args["sql"].replace("{CODES}", codes_str)
                
                # Reuse SQL
                if tool_args.get("sql") == "REUSE_SQL" and last_sql:
                    tool_args["sql"] = last_sql
                
                try:
                    tool_fn = tools_by_name.get(tool_name)
                    result = tool_fn.invoke(tool_args) if tool_fn else f"Unknown tool: {tool_name}"
                    
                    # Extract codes from search results
                    if tool_name == "search_codes" and result and "Error" not in result:
                        for line in result.split('\n')[1:]:
                            parts = line.split()
                            if parts and parts[0] not in found_codes:
                                found_codes.append(parts[0])
                    
                    # Track SQL
                    if tool_name == "run_sql" and "Error" not in str(result):
                        last_sql = tool_args["sql"]
                    
                    # Capture chart
                    if tool_name == "create_chart":
                        chart = get_last_chart()
                        if chart:
                            viz = chart
                        
                except Exception as e:
                    result = f"Error: {str(e)[:200]}"
                    log("Tool", f"Error: {e}", "R")
                
                results.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
                log("Tool", f"Result: {str(result)[:150]}...", "C")
            
            update = {"messages": results, "found_codes": found_codes, "last_sql": last_sql}
            if viz:
                update["visualization_json"] = viz
            return update

        def should_continue(state: MedicalAgentState) -> str:
            if state.get("final_response") or state.get("step_count", 0) >= MAX_STEPS:
                return "end"
            
            last_msg = state["messages"][-1]
            tool_calls = getattr(last_msg, 'tool_calls', None) or []
            if tool_calls:
                return "tools"
            
            return "end"

        def finalize(state: MedicalAgentState) -> dict:
            if state.get("final_response"):
                return {}
            
            last_msg = state["messages"][-1]
            content = getattr(last_msg, 'content', '') or ''
            content = re.sub(r'<[^>]+>.*?</[^>]+>', '', content, flags=re.DOTALL).strip()
            
            return {"final_response": {"answer": content or "Анализ завершен."}}

        builder.add_node("agent", agent)
        builder.add_node("tools", tools_node)
        builder.add_node("finalize", finalize)
        
        builder.add_edge(START, "agent")
        builder.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": "finalize"})
        builder.add_edge("tools", "agent")
        builder.add_edge("finalize", END)
        
        return builder.compile(checkpointer=self.checkpointer)


medical_graph = MedicalGraph()
