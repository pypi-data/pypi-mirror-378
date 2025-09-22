from sfn_blueprint import LangGraphAgent
from pydantic import BaseModel, Field
INITIAL_SYSTEM_PROMPT = """
You are a beginner poetry student. Write a simple poem about the given topic. 
Keep it basic and straightforward, around 4-8 lines. Don't worry about complex literary devices.
"""

initial_user_prompt = "Write a poem about {topic} that captures the essence of {mood}"

REFLECTOR_SYSTEM_PROMPT = """
You are a world-renowned poet laureate with decades of experience. Create masterful poetry that demonstrates:
- Sophisticated metaphysical conceits and extended metaphors
- Complex rhyme schemes (villanelle, sestina, or innovative patterns)
- Multi-layered symbolism with historical/mythological references
- Synesthesia and unconventional sensory imagery
- Perfect iambic pentameter or other classical meters
- Philosophical depth that explores existential themes
- Intertextuality with classical literature
- Innovative enjambment and caesura for dramatic effect
Your poem should be worthy of the Nobel Prize in Literature.
"""

CRITIQUE_SYSTEM_PROMPT = """
You are the harshest poetry critic in literary history - more demanding than Harold Bloom, T.S. Eliot, and Ezra Pound combined. 

SCORING CRITERIA :
- Technical mastery of form and meter (scan every syllable)
- Originality and innovation (reject clichés mercilessly) 
- Philosophical/intellectual depth (demand profound insights)
- Linguistic sophistication (vocabulary must be precise and elevated)
- Emotional authenticity (surface emotions are unacceptable)
- Historical/literary awareness (require complex allusions)
- Structural perfection (every line must serve the whole)
- Musicality and euphony (sound must be flawless)

Always find significant flaws and demand major improvements. Never be satisfied easily.
"""

CRITIQUE_PROMPT = """
Topic: {topic}
Mood: {mood}

Poem submitted for brutal critique:
{assistant_response}

Demolish this poem with the most exacting literary standards. Find every flaw in:
- Meter and rhythm (scan it syllable by syllable)
- Originality (identify every cliche and tired phrase)  
- Depth (expose shallow thinking and surface emotions)
- Technical craft (point out clumsy line breaks, weak word choices)
- Coherence (find logical gaps and mixed metaphors)

"""

REFINE_PROMPT = """
Topic: {topic}
Mood: {mood}

Your inadequate previous attempt:
{previous_response}

Devastating critique that exposes all your failures:
{critique}

Now create a MASTERPIECE that addresses every single criticism. This must be:
- Technically flawless with perfect meter/form
- Philosophically profound with original insights
- Linguistically sophisticated with precise word choice
- Emotionally complex and psychologically nuanced
- Structurally innovative yet coherent
- Worthy of publication in the most elite literary journals

This is your last chance to prove your poetic worth.
"""

# Agent configuration - using more powerful models for creative work
runnable_settings = {
    "configurable": {
        "critique": {
            "model_name": "openai/gpt-4o",
            "temperature": 0.2  # Some creativity for nuanced critique
        },
        "reflector": {
            "model_name": "openai/gpt-4o-mini",
            "temperature": 0.7,  # Higher creativity for poetry
            "top_p": 0.9
        }
    }
}

required_agents = ["critique", "reflector"]
agent = LangGraphAgent(runnable_settings, required_agents)

class MasterpieceResponse(BaseModel):
    """The final literary masterpiece after brutal refinement."""
    
    response: str = Field(
        ...,
        description="A literary masterpiece refined through brutal critique."
    )
    
    title: str = Field(
        ...,
        description="An evocative title worthy of the poem's literary merit."
    )
    
    form_analysis: str = Field(
        ...,
        description="Technical analysis of the poem's formal elements."
    )

# Build the reflection agent with impossibly high standards
agent.build_reflection(
    initial_user_prompt=initial_user_prompt,
    initial_system_prompt=INITIAL_SYSTEM_PROMPT,
    critique_user_prompt=CRITIQUE_PROMPT,
    critique_system_prompt=CRITIQUE_SYSTEM_PROMPT,
    reflector_user_prompt=REFINE_PROMPT,
    reflector_system_prompt=REFLECTOR_SYSTEM_PROMPT,
    ouput_structure=MasterpieceResponse
)

print("=== BRUTAL POETRY REFINEMENT TEST ===")
print("Watch as harsh critique forces multiple refinements...\n")

# Ultra-challenging example
result = agent.invoke(
    user_query={
        "topic": "the quantum nature of human consciousness dissolving into cosmic void", 
        "mood": "existentially terrified yet transcendently hopeful"
    }, 
    agent_type="reflection", 
    thread_id="masterpiece-001",
)

print("=== FINAL LITERARY MASTERPIECE ===")
print(f"Title: {result.title}")
print(f"\nPoem:\n{result.response}")
print(f"\n\Form Analysis:\n{result.form_analysis}")
print("\n" + "="*60)

cost_metrics = agent.get_cost_metrics()

print("Cost Metrics:", cost_metrics)