from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

## Documentation for Selenium at https://selenium-python.readthedocs.io/

class ChromeBrowser:
	def __init__(self, path = None):
		if path != None:
			self.driver = webdriver.Chrome(executable_path = path)
		elif path == None:
			self.driver = webdriver.Chrome()
		self.driver.maximize_window()
			
	def __getattr__(self, name):
		return getattr(self.driver, name)
	
	def back(self):
		self.driver.back()
		
	def forward(self):
		self.driver.forward()
		
	def saveAs(self, htmlFile, rendered = False, encoding = "utf8"):
		## Fix for weird encoding adapted from
		## https://stackoverflow.com/a/6048203
		f = open(htmlFile, "w")
		if rendered == False:
			f.write(self.driver.page_source.encode(encoding))
		else:
			## Adapted from https://stackoverflow.com/a/26819950
			f.write(self.driver.execute_script("return document.documentElement.outerHTML").encode(encoding))
		f.close()
	
	def goto(self, URL):
		self.driver.get(URL)
		
	def close(self):
		self.driver.close()
		
	def validatekwargs(self, kwargs):
		kwargs = kwargs.items()
		if len(kwargs) != 1:
			raise ValueError("Must have one keyword argument")
		else:
			method, parameter = kwargs[0]
			validMethods = ["id", "name", "xpath", "link_text", "partial_link_text", "tag_name", "class_name", "css_selector"]
			if method not in validMethods:
				raise ValueError("Keyword argument must one of these (%s)" % ", ".join(validMethods))
		method = method.lower().replace("_", " ")
		return method, parameter
		
	def listElements(self, **kwargs):
		linksList = []
		method, parameter = self.validatekwargs(kwargs)
		return self.driver.find_elements(method, parameter)
			
	def clickElement(self, index = 0, **kwargs):
		method, parameter = self.validatekwargs(kwargs)
		self.driver.find_elements(method, parameter)[index].click()
		
	def selectElements(self, labels, **kwargs):
		## Adapted from https://sqa.stackexchange.com/a/2258
		if type(labels) != list:
			labels = [labels]
		method, parameter = self.validatekwargs(kwargs)
		selectElement = Select(self.driver.find_element(method, parameter))
		for label in labels:
			selectElement.select_by_visible_text(label)
			
	def hoverElement(self, index = 0, **kwargs):
		method, parameter = self.validatekwargs(kwargs)
		hoverElement = self.driver.find_elements(method, parameter)[index]
		hoverAction = ActionChains(self.driver).move_to_element(hoverElement)
		hoverAction.perform()