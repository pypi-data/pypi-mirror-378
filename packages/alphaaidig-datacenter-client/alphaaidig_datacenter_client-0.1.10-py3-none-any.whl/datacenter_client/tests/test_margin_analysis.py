from datacenter_client.tests.base import BaseClientTest
import unittest


class TestMarginAnalysisClient(BaseClientTest):
    """融资融券分析客户端测试类"""
    
    def test_page_list(self):
        """测试通用分页获取融资融券分析"""
        print("\n" + "=" * 50)
        print("测试融资融券分析客户端 - 通用分页获取")
        print("=" * 50)
        
        try:
            result = self.client.margin_analysis.page_list(analysis_type="index", target_code="000300.SH", page=1, page_size=5)
            print(f"状态: {result.status}")
            self.print_pagination_info(result)
        except Exception as e:
            print(f"测试通用分页获取时出错: {e}")
    
    def test_list(self):
        """测试批量获取融资融券分析"""
        print("\n" + "=" * 50)
        print("测试融资融券分析客户端 - 批量获取")
        print("=" * 50)
        
        try:
            result = self.client.margin_analysis.list(
                analysis_type="index", 
                target_codes=["000300.SH", "000905.SH"], 
                start_date="20250101", 
                end_date="20250922"
            )   
            print(f"状态: {result.status}")
            self.print_list_info(result)
        except Exception as e:
            print(f"测试批量获取时出错: {e}")
    
    

if __name__ == "__main__":
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加单个测试方法
    suite.addTest(TestMarginAnalysisClient('test_page_list'))
    suite.addTest(TestMarginAnalysisClient('test_list'))
    # suite.addTest(TestMarginAnalysisClient('test_batch_list'))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)