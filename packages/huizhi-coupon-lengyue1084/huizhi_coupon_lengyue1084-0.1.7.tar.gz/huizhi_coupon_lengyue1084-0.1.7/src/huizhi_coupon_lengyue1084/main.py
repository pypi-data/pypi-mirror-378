
from mcp.server.fastmcp import FastMCP
# 初始化 MCP 服务器
mcp = FastMCP("CouponServer")

@mcp.tool()
def get_movie_ticket(movie_name: str, seat_number: int) -> str:
    """
    获取电影票信息
    """
    return f"电影: {movie_name}, 座位号: {seat_number}"

@mcp.tool()
def get_meal_ticket(restaurant_name: str, meal_type: str) -> str:
    """
    获取餐饮票信息
    """
    return f"餐厅: {restaurant_name}, 餐点类型: {meal_type}"

@mcp.tool()
def calculate_discount(original_price: float, discount_rate: float) -> float:
    """
    计算折扣后的价格
    """
    return original_price * (1 - discount_rate)

@mcp.tool()
def get_user_info(user_id: int) -> dict:
    """
    获取用户信息
    """
    return {
        "user_id": user_id,
        "name": "张三",
        "level": "VIP"
    }

# 添加main函数以支持命令行入口点
def main():
    """\命令行入口点函数"""
    mcp.run(transport="stdio")

if __name__ == '__main__':
    main()


