from pydantic import BaseModel, Field


class DocumentHeadings(BaseModel):
    headings: list[str] = Field(description="قائمة المحاور الرئيسية في الوثيقة")
