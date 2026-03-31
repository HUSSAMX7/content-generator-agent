from pydantic import BaseModel, Field


class Axis(BaseModel):
    title: str = Field(description="عنوان المحور الرئيسي")
    content: str = Field(description="النص الكامل للمحور بما فيه جميع الأقسام الفرعية")


class DocumentAxes(BaseModel):
    axes: list[Axis] = Field(description="list of axes in the document")

