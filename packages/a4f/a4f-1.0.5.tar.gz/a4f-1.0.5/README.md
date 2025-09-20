
# A4F Python SDK

[![PyPI version](https://badge.fury.io/py/a4f.svg)](https://badge.fury.io/py/a4f)
[![Python](https://img.shields.io/pypi/pyversions/a4f.svg)](https://pypi.org/project/a4f/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/a4f)](https://pepy.tech/project/a4f)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/a4f)](https://pypi.org/project/a4f/)
[![Type Checker: mypy](https://img.shields.io/badge/type%20checker-mypy-blue.svg)](https://github.com/python/mypy)

The official **Python SDK for A4F** — your unified AI gateway.  
Seamlessly access **hundreds of AI models** across providers through a single, powerful API.

---

## 🚀 Installation

Install via pip:

```bash
pip install a4f
```
> ✅ Requires **Python 3.8+**

---

## 🔄 Quick Start

1. **Sign up & get API key** at [A4F.co](https://a4f.co)
2. **Install the SDK**

   ```bash
   pip install a4f
   ```
3. **Initialize the client**

   ```python
   from a4f import A4F
   client = A4F(api_key="your_api_key")
   ```
4. **Pick your model** (e.g. GPT, Claude, Gemini, Qwen, etc.)
5. **Start making requests!**
    ```python
    response = client.chat.create(
        model="provider-3/gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain quantum computing."}
        ]
    )

    print(response.choices[0].message.content)
    ```

---

## 🔑 Authentication

Set your API key:

```python
# In code
client = A4F(api_key="your_api_key")

```

---

## 📖 Usage Examples

### 💬 Chat Completions

```python
response = client.chat.create(
    model="provider-3/gpt-5-nano",
    messages=[{"role": "user", "content": "What is machine learning?"}]
)
```

Streaming mode:

```python
stream = client.chat.create(
    model="provider-3/gpt-5-nano",
    messages=[
        {"role": "user", "content": "Count from 1 to 5"}
    ],
    stream=True
)
for chunk in stream:
    if chunk.has_content:
        print(chunk.content, end="", flush=True)
```
---

### 🖼️ Image Generation

```python
image = client.images.generate(
    model="provider-4/imagen-4",
    prompt="A serene mountain landscape at sunset",
    size="1024x1024"
)
```

### Image editing comming soon

<!-- ```python
with open("image.png", "rb") as img, open("mask.png", "rb") as mask:
    result = client.images.edit(
        image=img,
        mask=mask,
        model="provider-3/flux-kontext-pro",
        prompt="Add a flying bird"
    )
``` -->

---

<!-- ### 🎙️ Audio Processing

```python
# Speech-to-text
with open("audio.mp3", "rb") as f:
    transcript = client.audio.transcriptions.create(
        model="provider-3/whisper-1",
        file=f,
        language="en"
    )

# Text-to-speech
speech = client.audio.speech.create(
    model="provider-3/gemini-2.5-flash-preview-tts",
    input="Hello world!",
    voice="alloy"
)
speech.stream_to_file("output.mp3")
```

--- -->

### 🔎 Embeddings

```python
embedding = client.embeddings.create(
    model="provider-6/qwen3-embedding-4b",
    input="The quick brown fox jumps over the lazy dog"
)
```

---

## ⚙️ Advanced Configuration

```python
client = A4F(
    api_key="your_api_key",
    timeout=30,        # custom timeout
    max_retries=3,     # retry failed requests
)
```

---

## ❌ Error Handling

```python
from a4f import A4F

client = A4F(api_key="your_api_key")

try:
    response = client.chat.create(
        model="provider-3/gpt-5-nano",
        messages=[{"role": "user", "content": "Hello!"}]
    )
except Exception as e:
        print(f"Error: {e}\n")
```

---


## 🌐 What is A4F?

[A4F.co](https://a4f.co/?utm_source=python-sdk) is a **revolutionary AI gateway** that simplifies interaction with multiple AI providers. Instead of integrating with OpenAI, Anthropic, Google, and others separately, A4F provides **one consistent API** to access them all.  

This makes development faster, cheaper, and more reliable.

---

## ✨ Why A4F?

- 🌐 **Unified API** – One interface for hundreds of AI models  
- 💰 **Free Tier** – Start building with no upfront costs  
- ⚡ **High Availability** – Failover & load balancing built-in  
- 💸 **Cost Optimization** – Smart routing & price-performance tuning  
- 🔒 **Privacy Controls** – Decide which provider handles your data  
- 🚀 **Production-Ready** – Enterprise-grade scalability and support  

---

## 🌟 Key Features

| Feature            | Description                                | Benefits                                |
|--------------------|--------------------------------------------|-----------------------------------------|
| **Unified API**    | Consistent interface for all models        | Less complexity, faster dev cycles       |
| **Model Variety**  | Access to 100+ LLMs & AI services          | Flexibility for any use case             |
| **High Availability** | Auto failover & load balancing          | Better uptime & resilience               |
| **Cost Management**| Smart routing & pricing options            | Control spending without losing quality  |
| **Privacy Controls** | Granular provider selection              | Security & compliance ensured            |
| **Streaming**      | Real-time responses across endpoints       | Smooth user experiences                  |
| **Type Safety**    | Strong typing & mypy support               | Catch bugs early, better IDE hints       |

---

## 📧 Support & Resources

* [📘 Official Docs](https://a4f.co/docs)
* [🚀 Changelog](https://www.a4f.co/changelog)
* [💬 Telegram Community](https://t.me/DDC_Group)
* [🎮 Discord Community](https://discord.gg/9dK2xGFsfw)

---

## 🤝 Enterprise Support

A4F offers enterprise-grade benefits:

* Dedicated account managers
* SLA guarantees
* Priority support response times
* Custom privacy configurations
* Volume-based pricing

📩 Contact our [Owner](http://t.me/Sreejan07) for details.

---

Built with ❤️ by the [A4F Team](https://a4f.co) — *Your Unified AI Gateway*.