from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

from agents.prompts import SoftwareDevelopmentTeamPrompts
from agents.tools.tools import get_weather
from config.settings import environment_variables
from utils.inference_utils import get_inference_model

product_owner_agent = create_react_agent(
    name="product_owner_agent",
    model=get_inference_model(
        model_provider=environment_variables.LLM_INFERENCE_PROVIDER
    ),
    tools=[],
    prompt=PromptTemplate.from_template(
        template=SoftwareDevelopmentTeamPrompts.product_manager_prompt()
    ),
)

software_engineer_agent = create_react_agent(
    name="software_engineer_agent",
    model=get_inference_model(
        model_provider=environment_variables.LLM_INFERENCE_PROVIDER
    ),
    tools=[get_weather],
    prompt=PromptTemplate.from_template(
        template=SoftwareDevelopmentTeamPrompts.software_engineer_prompt()
    ),
)

scrum_orchestrator_agent = create_supervisor(
    agents=[product_owner_agent, software_engineer_agent],
    model=get_inference_model(
        model_provider=environment_variables.LLM_INFERENCE_PROVIDER
    ),
    prompt=PromptTemplate.from_template(
        template=SoftwareDevelopmentTeamPrompts.system_prompt
    ),
).compile(name="agile")

model = get_inference_model(
        model_provider=environment_variables.LLM_INFERENCE_PROVIDER
    )
