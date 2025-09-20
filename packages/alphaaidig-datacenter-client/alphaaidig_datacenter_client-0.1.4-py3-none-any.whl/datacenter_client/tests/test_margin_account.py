from datacenter_client.tests.base import BaseClientTest
import unittest

class TestMarginAccountClient(BaseClientTest):
    """融资融券账户客户端测试类"""

    def test_page_list(self):
        """测试分页获取融资融券账户列表"""
        print("\n" + "=" * 50)
        print("测试融资融券账户客户端 - 分页获取列表")
        print("=" * 50)
        
        try:
            result = self.client.margin_account.page_list(page=1, page_size=5)
            self.print_pagination_info(result)
            self.assertIn('items', result)
            self.assertEqual(len(result.get('items', [])), 5)
        except Exception as e:
            self.fail(f"测试分页获取列表时出错: {e}")

    def test_get_by_date(self):
        """测试根据日期获取融资融券账户信息"""
        print("\n" + "=" * 50)
        print("测试融资融券账户客户端 - 根据日期获取信息")
        print("=" * 50)
        
        # 假设 '2025-09-17' 是一个有效日期
        trade_date = "2025-09-17"
        try:
            result = self.client.margin_account.get_by_date(trade_date)
            self.print_item_info(result)
            self.assertIn('trade_date', result)
            self.assertEqual(result.get('trade_date'), trade_date)
        except Exception as e:
            self.fail(f"测试根据日期获取信息时出错: {e}")

    def test_get_stats(self):
        """测试获取融资融券账户统计信息"""
        print("\n" + "=" * 50)
        print("测试融资融券账户客户端 - 获取统计信息")
        print("=" * 50)
        
        try:
            result = self.client.margin_account.get_stats()
            self.print_item_info(result)
            self.assertIn('total_count', result)
        except Exception as e:
            self.fail(f"测试获取统计信息时出错: {e}")


if __name__ == "__main__":
    unittest.main()