from openai import AsyncOpenAI
from sqlalchemy import TextClause, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_KEY)


async def execute_query(query: str, db: AsyncSession) -> list[dict]:
    """
    Execute query in the database
    """
    sql_query = text(query)
    result = await db.execute(sql_query)
    result_rows = result.fetchall()
    # save the result in a dictionary and ask llm to coment about it
    data = {}
    data["result"] = [dict(row._mapping) for row in result_rows]

    return [dict(row._mapping) for row in result_rows]


async def analise_results(results: list[dict], prompt: str) -> str:
    """
    Analise the results and return a comment
    """
    ai_response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                You are a BI analyst and need to take insights based on some chunk of data and a user question.
                You should analyze the data and generate a comment that can be useful for the user based on what he asked for.
                The comment should be concise and direct.
             """,
            },
            {
                "role": "user",
                "content": f"""
                data: {results},
                user_question: {prompt}
             """,
            },
        ],
    )
    if ai_response.choices[0].message.content:
        return ai_response.choices[0].message.content
    return "No insights for this query results"


async def generate_query(prompt: str) -> str | None:
    """
    Get answer from AI model
    """

    messages = [
        {
            "role": "system",
            "content": """
         You are a proficient SQL user and need to create a query for the user.  
Your goal is to generate a query that will return what the user asked for, using the best SQL practices.  
You are operating in a PostgreSQL database.  

### Guidelines:
- Always use column names surrounded by double quotes when using aliases. For example, use `ec."createdAt"` instead of `ec.createdAt`.
- Prefer to bring descriptive fields (e.g., names) instead of their IDs when applicable.
- Order the data so that the most recent rows appear first, based on timestamps.
- Use JOINs when appropriate to combine related tables, using foreign keys (FKs) as described below.
- If you do not have enough information to create the query, respond with `Not enough information` in the `query` field.
- If the user question can not be answered directly with data from a query, you should make a query to gather data that you think will be needed to make an analisis and possibly answer the question.

### Models Description:
The database has the following tables and their relationships:  

1. **`embed_users`**  
   - Columns:  
     - `session_id` (Primary Key)  
     - `name`: User's name.  
     - `email`: User's email address.  
     - `created_at`: Timestamp of when the user session was created.  

2. **`embed_chats`**  
   - Columns:  
     - `id` (Primary Key)  
     - `prompt`: Text of the chat prompt.  
     - `response`: Text of the chat response.  
     - `session_id` (FK to `embed_users.session_id`): Links the chat to a specific user session.  
     - `embed_id` (FK to `embed_configs.id`): Links the chat to a specific embed configuration.  
     - `createdAt`: Timestamp of when the chat was created.  

3. **`embed_configs`**  
   - Columns:  
     - `id` (Primary Key)  
     - `workspace_id` (FK to `workspaces.id`): Links the configuration to a specific workspace.  
     - `createdAt`: Timestamp of when the configuration was created.  

4. **`workspaces`**  
   - Columns:  
     - `id` (Primary Key)  
     - `name`: Name of the workspace. 
     - `slug`: Unique slug for the workspace.
     - `createdAt`: Timestamp of when the workspace was created.  
     - `lastUpdatedAt`: Timestamp of the last update to the workspace.

### Example Relationships:
- A user (`embed_users`) can have multiple chats (`embed_chats`) linked by `session_id`.  
- A chat (`embed_chats`) can reference an embed configuration (`embed_configs`) by `embed_id`.  
- An embed configuration (`embed_configs`) is linked to a workspace (`workspaces`) by `workspace_id`.  

### Output Format:
Respond in the following JSON format on a single line:  
{ 
   "query": "The query you created, written in one line with no formatting.",
   "confidence": Your confidence level in the query as a float between 0 and 1.
}.

If you lack sufficient information to generate the query, return:
{ 
   "query": "Not enough information",
   "confidence": 0.0
}
         """,
        },
        {"role": "user", "content": prompt},
    ]

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,  # type: ignore
    )

    return response.choices[0].message.content
