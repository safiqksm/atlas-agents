atlas_v01_anthropic.py—A minimal tool-calling loop using the
Anthropic SDK (input_schema instead of OpenAI’s parameters schema).

2. atlas_v01_streaming.py—Server-Sent Events implementation to
stream the LLM’s thought process and tool execution in real-time.

3. atlas_v01_plan_and_execute.py—Re-implementation of ReAct into
a Plan-and-Execute pattern, isolating reasoning from execution.

python online/atlas_v01_anthropic.py "What is the Model Context Protocol?"

python online/atlas_v01_plan_and_execute.py "Research the top 3 AI agent frameworks"

python online/atlas_v01_streaming.py "What is the Model Context Protocol?"

python online/atlas_v01_anthropic_fixed.py "What is the Model Context Protocol?"

python online/atlas_v01_streaming_fixed.py "What is the Model Context Protocol?"
