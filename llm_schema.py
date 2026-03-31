from pydantic import BaseModel, Field


class DocumentHeadings(BaseModel):
    headings: list[str] = Field(description="قائمة عناوين المحاور الرئيسية فقط")


class NormalizedHeadings(BaseModel):
    headings: list[str] = Field(description="العناوين بعد التنظيف والتوحيد")
