from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('NOTION_API_KEY')

app = FastAPI(
    title="Notion Page Creator API",
    description="A simple API for creating Notion pages.",
    version="1.0.0",
)


class NotionPageRequest(BaseModel):
    notion_parent_page_id: str
    title: str
    content: str


def create_notion_page(notion_api_key, notion_parent_page_id, title, content):
    url = 'https://api.notion.com/v1/pages'

    headers = {
        'Authorization': f'Bearer {notion_api_key}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }

    data = {
        "parent": {"type": "page_id", "page_id": notion_parent_page_id},
        "properties": {
            "title": [
                {
                    "text": {
                        "content": title
                    }
                }
            ]
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": content
                            }
                        }
                    ]
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


@app.post("/create-notion-page/")
async def create_page(request: NotionPageRequest):
    try:
        response = create_notion_page(
            notion_api_key=api_key,
            notion_parent_page_id=request.notion_parent_page_id,
            title=request.title,
            content=request.content
        )
        return {"status": "success", "data": response}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


