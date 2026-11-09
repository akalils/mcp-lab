import os

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("MCP Permission Learning")

ROLE = os.environ.get("DEMO_ROLE", "reader")
SHOP = os.environ.get("DEMO_SHOP", "shop-a")
if ROLE not in {"reader", "editor"} or SHOP not in {"shop-a", "shop-b"}:
    raise ValueError("INVALID_DEMO_CONFIG")

PRODUCTS = {
    "product-a": {"product_id": "product-a", "shop_id": "shop-a", "title": "A店原始标题"},
    "product-b": {"product_id": "product-b", "shop_id": "shop-b", "title": "B店原始标题"},
}

def accessible_product(product_id: str) -> dict[str, str]:
    product = PRODUCTS.get(product_id)
    if product is None or product["shop_id"] != SHOP:
        raise ValueError("ACCESS_DENIED")
    return product

@mcp.tool()
def get_access_context() -> dict[str, str]:
    """查看本进程模拟的角色和店铺"""
    return {"role": ROLE, "shop_id": SHOP}

@mcp.tool()
def get_scoped_product(product_id: str) -> dict[str, str]:
    """查询当前店铺内的商品；其他店铺和不存在的ID均拒绝"""
    return dict(accessible_product(product_id))

@mcp.tool()
def set_scoped_title(product_id: str, title: str) -> dict[str, str]:
    """只有editor可以修改当前店铺内的商品标题。"""
    if ROLE != "editor":
        raise ValueError("FORBIDDEN_WRITE")
    product = accessible_product(product_id)
    before = product["title"]
    product["title"] = title
    return {"product_id": product_id, "before": before, "after": title}

if __name__ == "__main__":
    mcp.run(transport="stdio")