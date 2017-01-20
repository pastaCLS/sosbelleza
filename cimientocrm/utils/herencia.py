class A(object):
	def __init__(self):
		self.algo = "fruta"

class Papa(A):
	def __init__(self):
		print self.mro()
		print "--> Desde {}: {}".format(self.__class__.__name__, self.fruta)

class B(Papa):
	pass

class C(Papa):
	pass

if __name__ == "__main__":
	obj = B()
