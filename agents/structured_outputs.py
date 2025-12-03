from typing import List

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    """
    Requirement required for software engineer agent to ensure
    that all features have been completed
    """

    id: str = Field(examples=["REQ-001"])
    type: str = Field(examples=["Functional"])
    priority: str = Field(examples=["High"])
    title: str = Field(examples=["Create Todo Item"])
    description: str = Field(
        examples=[
            "The system shall allow users to create new todo items with a title, optional description, optional due date, and optional priority level."
        ]
    )
    acceptance_criteria: List[str] = Field(
        examples=[
            "A user can enter a title (mandatory, max 255 characters).",
            "A user can enter a description (optional, multiline text).",
            "A user can select a due date (optional).",
            "A user can select a priority level (optional: Low, Medium, High).",
            "Upon successful creation, the new todo item appears in the list of todos.",
            "Error messages are displayed for invalid input (e.g., missing title).",
        ]
    )
    status: str = Field(examples=["Pending"])


class UserStories(BaseModel):
    id: str = Field(examples=["RUS-001"])
    title: str = Field(examples=["Create a new task"])
    story: str = Field(
        examples=[
            "As a user, I want to add new tasks to my list, so I can keep track of what I need to do."
        ]
    )
    requirements_linked: List[str] = Field(examples=["REQ-001"])
    status: str = Field(examples=["Pending"])


class ProductOwnerSpecification(BaseModel):
    """
    Requirements for the software engineer agent
    """

    product_name: str = Field(examples=["Simple Todo Application"])
    description: str = Field(
        examples=[
            "A web-based application allowing users to manage their daily tasks, including creating, viewing, updating, marking complete, and deleting todo items."
        ]
    )
    requirements: List[Requirement]
    user_stories: List[UserStories]
