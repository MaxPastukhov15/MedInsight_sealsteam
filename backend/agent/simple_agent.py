"""Simple LLM agent without LangGraph."""
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from backend.core.config import get_settings
from backend.database.models import DiseaseCase

settings = get_settings()


def create_simple_agent(db: Session):
    """Create simple agent that generates SQL."""
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
    )

    sql_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Ты аналитик медицинских данных.

База данных PostgreSQL с таблицей disease_cases:
- id: INTEGER
- district: VARCHAR(100) - район
- disease: VARCHAR(100) - заболевание
- date: DATE - дата
- age: INTEGER - возраст
- gender: VARCHAR(10) - пол

Генерируй ТОЛЬКО SELECT запросы PostgreSQL.
Не используй DROP, DELETE, UPDATE.

Примеры:
- "Сколько случаев гриппа?" -> SELECT COUNT(*) FROM disease_cases WHERE disease = 'грипп';
- "Тренды по месяцам" -> SELECT date_trunc('month', date) as month, COUNT(*) FROM disease_cases GROUP BY month ORDER BY month;
""",
            ),
            ("human", "{question}"),
        ]
    )

    def agent(inputs: dict) -> dict:
        question = inputs["question"]

        # Generate SQL
        sql_response = llm.invoke(sql_prompt.format_messages(question=question))
        sql_query = sql_response.content.strip()

        # Clean SQL (remove markdown)
        if "```" in sql_query:
            sql_query = sql_query.split("```")[1]
            if sql_query.startswith("sql"):
                sql_query = sql_query[3:]
            sql_query = sql_query.strip()

        # Execute SQL
        try:
            result = db.execute(sql_query).fetchall()
            result_str = str(result)
        except Exception as e:
            result_str = f"SQL Error: {str(e)}"

        # Format answer
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Отформатируй результат SQL запроса в понятный ответ на русском языке.",
                ),
                (
                    "human",
                    "Вопрос: {question}\n\nSQL: {sql}\n\nРезультат: {result}\n\nОтвет:",
                ),
            ]
        )

        answer = llm.invoke(
            answer_prompt.format_messages(
                question=question, sql=sql_query, result=result_str
            )
        )

        return {"answer": answer.content, "sql": sql_query, "sources": []}

    return agent
