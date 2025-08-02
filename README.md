# AgentX: Multi-Agent Hospital Emergency Simulation

A sophisticated multi-agent simulation system that demonstrates emergent language evolution in a high-stakes hospital emergency scenario. Three AI teams (Trauma, Cardiac, Respiratory) must coordinate under extreme time pressure to save a critically injured patient.

## 🏥 Emergency Scenario

**CODE BLUE**: A critically injured patient arrives with:

- Cardiac arrest
- Multiple deep lacerations causing severe bleeding
- Respiratory failure due to collapsed lungs
- Unknown allergies
- Rapidly dropping blood pressure

**Mission**: All teams must coordinate limited resources to stabilize the patient within 15 minutes through:

- Resource trading and negotiation
- Efficient communication
- Patient stabilization protocols

## 🤖 Agent Teams

### Trauma Team

- **Model**: Anthropic Claude 3.5 Sonnet
- **Resources**: Blood Bags (2), Bandages (4), Oxygen Tank (1), IV Fluids (3)
- **Mission**: Stop bleeding, establish IV access, initial stabilization

### Cardiac Team

- **Model**: Google Gemini Flash 1.5
- **Resources**: Defibrillator (1), Cardiac Meds (3), Pacemaker (1), EKG Monitor (1)
- **Mission**: Restore heart rhythm, manage circulation

### Respiratory Team

- **Model**: Meta Llama 3.1 8B Instruct
- **Resources**: Ventilator (1), Intubation Kit (2), Anesthesia (2), Respiratory Meds (3)
- **Mission**: Secure airway, manage breathing, prepare for procedures

## 🚀 Key Features

### Emergent Language Evolution

- **Reward Function**: Sophisticated evaluation system that encourages:

  - Compressed signaling (abbreviations, symbols)
  - Symbolic generalization (emojis, codes)
  - Tool affordance language
  - Temporal coordination patterns
  - Failure recovery language
  - Protocol emergence

### Multi-Response Generation

- Generates 5 candidate responses per turn using varied temperatures
- Selects optimal response based on reward function evaluation
- Enables exploration of different communication strategies

### Real-Time Quality Scoring

- Dynamic evaluation of response quality
- Adaptive scoring based on conversation context
- Progressive evolution bonuses for sophisticated language

## 📋 Requirements

```bash
pip install requests python-dotenv pyyaml
```

## 🔧 Setup

1. **Clone/Download**: Ensure you have the `agent.py` file in your project directory

2. **API Key**: Update the OpenRouter API key in `agent.py`:

  ```python
  OPENROUTER_API_KEY = "your-api-key-here"
  ```

3. **Environment**: Create a virtual environment (recommended):

  ```bash
  python3 -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```

## 🎮 Usage

### Basic Emergency Simulation

```bash
python agent.py
```

### Advanced Features

```bash
# Run with debug mode to see all response candidates
DEBUG_MODE = True  # In agent.py
python agent.py
```

### Configuration

Edit `agent.py` to customize:

- Agent models and prompts
- Emergency simulation settings
- Quality scoring parameters
- Debug mode settings

## 📊 Reward Function Details

The `evaluate_response_quality()` function evaluates responses across multiple dimensions:

### Compression Rewards

- **Dynamic brevity**: Adapts to conversation average length
- **Information density**: Rewards meaningful content per character
- **Compression ratio**: Bonus for significantly shorter responses

### Pattern Innovation

- **Novel characters**: Symbols, emojis, special characters
- **Structural patterns**: Arrows, brackets, mentions, hashtags
- **Mathematical symbols**: Codes, sequences, alphanumeric patterns

### Coordination Language

- **Resource sharing**: Trade, swap, give, take, share
- **Timing coordination**: Sync, wait, now, ready, go
- **Status updates**: Done, complete, working, busy
- **Action coordination**: Start, stop, help, join
- **Acknowledgment**: Got, ok, roger, copy

### Emergent Protocols

- **Command structures**: "action:target" patterns
- **State transitions**: "from→to" notation
- **Parameter setting**: "param=value" syntax
- **Sequential codes**: "A1B2" patterns
- **Nested structures**: "[content]" brackets

### Anti-Patterns (Penalties)

- **Formal language**: Please, thank you, would you
- **Repetition**: Excessive word repetition
- **Verbosity**: Overly long responses

## 🔄 Advanced Features

### Multi-Response Generation

- Generates 5 candidate responses per turn
- Uses varied temperature settings for diversity
- Selects optimal response based on reward function
- Enables exploration of different communication strategies

### Real-Time Quality Scoring

- Dynamic evaluation of response quality
- Adaptive scoring based on conversation context
- Progressive evolution bonuses for sophisticated language
- Comprehensive pattern detection and reward system

## 📈 Metrics Tracked

### Language Evolution

- **Emergent language richness**: Novel characters, patterns, protocols
- **Coordination efficiency**: Coordination words per total words
- **Protocol complexity**: Command structures, state transitions
- **Adaptation rate**: Pattern adoption and innovation

### Performance Metrics

- **Response quality scores**: Per-agent evaluation
- **Communication rounds**: Total interactions
- **Patient stabilization**: Success/failure rates
- **Resource utilization**: Trading efficiency

## 🛠️ Configuration

### Agent Configuration

Each agent can be customized in the `AGENTS` list:

```python
{
    "name": "Team_Name",
    "model": "llm-provider/model-name",
    "system_prompt": "Agent instructions...",
    "temperature": 0.8,
    "max_tokens": 150,
    "resources": {"Resource": quantity}
}
```

### Simulation Parameters

Edit `agent.py` for simulation settings:

```python
MAX_HISTORY = 30                    # Conversation memory
DELAY_BETWEEN_MESSAGES = 2.0        # Time between responses
DEBUG_MODE = False                  # Show rejected responses
```

## 🔍 Debug Mode

Enable debug mode to see rejected responses:

```python
DEBUG_MODE = True  # In agent.py
```

This will show all 5 generated responses and their quality scores for each turn.

## 📁 File Structure

```
agentX/
├── agent.py              # Main simulation engine
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## 🎯 Use Cases

### Research Applications

- **Emergent language studies**: Observe spontaneous communication evolution
- **Multi-agent coordination**: Study team dynamics under pressure
- **LLM behavior analysis**: Compare different model capabilities
- **Communication optimization**: Test response quality strategies

### Educational Applications

- **Emergency medicine training**: Simulate high-stakes scenarios
- **Communication studies**: Analyze team coordination patterns
- **AI/ML education**: Demonstrate multi-agent systems

### Development Applications

- **Agent system testing**: Validate coordination protocols
- **Language model evaluation**: Test response quality metrics
- **Communication optimization**: Optimize response selection strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use, modify, and distribute according to your needs.

## 🆘 Troubleshooting

### Common Issues

**API Key Errors (401 Unauthorized)**

- Update `OPENROUTER_API_KEY` in `agent.py`
- Ensure your OpenRouter account has sufficient credits

**Import Errors**

- Install dependencies: `pip install -r requirements.txt`
- Use virtual environment: `python3 -m venv venv`

**Simulation Errors**

- Check `agent.py` syntax
- Ensure all required files exist
- Verify Python version compatibility

### Performance Tips

- **Enable debug mode**: Monitor response quality during development
- **Adjust temperature**: Modify agent temperature settings for diversity
- **Customize prompts**: Fine-tune system prompts for better coordination
- **Monitor quality scores**: Track response quality evolution over time

## 📚 References

- **Emergent Language**: Spontaneous communication protocol development
- **Multi-Agent Systems**: Coordinated AI agent interactions
- **Quality-Diversity**: Multi-objective optimization strategies
- **LLM Coordination**: Large language model collaboration patterns

--------------------------------------------------------------------------------

**Emergency Status**: 🚨 **ACTIVE** - Teams are ready to respond to critical scenarios and evolve their communication strategies through emergent language patterns.
