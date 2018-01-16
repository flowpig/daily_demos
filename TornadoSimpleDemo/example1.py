#!/usr/bin/env python
#-*- coding:utf-8 -*-

# import tornado.ioloop
# import tornado.web
#
# class MainHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write("Hello,World!")
#
# application = tornado.web.Application([
#     (r"/index",MainHandler),
# ])
# if __name__ == '__main__':
#     application.listen(8888)
#     tornado.ioloop.IOLoop.instance().start()

#----------------------------------------------------
import tornado.ioloop
import tornado.web

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie('user'):
            self.redirect('/login')
            return
        user_list = ['tom','jack']
        user_dict = {'name':'clark'}
        self.render('index.html',user_list = user_list,user_dict = user_dict)
class LoginHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user = self.get_secure_cookie('user')
        return user
    def get(self):
        self.render('login.html',msg = '')
    def post(self):
        #取GET数据
        # print(self.get_query_argument('page'))     # 2
        # print(self.get_query_arguments('page'))    # ['2']
        #取POST数据
        # import pdb
        # pdb.set_trace()
        print(self.get_body_argument('user'))      # clark
        print(self.get_body_arguments('user'))     # ['clark']
        if self.get_body_argument('user')  == 'clark' and self.get_body_argument('pwd') == '123':
            self.set_secure_cookie('user',self.get_body_argument('user'))
            self.redirect('/index')
            return
        self.render('login.html',msg = '用户名或密码错误')

settings = {
    'template_path':'templates',
    'static_path':'static',
    "xsrf_cookies": True,
    "cookie_secret":"wqwesakdkakkak",
}
application = tornado.web.Application([
    (r"/login",LoginHandler),
    (r"/index",IndexHandler),
],**settings)
if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()