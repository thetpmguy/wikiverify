# LLM Integration for WikiVerify

## Overview

The LLM integration provides intelligent filtering and explanation capabilities for WikiVerify agents. It uses cheap LLM models (GPT-4o-mini) to:

1. **Filter false positives** - Determine if a finding is worth reporting
2. **Generate explanations** - Create human-readable descriptions of problems

## Cost

- **Triage**: ~$0.001 per flagged item (GPT-4o-mini)
- **Explanation**: ~$0.001 per finding (GPT-4o-mini)
- **Total**: ~$0.002 per finding

For 1,000 findings per month: ~$2/month

## Setup

1. **Get OpenAI API Key**:
   - Sign up at https://platform.openai.com
   - Create an API key
   - Add to `.env` file: `OPENAI_API_KEY=your_key_here`

2. **Install dependencies** (already in requirements.txt):
   ```bash
   pip install openai
   ```

3. **Enable/Disable LLM**:
   - LLM is enabled by default if `OPENAI_API_KEY` is set
   - To disable: Set `use_llm_triage=False` when initializing agents
   - Or remove `OPENAI_API_KEY` from `.env`

## Usage

### Automatic (Default)

Agents automatically use LLM triage if API key is configured:

```python
# LLM triage enabled automatically
agent = BrokenLinkAgent()
agent.run()
```

### Manual Control

```python
# Disable LLM triage
agent = BrokenLinkAgent(use_llm_triage=False)

# Enable LLM triage
agent = BrokenLinkAgent(use_llm_triage=True)
```

## How It Works

### Triage Layer

When an agent finds a problem:

1. **Basic Check** (no LLM): Agent detects problem (404, retraction, etc.)
2. **LLM Triage** (if enabled): Quick assessment - "Is this worth reporting?"
   - Filters temporary issues
   - Identifies false positives
   - Only reports real problems
3. **Save Finding**: If LLM confirms it's real, save to database

### Explanation Layer

When saving a finding:

1. **Basic Details**: Technical description (e.g., "HTTP 404")
2. **LLM Explanation** (if enabled): Human-readable explanation
   - Context about why it matters
   - Impact on Wikipedia article
   - Clear language for editors

## Example

### Without LLM:
```
Finding: "URL returns 404 error"
```

### With LLM:
```
Finding: "The citation links to a 2019 medical study that is no longer 
available at the original URL. This source supports the claim about 
aspirin's effectiveness. The link may have been moved or the paper 
removed. Editors should verify if an alternative source or archived 
version is available."
```

## Configuration

In `.env`:
```bash
# Required for LLM features
OPENAI_API_KEY=sk-...

# Optional: Use different model
# (Currently hardcoded to gpt-4o-mini for cost efficiency)
```

## Cost Optimization

- Uses **GPT-4o-mini** (cheapest capable model)
- Only processes **flagged items** (not all citations)
- **Short prompts** (max 150 tokens for explanations)
- **Low temperature** (0.1-0.3) for consistent results

## Future Enhancements

- Support for other LLM providers (Claude, Anthropic)
- Configurable model selection
- Batch processing for efficiency
- Caching common explanations
