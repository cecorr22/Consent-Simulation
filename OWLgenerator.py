from owlready2 import *
import types

class OWLgenerator:

	def __init__(self, iri):
		#loads/creates ontology with given iri
		self.onto = get_ontology(iri).load()

	'''returns class in the ontology
	mainly so methods creating classses can access classes passed in as stirngs in perameters
	assumes c is either a string or a class'''
	def getClass(self, c):
		if isinstance(c, str):
			return self.onto[c]
		else:
			return c


	'''creates a consent class of the given name using classes D, U, T, and R passed in all as strings
	if retroactive is True, consent will be retroactive, otherwise will be non retroactive'''
	def Consent(self, Dx, Uy, Tz, Rw, className, retroactive=True):
		if retroactive:
			#is subsumed by (T and U) or access(D)
			#classes do not intersect when created as below:
			className = types.new_class(className, (Thing, (self.getClass(Tz) and self.getClass(Uy)) or self.onto.access.some(self.getClass(Dx))))
			className.is_a.append(self.onto.rConsent)

			# #created using a list, metaclass conflict
			# className = types.new_class(className, (Thing, [(self.getClass(Tz) and self.getClass(Uy)) or self.onto.access.some(self.getClass(Dx))]))
			# className.is_a.append(self.onto.rConsent)
		else:
			#non-retroactive Consent: subsumed by (T and U) or access(D and T)
			className = types.new_class(className, (Thing, (self.getClass(Tz) and self.getClass(Uy) or self.onto.access.some((self.getClass(Dx) and self.getClass(Tz))))))
			className.is_a.append(self.onto.nrConsent)

			# #created using a list
			# className = types.new_class(className, (Thing, [(self.getClass(Tz) and self.getClass(Uy)) or self.onto.access.some((self.getClass(Dx) and self.getClass(Tz)))]))
			# className.is_a.append(self.onto.rConsent)

		#is equivalent to (T and U)
		is_equivalent = self.onto[self.getClass(Tz) and self.getClass(Uy)]

		return className

	'''creates a withdrawal class of name className using classes D, U, T, and R passed in all as strings
	creates retroactive/non-retroactive withdrawal if retroactive argument is True/False'''
	def Withdrawal(self, Dx, Uy, Tz, Rw, className, retroactive=True):
		if retroactive:
			#is subsumed by (T and U) and not access(D)
			className = types.new_class(className, (Thing, (self.getClass(Tz) and self.getClass(Uy)) and Not(self.onto.access.some(self.getClass(Dx)))))
			# className = types.new_class(className, (Thing, (self.getClass(Tz) and self.getClass(Uy))))
			# className.is_a.append(Not(self.onto.access.some(self.getClass(Dx))))
		else:
			#non-retroactive Consent: subsumed by (T and U) and not access(D and T)
			className = types.new_class(className, (Thing, (self.getClass(Tz) and self.getClass(Uy) and  Not(self.onto.access.some((self.getClass(Dx) and self.getClass(Tz)))))))

		#is equivalent to (T and U)
		is_equivalent = self.onto[self.getClass(Tz) and self.getClass(Uy)]

		return className


	'''creates a dataCollection individual of passed in types D, U, R, and T'''
	def createDataCollection(self, name, Dx, Uy, Tz, Rw):
		classD = self.getClass(Dx)
		individual = classD(name)
		individual.is_a.extend((self.getClass(Uy), self.getClass(Tz), self.getClass(Rw)))

		return individual

	'''creates a data access individual at R and T and access value dataCollection
	dc must be passed in as a dataCollection object, not a string'''
	def createDataAccess(self, name, dc, Tz, Rw):
		classT = self.getClass(Tz)
		individual = classT(name)
		individual.is_a.extend((self.getClass(Rw), self.onto.access.value(dc)))

		return individual

	'''uses a reasoner to make inferences'''
	def reason(self):
		with self.onto:
			sync_reasoner()

	'''saves KB to owl file'''
	def save(self, filename):
		self.onto.save(filename)


if __name__ == "__main__":
	my_onto = OWLgenerator("file://C:/Users/Cassidy/Documents/consentSimulation.owl")
	
	
	''' test to check things'''
	#test getClass with string passed in
	# T = my_onto.getClass("T1")
	# print("Class T1: ", T)

	# #testing consents and withdrawals
	# rC1 = my_onto.Consent("D1", "U1", "T1", "R1", "rC1")
	# nrC1 = my_onto.Consent("D1", "U1", "T1", "R1", "nrC1", False)
	# # rW1 = my_onto.Withdrawal("D1", "U1", "T1", "R1", "rW1")
	# # nrW1 = my_onto.Withdrawal("D1", "U1", "T1", "R1", "nrW1", False)

	# #testing getClass with class passed in
	# testClass = my_onto.getClass(rC1)
	# print("Class rC1: ", testClass)

	# print(rC1)
	# print(nrC1)
	# # print(rW1)
	# # print(nrW1)

	# dc1 = my_onto.createDataCollection("dc1", "D1", "U1", "T1", "R1")
	# da1 = my_onto.createDataAccess("da1", dc1, "T1", "R1")

	# print(dc1)
	# print(da1)


	#Creating scenario 1
	print("Scenario 1: revocation")

	#Scenario 1 (and 2) step 1: consent by U1 to data collection of D1 for R1 at T1
	rC1 = my_onto.Consent("D1", "U1", "T1", "R1", "rC1")
	# print("rC1 classes: ", rC1.is_a)

	#s1 (and 2) step 2: data is collected for D1 and U1 at T1 for R1
	dc1 = my_onto.createDataCollection("dc1", "D1", "U1", "T1", "R1")

	#s1 step 3: data is collected for D1 and U1 at T2 for R1
	dc2 = my_onto.createDataCollection("dc2", "D1", "U1", "T2", "R1")

	#s1 step 4: withdraw consent by U1 at T3 for data collection D1 for R1
	#TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
	# nrW1 = my_onto.Withdrawal("D1", "U1", "T3", "R1", "nrW1", False)

	#s1 step 5: collect data D1 U1 at T3 (violtes cosnent)
	dc3 = my_onto.createDataCollection("dc3", "D1", "U1", "T3", "R1")

	print("rC1 type: ", type(rC1))
	print("dc1 type: ", type(dc1))


	#testing dataAccess instances in saved files:
	# da1 = my_onto.createDataAccess("da1", dc1, "T1", "R1")

	# print("\ndata collection 1 initial classes: ", dc1.__class__)

	my_onto.reason()

	# print("\ndata collection1 after reasoner: ", dc1.__class__)

	my_onto.save("or2s1.owl")
