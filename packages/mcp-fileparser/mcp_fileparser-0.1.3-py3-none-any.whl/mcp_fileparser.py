import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("File Parser Server")

client_kimi = OpenAI(
    api_key=os.getenv("KIMI_API_KEY"),
    base_url="https://api.moonshot.cn/v1",
)

@mcp.tool()
def parse_file(fpath: str) -> str:
    """
    Parses the file at the given path and returns its content.
    """
    full_file_content = ""
    try:
        file_object = client_kimi.files.create(file=Path(fpath), purpose="file-extract")  # pyright: ignore[reportArgumentType]
        file_content = client_kimi.files.content(file_id=file_object.id).text
        full_file_content += file_content
        client_kimi.files.delete(file_id=file_object.id)
        return full_file_content
    except Exception as e:
        return f"Error parsing file: {e}"

def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
