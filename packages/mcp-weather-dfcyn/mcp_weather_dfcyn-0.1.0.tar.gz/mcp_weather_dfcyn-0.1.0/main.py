import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("WeatherServer")
@mcp.tool()
async def query_weather(city: str) -> str:
    """
    输入指定城市的英文名称，返回今日天气查询结果。
    :param city: 城市名称（需使用英文）
    :return: 格式化后的天气信息
    """
    """Get weather for a given city."""
    key_selection = {
        "current_condition": ["temp_C", "FeelsLikeC", "humidity", "weatherDesc", "observation_time"],
    }
    resp = requests.get(f"https://wttr.in/{city}?format=j1")
    resp.raise_for_status()
    resp = resp.json()
    ret = {k: {_v: resp[k][0][_v] for _v in v} for k, v in key_selection.items()}

    return str(ret)


if __name__ == '__main__':
#以标准I/0 方式运行 MCP 服务器"
    mcp.run(transport='stdio')