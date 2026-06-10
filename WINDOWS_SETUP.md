# 🪟 Windows PowerShell Setup Guide

## Quick Start (2 Minutes)

### Method 1: Using PowerShell Script (Easiest)

```powershell
cd multi-agent
.\run_demo.ps1
```

That's it! The script will:
- ✅ Check Python installation
- ✅ Install dependencies automatically
- ✅ Load environment variables
- ✅ Run the demo

### Method 2: Manual Commands

```powershell
# Navigate to the multi-agent directory
cd multi-agent

# Install dependencies (one-time setup)
pip install pydantic requests

# Run the demo
python examples/advanced_multi_agent_demo.py
```

## 🔧 Setup Your API Keys (Optional)

The system works perfectly without API keys using intelligent heuristics. But for AI-powered analysis, create a `.env` file:

```powershell
# Create .env file in multi-agent directory
@"
AI_ML_API_KEY=d7e282ae...
FEATHERLESS_API_KEY=your_featherless_key_here
"@ | Out-File -FilePath .env -Encoding UTF8
```

Or set environment variables directly in PowerShell:

```powershell
$env:AI_ML_API_KEY = "d7e282ae..."
$env:FEATHERLESS_API_KEY = "your_featherless_key"
```

## 📋 System Requirements

- ✅ **Python 3.9+** (You have Python 3.14.0 ✓)
- ✅ **PowerShell 5.0+** (Built into Windows)
- ✅ **Dependencies**: pydantic, requests (auto-installed)

## 🚀 Running the Demo

### Interactive Demo

The demo is interactive and will guide you through each component:

```powershell
python examples/advanced_multi_agent_demo.py
```

Press **Enter** to step through:
1. Orchestrator Agent demonstration
2. Memory Layer capabilities
3. Coordination Agent in action
4. AI-powered Analysis
5. Complete multi-agent pipeline

### Non-Interactive Mode

To run without pausing:

```powershell
# Create a simple test script
python -c "from examples.advanced_multi_agent_demo import demonstrate_orchestrator; demonstrate_orchestrator()"
```

## 🎯 What You'll See

### 1. System Initialization
```
🎯 OrchestratorAgent 'MainOrchestrator' initialized
✅ Registered agent 'PQCAnalysisAgent' with capabilities: ['analysis', 'pqc', 'cryptography']
✅ Registered agent 'PQCCoordinationAgent' with capabilities: ['coordination', 'crisis_management']
```

### 2. Crisis Room Management
```
🏢 CRISIS ROOM INITIALIZED: PQC-CRISIS-ROOM-HSM-01
📋 Incident ID: PQC-FLASH-CRASH-2026
📡 Channels: Network, Security, Infrastructure, Executive
👥 Stakeholders: Security Team, Infrastructure Team, Executive Leadership
🚦 Status: ESCALATED
```

### 3. AI Analysis
```
🔍 Performing AI-powered incident analysis...
✅ Analysis completed: Level 5 (Critical)
💡 Root cause: HSM entropy starvation under peak Kyber-1024 load
💰 Financial exposure: $120,000/minute
```

### 4. Learning & Recommendations
```
🧠 Memory Layer initialized with 3 incidents
🔍 Found 2 similar incidents (top similarity: 0.87)
💡 Recommendations based on historical data:
   1. Apply strategy from incident INC-001 (Confidence: 0.83)
```

## 🛠️ Troubleshooting

### Issue: "python: command not found"

**Solution**: Add Python to PATH or use full path:
```powershell
C:\Python314\python.exe examples/advanced_multi_agent_demo.py
```

### Issue: "ModuleNotFoundError: No module named 'pydantic'"

**Solution**: Install dependencies:
```powershell
pip install pydantic requests
```

### Issue: Unicode encoding errors

**Solution**: Already fixed! The demo now handles Windows encoding automatically.

### Issue: Execution policy prevents running scripts

**Solution**: Allow script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📊 Testing Individual Components

### Test Coordination Agent Only

```powershell
python -c @"
import sys
sys.path.insert(0, '.')
from adapters.band_client import InMemoryBandClient
from agents.coordination_agent import PQCCoordinationAgent
from services.enhanced_ai_client import EnhancedAIClient
from messages.models import PQCIncidentDetected
from datetime import datetime, timezone

band = InMemoryBandClient()
ai_client = EnhancedAIClient()
coord_agent = PQCCoordinationAgent('Coordinator', band, ai_client)

incident = PQCIncidentDetected(
    incident_id='TEST-001',
    source='TestSystem',
    description='HSM entropy degradation detected',
    timestamp=datetime.now(timezone.utc),
    severity_initial='critical'
)

band.subscribe('pqc.incident.detected', coord_agent.handle_message)
band.publish('pqc.incident.detected', {
    'source': 'Test',
    'topic': 'pqc.incident.detected',
    'payload': incident.model_dump()
})

print('Crisis rooms:', coord_agent.get_active_crisis_rooms())
"@
```

### Test Memory Layer Only

```powershell
python -c @"
import sys
sys.path.insert(0, '.')
from services.memory_layer import MemoryLayer

memory = MemoryLayer('test_memory')
memory.store_incident({
    'incident_id': 'TEST-001',
    'description': 'HSM entropy degradation',
    'severity': 'critical',
    'outcome': 'resolved'
})

similar = memory.find_similar_incidents('HSM issues', limit=5)
print(f'Found {len(similar)} similar incidents')
print('Statistics:', memory.get_statistics())
"@
```

### Test Orchestrator Only

```powershell
python -c @"
import sys
sys.path.insert(0, '.')
from adapters.band_client import InMemoryBandClient
from agents.orchestrator_agent import OrchestratorAgent

band = InMemoryBandClient()
orchestrator = OrchestratorAgent('Orchestrator', band)

orchestrator.register_agent(
    'TestAgent',
    capabilities=['test'],
    topics=['test.topic'],
    max_concurrent_tasks=5
)

status = orchestrator.get_system_status()
print('System status:', status)
"@
```

## 🎨 PowerShell Tips

### Colorful Output

PowerShell supports colored output. The demo uses emojis and formatting for better visualization.

### Running in Background

```powershell
Start-Job -ScriptBlock { cd C:\Users\TRETEC\Desktop\multi-agent; python examples/advanced_multi_agent_demo.py }
```

### Logging Output

```powershell
python examples/advanced_multi_agent_demo.py | Tee-Object -FilePath demo_output.log
```

## 📁 File Structure

```
multi-agent/
├── run_demo.ps1              # PowerShell launcher script
├── examples/
│   └── advanced_multi_agent_demo.py  # Main demo
├── agents/
│   ├── coordination_agent.py  # Crisis coordination
│   ├── orchestrator_agent.py  # Task orchestration
│   └── analysis_agent.py      # Incident analysis
├── services/
│   ├── memory_layer.py        # Learning & memory
│   ├── enhanced_ai_client.py  # AI integration
│   └── monitoring_dashboard.py # Monitoring
└── README_ADVANCED.md         # Full documentation
```

## 🎯 Next Steps

1. **Run the demo**: `.\run_demo.ps1`
2. **Explore the code**: Check out the agents and services
3. **Read documentation**: See README_ADVANCED.md
4. **Test components**: Try individual component tests above
5. **Customize**: Adapt for your use case

## 💡 Pro Tips

1. **Use Windows Terminal** for better Unicode support
2. **Enable UTF-8** in PowerShell: `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`
3. **Create shortcuts** for frequently used commands
4. **Use VS Code terminal** for integrated experience

## 🏆 You're Ready!

The system is now running on your Windows machine with PowerShell. Enjoy exploring the advanced multi-agent system!

---

**Made with ❤️ for Windows PowerShell users**