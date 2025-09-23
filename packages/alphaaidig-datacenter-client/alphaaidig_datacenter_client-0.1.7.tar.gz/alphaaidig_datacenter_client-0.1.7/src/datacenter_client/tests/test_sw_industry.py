from datacenter_client.tests.base import BaseClientTest
import unittest


class TestSWIndustryClient(BaseClientTest):
    """申万行业客户端测试类"""
    
    def test_page_list(self):
        """测试分页获取申万行业列表"""
        print("\n" + "=" * 50)
        print("测试申万行业客户端 - 分页获取列表")
        print("=" * 50)
        
        try:
            result = self.client.sw_industry.page_list(page=1, page_size=5)
            print(f"状态: {result.get('status')}")
            self.print_pagination_info(result)
        except Exception as e:
            print(f"测试分页获取列表时出错: {e}")
    
    def test_list(self):
        """测试获取申万行业列表"""
        print("\n" + "=" * 50)
        print("测试申万行业客户端 - 获取列表")
        print("=" * 50)
        
        try:
            result = self.client.sw_industry.list()
            print(f"状态: {result.get('status')}")
            self.print_list_info(result)
        except Exception as e:
            print(f"测试获取列表时出错: {e}")


if __name__ == "__main__":
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加单个测试方法
    # suite.addTest(TestSWIndustryClient('test_page_list'))
    suite.addTest(TestSWIndustryClient('test_list'))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)