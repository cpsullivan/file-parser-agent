"""
File Parser Agent - Usage Examples
Demonstrates how to use the API wrapper for document parsing.
"""

import base64
from pathlib import Path
from api_wrapper import FileParserAgent


def example_parse_file():
    """Example: Parse a local file directly."""
    print("\n" + "=" * 50)
    print("Example 1: Parse a local file")
    print("=" * 50)

    agent = FileParserAgent()

    # Parse a PDF file
    result = agent.parse_file("path/to/document.pdf", output_format="json")

    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Parsed successfully!")
        print(f"Size: {result.get('size_bytes', 0)} bytes")


def example_parse_with_tools():
    """Example: Use individual tools for more control."""
    print("\n" + "=" * 50)
    print("Example 2: Use individual tools")
    print("=" * 50)

    agent = FileParserAgent()

    # Read and encode a file
    filepath = Path("path/to/document.docx")
    file_bytes = filepath.read_bytes()
    file_content = base64.b64encode(file_bytes).decode('utf-8')

    # Step 1: Validate the file
    validation = agent.tool_file_reader(
        file_content=file_content,
        filename=filepath.name
    )
    print(f"Validation: {validation}")

    if not validation.get('success'):
        return

    # Step 2: Parse the document
    parsed = agent.tool_parse_document(
        file_content=file_content,
        filename=filepath.name,
        options={'extract_images': True, 'extract_tables': True}
    )
    print(f"Parsed {parsed.get('total_paragraphs', 0)} paragraphs")

    # Step 3: Format as Markdown
    markdown = agent.tool_format_as_markdown(
        parsed_data=parsed,
        include_toc=True
    )
    print(f"Markdown output: {markdown.get('size_bytes', 0)} bytes")

    # Step 4: Save to file
    artifact = agent.tool_create_artifact(
        content=markdown['content'],
        filename="output",
        format="markdown"
    )
    print(f"Saved to: {artifact.get('path')}")


def example_chat_with_agent():
    """Example: Have a conversation with the agent."""
    print("\n" + "=" * 50)
    print("Example 3: Chat with the agent")
    print("=" * 50)

    agent = FileParserAgent()

    # Simple question
    response = agent.chat("What file formats do you support?")
    print(f"Agent: {response}")

    # Parse a file through chat
    filepath = Path("path/to/presentation.pptx")
    if filepath.exists():
        file_bytes = filepath.read_bytes()
        file_content = base64.b64encode(file_bytes).decode('utf-8')

        response = agent.chat(
            user_message="Parse this presentation and give me a summary of each slide.",
            file_content=file_content,
            filename=filepath.name
        )
        print(f"Agent: {response}")


def example_extract_tables():
    """Example: Extract just tables from a document."""
    print("\n" + "=" * 50)
    print("Example 4: Extract tables only")
    print("=" * 50)

    agent = FileParserAgent()

    # Read Excel file
    filepath = Path("path/to/spreadsheet.xlsx")
    file_bytes = filepath.read_bytes()
    file_content = base64.b64encode(file_bytes).decode('utf-8')

    # Extract tables as CSV
    tables = agent.tool_extract_tables(
        file_content=file_content,
        filename=filepath.name,
        output_format="csv"
    )

    if tables.get('success'):
        print(f"Found {tables.get('table_count', 0)} tables")
        print(f"CSV content:\n{tables.get('content', '')[:500]}...")


def example_analyze_image():
    """Example: Analyze an image with AI vision."""
    print("\n" + "=" * 50)
    print("Example 5: Analyze an image")
    print("=" * 50)

    agent = FileParserAgent()

    # Read image file
    image_path = Path("path/to/chart.png")
    image_bytes = image_path.read_bytes()
    image_content = base64.b64encode(image_bytes).decode('utf-8')

    # Analyze as a chart
    analysis = agent.tool_analyze_image(
        image_content=image_content,
        image_format="png",
        analysis_type="chart",
        context="Q4 sales report"
    )

    if analysis.get('enabled'):
        print(f"Description: {analysis.get('description')}")
    else:
        print(f"Note: {analysis.get('note')}")


def example_summarize():
    """Example: Generate a document summary."""
    print("\n" + "=" * 50)
    print("Example 6: Summarize a document")
    print("=" * 50)

    agent = FileParserAgent()

    # Parse a document first
    filepath = Path("path/to/report.pdf")
    file_bytes = filepath.read_bytes()
    file_content = base64.b64encode(file_bytes).decode('utf-8')

    parsed = agent.tool_parse_document(
        file_content=file_content,
        filename=filepath.name
    )

    # Generate summary
    summary = agent.tool_summarize_document(
        parsed_data=parsed,
        summary_length="detailed"
    )

    if summary.get('success'):
        print(f"Summary:\n{summary.get('summary')}")
        print(f"\nStatistics: {summary.get('statistics')}")


def example_programmatic_api():
    """Example: Use with Claude API directly."""
    print("\n" + "=" * 50)
    print("Example 7: Direct API integration")
    print("=" * 50)

    import anthropic

    # Initialize client and agent
    client = anthropic.Anthropic()
    agent = FileParserAgent()

    # Get tool definitions
    tools = agent.get_tools()

    # Make API call with tools
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        tools=tools,
        messages=[{
            "role": "user",
            "content": "I have a PDF file I'd like to parse. What information do you need from me?"
        }]
    )

    print(f"Response: {response.content[0].text}")

    # If Claude wants to use a tool, process it
    if response.stop_reason == "tool_use":
        for block in response.content:
            if block.type == "tool_use":
                result = agent.process_tool_call(block.name, block.input)
                print(f"Tool result: {result}")


# Quick start function
def quick_start():
    """Quick start: Parse a file in one line."""
    print("\n" + "=" * 50)
    print("Quick Start")
    print("=" * 50)

    # One-liner to parse a file
    agent = FileParserAgent()
    result = agent.parse_file("document.pdf", "markdown")
    print(result.get('content', result.get('error')))


if __name__ == "__main__":
    print("File Parser Agent - Examples")
    print("Note: Update file paths before running examples.\n")

    # Uncomment the examples you want to run:

    # example_parse_file()
    # example_parse_with_tools()
    # example_chat_with_agent()
    # example_extract_tables()
    # example_analyze_image()
    # example_summarize()
    # example_programmatic_api()
    # quick_start()

    print("\nUncomment the examples in __main__ to run them.")
