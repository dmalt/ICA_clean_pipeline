def get_ECG_EOG_chnames_by_SubjID(Subj_ID):	
	import xlrd
	import os
	from params import main_path
	# import re
	table_name = 'Aut_gamma_EO_EC_Timing.xls'
	# print(main_path)
	table_name = main_path + table_name

	eo_ec_table = xlrd.open_workbook(table_name)
	if Subj_ID[0] == 'R':
		sheet = eo_ec_table.sheet_by_name('ASD')
	elif Subj_ID[0] == 'K':
		sheet = eo_ec_table.sheet_by_name('Control')
	else:
		print 'Can\'t find subject with ID ' + Subj_ID + '\n'
		print 'Subj_ID should start either with R or with K'


	# Subj_ID = 'K0009'

	iSID_col = sheet.row_values(0).index('Subj_ID')
	lSID = sheet.col_values(iSID_col)
	iSID = lSID.index(Subj_ID)
	iECG = sheet.row_values(0).index('ECG')
	ECG_name = sheet.cell_value(iSID, iECG)
	iEOG = sheet.row_values(0).index('EOG')
	EOG_names = sheet.cell_value(iSID,iEOG)
	# EOG_names = re.findall('(EOG[0-9]{3})',EOG_string)
	# print(ECG_name)
	# print(EOG_names)
	if ECG_name == 'N/A':
		print("For " + Subj_ID + " ECG channel name is not defined")	
	if EOG_names == 'N/A':
		print("For " + Subj_ID + " EOG channel names are not defined")	

	if ECG_name == 0.0:
		print("For" + Subj_id + " ECG channel name equals 0.0. probably it was defined with a formula in excel table")
	if EOG_names == 0.0:
		print("For" + Subj_id + " EOG channel name equals 0.0. probably it was defined with a formula in excel table")

	ECG_name = ECG_name.encode('ascii')
	EOG_names = EOG_names.encode('ascii')

	print("ECG and EOG channel names for " + Subj_ID + ":")
	print("ECG:	" + ECG_name)
	print("EOG:	" + EOG_names)

	if EOG_names == "EOG061,EOG062" or EOG_names == "EMG065,EMG066,EMG067,EMG068":
		return ECG_name, EOG_names
	else:
		print("EOG ch_name " + EOG_names + " is bad (probably, there's space after comma)")
		return



def get_eo_ec_by_name(Subj_ID, cond):

	import xlrd
	import os
	from params import main_path
	table_name = 'Aut_gamma_EO_EC_Timing.xls'
	# print(main_path)
	table_name = main_path + table_name
	eo_ec_table = xlrd.open_workbook(table_name)

	if Subj_ID[0] == 'R':
		sheet = eo_ec_table.sheet_by_name('ASD')
	elif Subj_ID[0] == 'K':
		sheet = eo_ec_table.sheet_by_name('Control')
	else:
		print 'Can\'t find subject with ID ' + Subj_ID + '\n'
		print 'Subj_ID should start either with R or with K'

	iSID_col = sheet.row_values(0).index('Subj_ID')
	lSID = sheet.col_values(iSID_col)

	iSID = lSID.index(Subj_ID)
	if cond == "eo":
		iCondStart = sheet.row_values(0).index('EO S')
	elif cond == "ec":
		iCondStart = sheet.row_values(0).index('EC S')
	CondStart = sheet.cell_value(iSID, iCondStart)
	CondEnd = sheet.cell_value(iSID, iCondStart + 1)

	iFirst_samp = sheet.row_values(0).index('#f')
	first_samp = sheet.cell_value(iSID, iFirst_samp)
	lCondStart = []
	lCondEnd = []

	while CondStart:
		lCondStart.append(CondStart)
		lCondEnd.append(CondEnd)
		iCondStart +=2
		CondStart = sheet.cell_value(iSID, iCondStart)
		CondEnd = sheet.cell_value(iSID, iCondStart + 1)
	print(cond + " start times: " )
	print(lCondStart)
	print(cond + " end times: ")
	print(lCondEnd)
	print("first sample time: ")
	print(first_samp)
	return lCondStart, lCondEnd, first_samp, cond
	



