# Passing Data to the Agent

LLMling agents can handle various types of input data in their `run()` and `run_stream()` methods. The actual support depends on the model and provider capabilities.

## Basic Text Input

The simplest form is passing text strings:

```python
await agent.run("Analyze this text")
await agent.run("First message", "Second message")  # Multiple prompts combined
```

## Path-Like Objects

The agent automatically handles path-like objects and converts them based on type:

```python
# Local files
await agent.run(Path("document.pdf"))
await agent.run(UPath("data/image.png"))

# Any UPath-supported protocol
await agent.run(UPath("s3://bucket/document.pdf"))
await agent.run(UPath("https://example.com/image.jpg"))
```

## Images

Images can be passed in several ways:

```python
# As PIL Image
from PIL import Image
img = Image.open("photo.jpg")
await agent.run(img)

# As path to image file
await agent.run(Path("photo.jpg"))

# As base64 or URL content
from llmling_agent_config import ImageBase64Content, ImageURLContent
img_content = ImageBase64Content.from_bytes(binary_data)
await agent.run(img_content)
```

## PDF Documents

PDF documents are supported by some models (e.g., Claude 3):

```python
await agent.run(Path("document.pdf"))
await agent.run("Analyze this:", Path("document.pdf"))
```

## Mixed Content

You can combine different types of input:

```python
await agent.run(
    "Analyze this image:",
    Path("chart.png"),
    "And compare it with this document:",
    Path("report.pdf")
)
```

## Model Support

Content type support depends on the model and provider:

```python
# Check vision support
if await agent.provider.supports_feature("vision"):
    await agent.run(Path("image.jpg"))

# Check PDF support
if await agent.provider.supports_feature("pdf"):
    await agent.run(Path("document.pdf"))
```

## Streaming Response

The same input types work with streaming:

```python
async with agent.run_stream(
    "Describe this image:",
    Path("photo.jpg")
) as stream:
    async for chunk in stream:
        print(chunk, end="")
```

## Provider-Specific Features

Some providers may support additional content types:

```python
# Example: Provider supporting audio input
if await agent.provider.supports_feature("audio"):
    await agent.run(Path("recording.mp3"))

# Example: Provider supporting video input
if await agent.provider.supports_feature("video"):
    await agent.run(Path("clip.mp4"))
```

## Input Conversion

The agent automatically converts inputs to the appropriate format for each provider:

- Paths are read and converted to base64 or URLs as needed
- Images are resized/encoded according to model requirements
- Multiple inputs are combined with appropriate separators
- Provider-specific content formats are generated

You rarely need to handle these conversions manually - just pass the raw inputs and let the agent handle the details.

## Response Types

Depending on the input, responses may include:

- Text analysis of documents
- Image descriptions
- Comparisons between different content types
- Extracted information in structured format

For structured output, use `StructuredAgent`:

```python
from pydantic import BaseModel

class ImageAnalysis(BaseModel):
    description: str
    objects: list[str]
    sentiment: str

agent = StructuredAgent[None, ImageAnalysis](base_agent)
result = await agent.run(Path("photo.jpg"))
print(result.content.objects)  # List of detected objects
```

This handling of multiple content types, combined with automatic conversion and provider-specific support checks, makes it easy to work with rich input data while maintaining a clean API.
