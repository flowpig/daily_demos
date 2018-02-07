
### python单元测试

数据驱动测试，也就是人们常说的黑盒测试。这里我主要学习python的单元测试unittest。测试框架使用unittest和ddt相结合的方式。

python中，unittest测试框架如下：

	import unittest

	class MyTestCase(unittest.TestCase):
	    def setUp(self):
	        '''
	        testcase init ...
	        :return:
	        '''
	        print 'setup'
	
	    def test_sth(self):
	        '''
	        must use test_***
	        :return:
	        '''
	        print 'test something' 
	
	    def tearDown(self):
	        '''
	        testcase release ...
	        :return:
	        '''
	        print 'teardown'
	
	
	if __name__ == '__main__':
	    unittest.main()

主要由三部分组成，setup，testcase和teardown。Setup过程，是测试用例执行前的初始化过程，teardown过程，是在测试用例执行后，对资源进行释放与回收的过程；而testcase是具体的测试用例。

-----------------------------------------------------
引入ddt框架，需要安装ddt模块

	import unittest
	import ddt
	
	@ddt.ddt
	class MyTestCase(unittest.TestCase):
	    def setUp(self):
	        '''
	        testcase init ...
	        :return:
	        '''
	        print 'setup'
	
	    @ddt.data(['t1', 'r1'],
	              ['t2', 'r2'])
	    @ddt.unpack
	    def test_sth(self, testdata, expectresult):
	        '''
	        must use test_***
	        :return:
	        '''
	        print 'test something'
	        print '%s - %s' %(testdata, expectresult)
	
	    def tearDown(self):
	        '''
	        testcase release ...
	        :return:
	        '''
	        print 'teardown'
	        print
	
	
	if __name__ == '__main__':
	    unittest.main()

首先在头部导入ddt，其次在测试类前声明使用ddt(@ddt.ddt)，第三步，在测试方法前，使用@ddt.data和@ddt.unpack进行装饰。而测试数据，在data中进行添加，该demo，有两条测试数据，每条测试数据有两个字段，第一个是测试数据，第二个是期望的测试结果。从代码中，可以看到，我们在测试用例的实体中并没有使用循环。看看执行如何：

	setup
	test something
	t1 - r1
	teardown
	
	
	setup
	test something
	t2 - r2
	teardown

从结果来看，测试结果有两条测试用例被执行，而非一条测试用例。也就是测试框架，自动将测试数据分在两条测试用例里来执行。



举个示例如下：

	class InterfaceTest(unittest.TestCase):
	    """
	    采集接口测试用例类
	    """
	
	    # 初始化工作
	    def setUp(self):
	        self.db = PonyDatabase()
	        if not self.db.provider:
	            self.db.bind('mysql', host=DATABASE['db_host'], db=DATABASE['db_name'],
	                         user=DATABASE['db_user'], passwd=DATABASE['db_pwd']
	                         )
	            self.db.generate_mapping(create_tables=False)
	
	    # 退出清理工作
	    def tearDown(self):
	        gc.collect()

	@ddt
	class FetchJxlTest(InterfaceTest):

	    user_id = str(uuid.uuid4())
	
	    @data(
	        [{"user_id": user_id, "name": u"李自龙", "id_card_num": "620525199101150050", "phone_num": "18615999991"},
	         {'status': 'success'}])
	    @unpack
	    def test_jxl_black(self, test_data, expect_data):
	        """聚型立黑名单测试"""
	        self.jxl_black = JxlBlackListHandler()
	        self.assertEqual(self.jxl_black.get_blacklist_data(test_data), expect_data['status'],
	                         'test jxl black fetch failed')

这里退出清理工作使用了python的gcc模块。
gc.collect()是当自动回收关闭时手动回收。默认情况垃圾回收是开启的。
self.assertEqual(firsst,second,msg=None)断定first和second是否相等，不等则抛出msg。

**注意**
测试用例里面的方法必须以test开头，否则不被unittest识别。

#### mock基本使用

mock翻译有模拟的意思，这里mock是辅助单元测试的一个模块。它允许你用模拟对象替换你的系统的部分，并对它们已使用的方式进行断言。

在python2中，mock是一个单独模块，需要单独安装。
> pip install mock

在python3中，mock已经被集成到了unittest单元测试框架中，所以，可以直接使用。

单元测试应该只针对当前单元进行测试, 所有的内部或外部的依赖应该是稳定的, 已经在别处进行测试过的.使用mock 就可以对外部依赖组件实现进行模拟并且替换掉, 从而使得单元测试将焦点只放在当前的单元功能。

**简单示例**

1.未完成add方法内的逻辑

modular.py

	#modular.py

	class Count(object):
	    def add(self):
	        pass

这里要实现一个Count计算类，add()方法要实现两数相加。但，这个功能还没有完成。这时就可以借助mock对其进行测试。

mock_demo1.py

	from unittest import mock
	import unittest
	
	from modular import Count
	
	class TestCount(unittest.TestCase):
	    def test_add(self):
	        count = Count()
	        count.add = mock.Mock(return_value=13)
	        result = count.add(8, 5)
	        self.assertEqual(result, 13)
	
	if __name__ == '__main__':
	    unittest.main()


count.add = mock.Mock(return_value=13)

通过Mock类模拟被调用的方法add()方法，return_value 定义add()方法的返回值。所以后面的语句result = count.add(8,5)里面参数不管有没有不管是多少最终都会返回13

最后，通过assertEqual()方法断言，返回的结果是否是预期的结果13

2.完成add方法的逻辑

modular.py
	class Count():

	    def add(self, a, b):
	        return a + b

修改测试用例

	from unittest import mock
	import unittest
	from modular import Count
	
	
	class MockDemo(unittest.TestCase):
	
	    def test_add(self):
	        count = Count()
	        count.add = mock.Mock(return_value=13, side_effect=count.add)
	        result = count.add(8, 8)
	        print(result)
	        count.add.assert_called_with(8, 8)
	        self.assertEqual(result, 16)
	
	if __name__ == '__main__':
	    unittest.main()


count.add = mock.Mock(return_value=13, side_effect=count.add)

side_effect参数和return_value是相反的。它给mock分配了可替换的结果，覆盖了return_value。简单的说，一个模拟工厂调用将返回side_effect值，而不是return_value。所以，这里是设置side_effect参数为Count类add()方法，就是说下面将使用传入的参数而不是像上面的和传入参数无关。

result = count.add(8,8)

这次会真正的调用add()方法，得到的返回值为16.

assert_caller_with(8,8)

检查mock方法是否获得了正确的参数。

**解决测试依赖**

例如，我们要测试A模块，然后A模块依赖于B模块的调用。但是，由于B模块的改变，导致了A模块返回结果的改变，从而使A模块的测试用例失败。其实，对于A模块，以及A模块的用例来说，并没有变化，不应该失败才对。

这个时候就是mock发挥作用的时候了。通过mock模拟掉影响A模块的部分（B模块）。至于mock掉的部分（B模块）应该由其它用例来测试。

function.py

	def add_and_multiply(x, y):
	    addition = x + y
	    multiple = multiply(x, y)
	    return (addition, multiple)

	def multiply(x, y):
	    return x * y

然后针对add_and_multiply()函数编写测试用例。
func_test.py

	import unittest
	import function
	
	class MyTestCase(unittest.TestCase):
	
	    def test_add_and_multiply(self):
	        x = 3
	        y = 5
	        addition, multiple = function.add_and_multiply(x, y)
	        self.assertEqual(8, addition)
	        self.assertEqual(15, multiple)

运行测试用例一切正常。add_and_multiply()函数依赖了multiply()函数的返回值。如果这个时候修改multiply()函数的代码。

	def multiply(x,y):
		return x * y + 3

然后再次运行测试就会失败，我们未在函数add_and_multiply()上做修改，只是因为他调用的multiply()函数改变影响了结果。我们应该把multiply()函数mock掉。

	import unittest
	from unittest.mock import patch
	import function
	
	
	class MyTestCase(unittest.TestCase):
	
	    @patch("function.multiply")
	    def test_add_and_multiply2(self, mock_multiply):
	        x = 3
	        y = 5
	        mock_multiply.return_value = 15
	        addition, multiple = function.add_and_multiply(x, y)
	        mock_multiply.assert_called_once_with(3, 5)
	
	        self.assertEqual(8, addition)
	        self.assertEqual(15, multiple)
	
	
	if __name__ == "__main__":
	    unittest.main()


@patch("function.multiply")

patch装饰/上下文管理器可以很容易地模拟类或对象在模块测试。在测试过程中，指定的这个对象将被替换为一个模拟，并在测试结束时还原。