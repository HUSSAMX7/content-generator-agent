from pydantic import BaseModel, Field


class DocumentHeadings(BaseModel):
    headings: list[str] = Field(description="قائمة عناوين المحاور الرئيسية فقط")
