# AI Audit Trail SDK - Python

Drop-in SDK for logging AI/ML decisions with compliance tracking. Get GDPR and EU AI Act compliant audit trails in under 15 minutes.

## Installation

```bash
pip install ai-audit-sdk
```

## Quick Start

```python
from ai_audit_sdk import AuditLogger
import openai

```python
# Initialize the logger with your API key
logger = AuditLogger(api_key="your_api_key")
```

For development and testing, use your sandbox API key:
```python
# Development/Testing with sandbox tenant
logger = AuditLogger(api_key="your_sandbox_api_key")
```

# Your existing OpenAI code
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello, world!"}]
)

# Log the decision for compliance
logger.log_decision(
    input_text="Hello, world!",
    output_text=response.choices[0].message.content,
    model_name="gpt-4",
    metadata={
        "user_id": "user123",
        "session_id": "session456"
    }
)
```

## Features

- **Asynchronous Logging**: Won't slow down your application
- **Compliance Ready**: GDPR Article 22 and EU AI Act support
- **Multi-Model Support**: Works with any AI/ML model
- **Secure**: API key authentication with encrypted transmission
- **Reliable**: Built-in error handling and timeout management

## API Reference

### AuditLogger

Main class for logging AI decisions.

```python
logger = AuditLogger(api_key="your_key")
```

**Production:**
```python
logger = AuditLogger(api_key="prod_api_key_xxx")
```

**Development/Testing:**
```python
logger = AuditLogger(api_key="sandbox_api_key_xxx")
```

> **Note**: All traffic goes through the production infrastructure at `https://explainableai.azurewebsites.net`. Tenant isolation is handled via API keys, not URLs.

#### Methods

##### `log_decision(input_text, output_text, ...)`

Log an AI decision asynchronously (recommended).

```python
logger.log_decision(
    input_text="The input prompt",
    output_text="The AI response",
    model_name="gpt-4",  # optional, defaults to 'unknown'
    metadata={  # optional
        "user_id": "user123",
        "session_id": "session456",
        "tags": ["production", "chat"]
    },
    confidence=0.95,  # optional, 0.0 to 1.0
    response_time=1200,  # optional, in milliseconds
    provider="openai",  # optional
    model_version="2024-02-01",  # optional
    risk_level="low",  # optional: 'low', 'medium', 'high'
    prompt_tokens=100,  # optional
    completion_tokens=50,  # optional
    total_tokens=150,  # optional
    cost_micros=1000,  # optional, cost in millionths of currency unit
    external_ref="req_123",  # optional, your internal reference
    data_subject_id="user_123",  # optional, for GDPR compliance
    lawful_basis="consent",  # optional, GDPR lawful basis
    automated_decision=True,  # optional, GDPR Article 22
    redact_pii=False,  # optional, redact PII from stored data
    priority="normal"  # optional: 'low', 'normal', 'high'
)
```

Log an AI decision asynchronously (recommended).

**Parameters:**
- `input_text` (str): The input prompt or data
- `output_text` (str): The AI model's output
- `model_name` (str): Name of the AI model used
- `metadata` (dict): Additional context (user_id, session_id, etc.)
- `confidence` (float): Model confidence score (0.0 to 1.0)
- `response_time` (int): Response time in milliseconds

##### `log_decision_sync(...)` 

Same as `log_decision()` but blocks until complete. Returns `True` if successful.

### Simple Function

For one-off logging:

```python
from ai_audit_sdk import log_ai_decision

log_ai_decision(
    api_key="your_key",
    input_text="prompt",
    output_text="response",
    model_name="gpt-4"
)
```

## Configuration

Set your API key as an environment variable:

```bash
export AI_AUDIT_API_KEY="your_api_key"
```

Then use it in your code:

```python
import os
from ai_audit_sdk import AuditLogger

logger = AuditLogger(api_key=os.getenv("AI_AUDIT_API_KEY"))
```

## Error Handling

The SDK uses fire-and-forget async logging by default. Errors are logged to stdout but won't crash your application.

For critical applications, use synchronous logging:

```python
success = logger.log_decision_sync(input_text, output_text)
if not success:
    # Handle logging failure
    print("Failed to log decision")
```

## Examples

### OpenAI Integration

```python
import openai
from ai_audit_sdk import AuditLogger

logger = AuditLogger(api_key="your_audit_key")
client = openai.OpenAI(api_key="your_openai_key")

def get_ai_response(prompt, user_id):
    start_time = time.time()
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_time = int((time.time() - start_time) * 1000)
    
    # Log for compliance
    logger.log_decision(
        input_text=prompt,
        output_text=response.choices[0].message.content,
        model_name="gpt-4",
        metadata={"user_id": user_id},
        response_time=response_time
    )
    
    return response.choices[0].message.content
```

### Context Manager

```python
with AuditLogger(api_key="your_key") as logger:
    logger.log_decision("input", "output", "model")
    # Logger automatically closes when exiting the context
```

## License

MIT License