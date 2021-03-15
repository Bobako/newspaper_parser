from threading import Thread
import time
from random import randint

#инпут разделить на потоки и с каждым элемнтом произвести фанк

class Controller(Thread):
	units = []
	results = {}
	save_thread = None
	need_to_save = False
	done = False
	transferred = 0
	saved = 0
	proccessed = 0
	max_time = 80
	working = 0
	ignore_save_c =False

	log = {'start_time':time.localtime(),
		   'start_time_s':time.mktime(time.localtime()),
		   'iterations':0,
		   'progress': 0}

	def __init__(self, n_units, inputs_, func, save_func, save_freq):
		self.inputs_ = inputs_
		self.l = len(inputs_)
		if self.l < n_units:
			self.n_units = self.l

		else:
			self.n_units = n_units
		self.func = func
		
		if save_freq != 0:
			self.save_func = save_func
			self.save_freq = save_freq
			self.need_to_save = True

		Thread.__init__(self)
		self.start()
		print('Controller initializated')


	def append_units(self):
		first = self.inputs_[:self.n_units]
		self.inputs_= self.inputs_[self.n_units:]
		for i in range (self.n_units):
			self.units.append(Unit([first[i],i],self.func))
		self.transferred = self.n_units


	
	def refresh(self,i):
		
		#self.units[i] = None
		if len(self.inputs_)>0:
			self.units[i] = Unit([self.inputs_[0],self.transferred],self.func)
			self.transferred+=1
			self.inputs_ = self.inputs_[1:]

	def check(self,i):
		if self.units[i].checked:
			return 0
		if ((self.need_to_save) and (self.units[i].result!=None)):	
			self.results[self.units[i].input_id] = self.units[i].result
		self.units[i].checked = True
		self.proccessed +=1

	def control_iteration(self):
		self.working=0
		for i in range(self.n_units):
			if self.units[i].done:

				self.check(i)
				
				
				self.refresh(i)
			
			elif self.delta_time(i)>= self.max_time:
				self.units[i].result = False
				self.check(i)
				self.refresh(i)

			else:
				self.working+=1

	def delta_time(self,i):
		return (time.mktime(time.localtime()) - self.units[i].start_time)


	def save_results(self):
		if self.need_to_save== False:
			return 0
		try:
			save_done = self.save_thread.done
		except Exception:
			save_done = True
		saving = []

		if self.ignore_save_c:
			keys_ = list(self.results.keys())
			for key in keys_:
				saving.append(self.results[key])
				

		elif ((len(self.results)>=self.save_freq)and save_done):
			
			for i in range(self.saved,self.saved+len(self.results)):
				try:
					saving.append(self.results.pop(i))
					
				except Exception:
					break


			self.saved +=len(saving)
			
			self.save_thread = Unit([saving,0],self.save_func)


	def control(self):
		k = 0 #переработать
		while ((self.proccessed<self.l) or (self.done!= True)):
			if (self.proccessed>=self.l):
				self.done = True

			self.control_iteration()
			self.save_results()
			k+=1
			if k/100==k//100:
				print('Процесс завершен на',(self.proccessed/self.l)*100,'%. С момента запуска прошло',time.mktime(time.localtime())-self.log['start_time_s'] ,'секунд. В буфере',len(self.results),'значений.В работе',self.working,'потоков.')
				#time.sleep(0.5)

	def run(self):
		self.append_units()
		self.control()

		#self.finish()

		self.wait_for_saving()

	def finish(self):
		r = []
		for i in range(len(self.results)):
			r +=[self.results[i]]

		print(r)


	def wait_for_saving(self):
		self.save_freq = 0

		while self.saved<self.l:
			self.save_results()
			time.sleep(2)
			print('Идет сохранение. Осталось ',self.l - self.saved,'элементов.')

		print('Сохранение завершено')


class Unit(Thread):

	done = False
	result = None
	input_id = None
	checked = False

	def __init__(self, input_, func):
		
		self.input_ = input_[0]
		self.input_id = input_[1]
		self.func = func

		Thread.__init__(self)

		self.start_time = time.mktime(time.localtime())
		self.start()

	def run(self):
		self.result = self.func(self.input_)
		self.done = True
