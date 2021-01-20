import inspect
from nseta.common.commons import *
from nseta.common.log import tracelog

@tracelog
def multithreaded_scan(**args):
	frame = inspect.currentframe()
	args, _, _, kwargs_main = inspect.getargvalues(frame)
	del(kwargs_main['frame'])
	kwargs = kwargs_main['args']
	items_segment = kwargs['items']
	# Max number of items to be processed at a time by a thread
	n = kwargs['max_per_thread']
	if len(items_segment) > n:
		kwargs1 = dict(kwargs)
		kwargs2 = dict(kwargs)
		first_n = items_segment[:n]
		remaining_items = items_segment[n:]
		# n_segmented_items = [items_segment[i * n:(i + 1) * n] for i in range((len(items_segment) + n - 1) // n )]
		kwargs1['items'] = first_n
		kwargs2['items'] = remaining_items
		t1 = ThreadReturns(target=multithreaded_scan, kwargs=kwargs1)
		t2 = ThreadReturns(target=multithreaded_scan, kwargs=kwargs2)
		t1.start()
		t2.start()
		t1.join()
		t2.join()
		list1 = t1.result
		list2 = t2.result
		df1 = list1.pop(0)
		df2 = list2.pop(0)
		signaldf1 = list1.pop(0)
		signaldf2 = list2.pop(0)
		df = concatenated_dataframe(df1, df2)
		signaldf = concatenated_dataframe(signaldf1, signaldf2)
		return [df, signaldf]
	else:
		callbackMethod = kwargs['callbackMethod']
		del(kwargs['callbackMethod'])
		return callbackMethod(**kwargs)
