from typing import List, Dict, Any

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    """
    Requirement required for software engineer agent to ensure
    that all features have been completed.
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


class TechnicalNotes(BaseModel):
    frontend: str = Field(
        examples=[
            "Consider using a modern JavaScript framework (e.g., React, Vue, Angular) or vanilla JS for a simple SPA. Responsive design is key."
        ]
    )
    backend: str = Field(
        examples=[
            "For initial development and local persistence, client-side storage (e.g., LocalStorage, IndexedDB) can be used. For future scalability, a simple REST API with a database (e.g., Node.js with Express and a NoSQL DB like MongoDB or a SQL DB like PostgreSQL) would be needed."
        ]
    )
    datamodel: Dict[Any, Any] = Field(
        examples=[
            {
                "TodoItem": {
                    "id": "UUID",
                    "title": "string",
                    "description": "string (optional)",
                    "dueDate": "date (optional)",
                    "priority": "enum (Low, Medium, High) (optional)",
                    "isComplete": "boolean (default: false)",
                    "createdAt": "timestamp",
                }
            }
        ]
    )


class NextSteps(BaseModel):
    instruction_to_software_engineer: str = Field(
        examples=[
            "Software Engineer, please begin by setting up the basic project structure and implementing the core UI components for displaying a list of todo items. Focus on 'REQ-002: View All Todo Items' and 'REQ-001: Create Todo Item' first, with client-side persistence (e.g., LocalStorage) as the initial data store. Once the UI for viewing and creating is functional, we can move to editing and deleting."
        ]
    )
    initial_tasks: List[str] = Field(
        examples=[
            "Set up a new project (e.g., React/Vue/Angular CLI or simple HTML/CSS/JS).",
            "Design and implement the main Todo List component to display items.",
            "Design and implement the 'Add New Todo' form component.",
            "Implement client-side data storage using LocalStorage for persistence.",
            "Develop the logic for creating and adding a new todo item to the list, saving it to LocalStorage.",
            "Ensure basic validation for the todo title (non-empty).",
        ]
    )
    current_progress: str = Field(
        examples=["No requirements are currently finished. All tasks are pending."]
    )


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
    technical_notes: TechnicalNotes
    next_steps: NextSteps
