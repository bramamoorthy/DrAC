import collections

class Evaluator():
	def evaluateNeji(clinicalNotes, nejiAnnotations, showDetail=False):
		"""
		This method evaluates the Neji performance to detect drugs. 
		This evaluation only considers if the drug was detecting considering the initial span.
		Strength was not evaluated in this method.
		:param clinicalNotes: Dict of clinical notes with the following structure
			{
				"train":{
					"file name"":{
						"cn": "clinical note",
						"annotation":{
							"id":("concept","type",[(span,span), ...])
						},
						"relation":{
							"id": (type, annId1, annId2)
						}
					}
				}
				"test":{...}
			}
		:param nejiAnnotations: Dict with the neji annotations, key is the dataset (train or test), value is another dict containing the
		files name as key and a list of annotations. The annotations have the following structure: date|UMLS:C2740799:T129:DrugsBank|10
			{
				"train":{
					"file name"":["annotation"]
				}
				"test":{...}
			}
		:param showDetail: Boolean that when is set as True, the system shows all the false positives and false negatives annotations
		"""
		for dataset in clinicalNotes:
			if dataset not in nejiAnnotations:
				print ("Dataset " + dataset + " not annotated yet!")
				continue
			print("Dataset: " + dataset)
			metrics = {}
			for fileName in clinicalNotes[dataset]:
				if fileName not in nejiAnnotations[dataset]:
					print ("Note " + fileName + " not annotated! Maybe an decoding error during the annotation procedure!")
					continue
				annGSList = []
				for annID in clinicalNotes[dataset][fileName]["annotation"]:
					ann = clinicalNotes[dataset][fileName]["annotation"][annID]
					annGSList.append((ann[0], str(ann[2][0])))
				annList = []
				for ann in nejiAnnotations[dataset][fileName]:
					annList.append((ann[0],ann[2]))
				annList = list(set(annList))
				metrics[fileName] = Evaluator._calculateIndividualMetrics(annGSList, annList)
			Evaluator._calculateGlobalMetrics(metrics, showDetail)

	def _calculateIndividualMetrics(annGS, ann):
		"""
		Private method to calculate metrics individually (Precision, Recall, F1-Score) and 
		to provide metrics to global calculation (True positives, False positives, False negatives)
		:param annGS: List of tuples with the concepts and the inital span for each Drug annotation in the gold standard
		:param ann: List of tuples with the concepts and the inital span for each Drug annotated
		:return: Dict with individual and global metrics
			{
				"individual":(Precision, Recall, F1-Score)
				"global":(True positives, False positives, False negatives)
				"false_negatives": False Negatives
				"false_positives": False Positives
			}
		"""
		falseNegatives = []
		falsePositives = []
		tp = 0

		for concept, span in annGS:
			if len([annConcept for annConcept, annSpan in ann if span == annSpan]) > 0:
				tp += 1
			else:
				falseNegatives.append(concept.lower())

		for concept, span in ann:
			if len([annConcept for annConcept, annSpan in annGS if span == annSpan]) == 0:
				falsePositives.append(concept.lower())

		fn = len(annGS) - tp
		fp = len(ann) - tp
		precision = tp/(tp+fp)
		recall = tp/(tp+fn)
		f1Score = 2*((precision*recall)/(precision+recall))
		return {
				"individual":(precision, recall, f1Score),
				"global":(tp, fp, fn),
				"false_negatives":falseNegatives,
				"false_positives":falsePositives
			}

	def _calculateGlobalMetrics(metrics, showDetail):
		"""
		Private method to calculate global metrics (Precision, Recall, F1-Score) and
		show the best and worst clinical note annotation (F1-score)
		:param metrics: Dict with individual and global metrics
			{
				"file name":{
					"individual":(Precision, Recall, F1-Score)
					"global":(True positives, False positives, False negatives)
					"false_negatives": False Negatives
					"false_positives": False Positives
				}
			}
		:param showDetail: Boolean that when is set as True, the system shows all the false positives and false negatives annotations
		"""
		tp = 0
		fp = 0
		fn = 0
		best = (None, 0)
		worst = (None, 1)
		falseNegatives = []
		falsePositives = []
		for file in metrics:
			tp += metrics[file]["global"][0]
			fp += metrics[file]["global"][1]
			fn += metrics[file]["global"][2]
			if metrics[file]["individual"][2] > best[1]:
				best = (file, metrics[file]["individual"][2], metrics[file]["individual"][0], metrics[file]["individual"][1])
			if metrics[file]["individual"][2] < worst[1]:
				worst = (file, metrics[file]["individual"][2], metrics[file]["individual"][0], metrics[file]["individual"][1])
			falseNegatives.extend(metrics[file]["false_negatives"])
			falsePositives.extend(metrics[file]["false_positives"])
		precision = tp/(tp+fp)
		recall = tp/(tp+fn)
		f1Score = 2*((precision*recall)/(precision+recall))
		print("{:20}\t{:20}\t{:20}".format("Precision", "Recall", "F1-Score"))
		print("{:<20}\t{:<20}\t{:<20}".format(precision, recall, f1Score))
		print("\nThe best annotated note was: {}, with the following scores:".format(best[0]))
		print("{:20}\t{:20}\t{:20}".format("Precision", "Recall", "F1-Score"))
		print("{:<20}\t{:<20}\t{:<20}".format(best[2], best[3], best[1]))
		print("\nThe worst annotated note was: {}, with the following scores:".format(worst[0]))
		print("{:20}\t{:20}\t{:20}".format("Precision", "Recall", "F1-Score"))
		print("{:<20}\t{:<20}\t{:<20}".format(worst[2], worst[3], worst[1]))
		if showDetail:
			print("False Negatives")
			print(collections.Counter(falseNegatives))
			print("False Positives")
			print(collections.Counter(falsePositives))
		#if False: #Just to test the impact of the False Negatives in Neji
		#	for concept in set(falseNegatives):
				#UMLS:C0000120:T121:AOD	
		#		print("AdHoc:UNK:UNK:AdHoc\t{}".format(concept))
	
	def evaluateAnnotations(clinicalNotes, annotations, detailEva=False):
		pass

	def evaluateAnnotationsWithRelations(clinicalNotes, annWithRelations, detailEva=False):
		pass