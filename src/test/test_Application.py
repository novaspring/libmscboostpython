import Msc.Boost

class MyApplication(Msc.Boost.Application):
    def _Main(self):
        print ('Executing main')

def test_Application():
    x = MyApplication()
    x.Run()
