#!/usr/bin/env python3
"""
Image processing example for BelArabyAI SDK.

This example demonstrates comprehensive image processing capabilities:
1. Image analysis and understanding
2. Image editing and manipulation
3. Batch processing
4. Image optimization
5. Visual content extraction
"""

import asyncio
import os

from ba.ba import BASdk
from ba.tools import AgentPressTools


async def main():
    """Main example function."""
    # Get API key from environment variable
    api_key = os.getenv("BELARABYAI_API_KEY")
    if not api_key:
        print("Please set BELARABYAI_API_KEY environment variable")
        return

    # Initialize the client
    print("🚀 Initializing BelArabyAI client...")
    client = BASdk(api_key=api_key)

    # Create an image processing agent
    print("\n🤖 Creating Image Processing Agent...")
    agent = await client.Agent.create(
        name="Image Processing Expert",
        system_prompt="""You are an image processing expert with capabilities in:
        - Image analysis and understanding
        - Image editing and manipulation
        - Batch processing operations
        - Image optimization and compression
        - Visual content extraction and analysis
        - Format conversion and enhancement
        Always provide detailed analysis and maintain image quality.""",
        mcp_tools=[AgentPressTools.SB_VISION_TOOL, AgentPressTools.SB_IMAGE_EDIT_TOOL],
        allowed_tools=["sb_vision_tool", "sb_image_edit_tool"],
    )
    print(f"✅ Agent created with ID: {agent._agent_id}")

    # Create a conversation thread
    print("\n💬 Creating conversation thread...")
    thread = await client.Thread.create("Image Processing Demo")
    print(f"✅ Thread created with ID: {thread._thread_id}")

    # Image processing scenarios
    scenarios = [
        {
            "title": "🔍 Image Analysis",
            "message": """Analyze the following types of images and provide detailed insights:
            1. A landscape photograph - describe composition, colors, lighting, and mood
            2. A portrait photo - analyze facial features, expression, and photographic techniques
            3. A technical diagram - extract and explain the information presented
            4. A chart or graph - interpret the data and trends shown
            5. A product image - describe the product, its features, and marketing appeal

            For each image type, provide:
            - Visual description
            - Technical analysis (resolution, format, quality)
            - Content interpretation
            - Potential improvements or modifications""",
        },
        {
            "title": "✏️ Image Editing",
            "message": """Demonstrate various image editing capabilities:
            1. Basic adjustments: brightness, contrast, saturation, and color balance
            2. Advanced editing: cropping, resizing, rotation, and perspective correction
            3. Creative effects: filters, artistic styles, and color grading
            4. Restoration: noise reduction, sharpening, and artifact removal
            5. Composition: adding text, watermarks, and overlays

            Explain the purpose and impact of each editing technique.""",
        },
        {
            "title": "📊 Batch Processing",
            "message": """Set up batch processing workflows:
            1. Resize multiple images to standard dimensions
            2. Convert image formats (JPEG to PNG, etc.)
            3. Apply consistent filters or effects to a set of images
            4. Optimize images for web use (compression, format selection)
            5. Generate thumbnails and previews

            Provide guidelines for efficient batch processing.""",
        },
        {
            "title": "🎨 Creative Processing",
            "message": """Explore creative image processing:
            1. Artistic style transfer and filters
            2. Color palette extraction and harmonization
            3. Texture analysis and enhancement
            4. Composition improvement suggestions
            5. Creative cropping and framing

            Focus on artistic and aesthetic improvements.""",
        },
        {
            "title": "🔧 Technical Optimization",
            "message": """Optimize images for different use cases:
            1. Web optimization: file size reduction while maintaining quality
            2. Print optimization: resolution and color space considerations
            3. Mobile optimization: responsive image sizing
            4. SEO optimization: alt text and metadata
            5. Accessibility: contrast and readability improvements

            Provide specific recommendations for each use case.""",
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"Scenario {i}: {scenario['title']}")
        print(f"{'='*60}")

        # Add message to thread
        await thread.add_message(scenario["message"])

        # Run the agent
        run = await agent.run(scenario["message"], thread)

        # Stream the response
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()  # New line after response

    # Demonstrate specific image processing techniques
    print(f"\n{'='*60}")
    print("🛠️ Specific Processing Techniques")
    print(f"{'='*60}")

    technique_scenarios = [
        {
            "title": "📐 Geometric Transformations",
            "message": "Explain and demonstrate geometric image transformations: rotation, scaling, skewing, perspective correction, and lens distortion correction.",
        },
        {
            "title": "🎨 Color Processing",
            "message": "Demonstrate advanced color processing: color space conversion, histogram equalization, color grading, and selective color adjustment.",
        },
        {
            "title": "🔍 Feature Detection",
            "message": "Explain feature detection and analysis: edge detection, corner detection, texture analysis, and pattern recognition in images.",
        },
        {
            "title": "📊 Image Statistics",
            "message": "Analyze image statistics: histogram analysis, color distribution, brightness analysis, and quality metrics.",
        },
        {
            "title": "🔄 Format Conversion",
            "message": "Guide through image format conversion: JPEG, PNG, GIF, WebP, TIFF, and BMP. Explain when to use each format.",
        },
    ]

    for scenario in technique_scenarios:
        print(f"\n🛠️ {scenario['title']}")
        await thread.add_message(scenario["message"])

        run = await agent.run(scenario["message"], thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Demonstrate real-world applications
    print(f"\n{'='*60}")
    print("🌍 Real-World Applications")
    print(f"{'='*60}")

    application_scenarios = [
        "Create a workflow for processing product images for an e-commerce website, including standardization, optimization, and thumbnail generation.",
        "Set up an image processing pipeline for social media content, including resizing, format conversion, and quality optimization.",
        "Design a system for processing user-uploaded images, including validation, optimization, and security checks.",
        "Create a workflow for batch processing photographs from a photo shoot, including color correction, retouching, and format standardization.",
        "Design an automated system for processing images for a news website, including resizing, watermarking, and SEO optimization.",
    ]

    for i, scenario in enumerate(application_scenarios, 1):
        print(f"\n🌍 Application {i}: {scenario}")
        await thread.add_message(scenario)

        run = await agent.run(scenario, thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Demonstrate troubleshooting
    print(f"\n{'='*60}")
    print("🔧 Troubleshooting Common Issues")
    print(f"{'='*60}")

    troubleshooting_scenarios = [
        "Images are appearing blurry after resizing. Help me understand the causes and solutions for maintaining image quality.",
        "File sizes are too large for web use. Guide me through optimization techniques to reduce file size while maintaining visual quality.",
        "Colors look different after processing. Explain color space issues and how to maintain color accuracy.",
        "Batch processing is taking too long. Help me optimize the workflow for better performance.",
        "Images are losing quality during format conversion. Explain lossy vs lossless compression and best practices.",
    ]

    for scenario in troubleshooting_scenarios:
        print(f"\n🔧 Troubleshooting: {scenario}")
        await thread.add_message(scenario)

        run = await agent.run(scenario, thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Get processing summary
    print(f"\n{'='*60}")
    print("📊 Image Processing Summary")
    print(f"{'='*60}")

    messages = await thread.get_messages()
    runs = await thread.get_agent_runs()

    print(f"📋 Total processing tasks: {len(messages)}")
    print(f"🏃 Total agent runs: {len(runs)}")

    print("\n🖼️ Image processing capabilities covered:")
    capabilities = [
        "Image Analysis & Understanding",
        "Basic & Advanced Editing",
        "Batch Processing Workflows",
        "Creative Processing",
        "Technical Optimization",
        "Geometric Transformations",
        "Color Processing",
        "Feature Detection",
        "Image Statistics",
        "Format Conversion",
        "E-commerce Applications",
        "Social Media Processing",
        "User Upload Handling",
        "Photo Shoot Processing",
        "News Website Optimization",
    ]

    for capability in capabilities:
        print(f"  ✅ {capability}")

    print("\n📐 Processing techniques demonstrated:")
    techniques = [
        "Brightness & Contrast Adjustment",
        "Color Balance & Saturation",
        "Cropping & Resizing",
        "Rotation & Perspective Correction",
        "Filter Application",
        "Noise Reduction",
        "Sharpening",
        "Histogram Equalization",
        "Edge Detection",
        "Texture Analysis",
        "Quality Metrics",
        "Compression Optimization",
    ]

    for technique in techniques:
        print(f"  - {technique}")

    # Clean up
    print(f"\n🗑️ Cleaning up thread {thread._thread_id}...")
    await client.Thread.delete(thread._thread_id)
    print("✅ Thread deleted")

    print("\n✅ Image processing example completed!")


if __name__ == "__main__":
    asyncio.run(main())
