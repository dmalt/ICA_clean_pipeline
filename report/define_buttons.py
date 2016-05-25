import os
# Read log and extract suggested ICs to exclude
ecg_inds_log= []
eog_inds_log = []
muscle_inds_log = []
if os.path.isfile(log_filename):
    log = open(log_filename, 'r')
    log_lines = log.readlines()[:-3]
    log.close()
    import re
    inds = []
    for log_line in log_lines:
        # match = re.findall(r'(\[|,\s?)(\d*)(,\s?|\])', line)
        match = re.search(r'((EOG|ECG|Muscles)).*', log_line)
        if match:
            IC_type = match.group(1)
            exclude =  match.group()
            ICs = re.findall(r'\d+', exclude)
            if ICs:
#                 print ICs
                for entry in ICs:
                    inds.append(int(entry))

                if IC_type == 'ECG':
                    ecg_inds_log = inds[:]
                elif IC_type == 'EOG':
                    eog_inds_log = inds[:]
#                 elif IC_type == 'Muscles':
#                     muscle_inds_log = inds
                inds = []

# Define widgets for ICs selection with defaults from log
# compDict = 
# for iComp in range(ica.n_components):
third_N = ica.n_components_ / 3 + 1
print "Number of ICA components: " + str(ica.n_components_)
sel_range = range(third_N)

comp_sel_ecg = [ widgets.SelectMultiple(
#     description="(ECG): ",
    options= [ j + third_N * i for j in sel_range if j + third_N * i < ica.n_components_],
    width='60px',
    height=str(18 * third_N) + 'px',
) for i in range(3) ]



comp_sel_eog = [ widgets.SelectMultiple(
#     description="(ECG): ",
    options= [j + third_N * i for j in sel_range if j + third_N * i < ica.n_components_],
    width='60px',
    height=str(18 * third_N) + 'px',
) for i in range(3) ]

comp_sel_emg = [ widgets.SelectMultiple(
#     description="(ECG): ",
    options= [j + third_N * i for j in sel_range if j + third_N * i < ica.n_components_],
    width='60px',
    height=str(18 * third_N) + 'px',
) for i in range(3) ]

for i in range(3):
    comp_sel_ecg[i].value = value=[k for k in ecg_inds_log if third_N * i <= k < third_N * (i + 1) ]
    comp_sel_eog[i].value = value=[k for k in eog_inds_log if third_N * i <= k < third_N * (i + 1) ]
    comp_sel_emg[i].value = []


    
def on_button_clicked(b):
    if b.sel == 'ecg':
        comp_sel_ecg[b.num].value = []
    elif b.sel == 'eog':
        comp_sel_eog[b.num].value = []
    elif b.sel == 'emg':
        comp_sel_emg[b.num].value = []
        
from ipywidgets.widgets import HBox, VBox
buttons_ecg = [widgets.Button(description='Clear ECG ' + str(i + 1), width='85px', sel='ecg', num=i) for i in range(3)]
buttons_eog = [widgets.Button(description='Clear EOG ' + str(i + 1), width='85px', sel='eog', num=i) for i in range(3)]
buttons_emg = [widgets.Button(description='Clear EMG ' + str(i + 1), width='85px', sel='emg', num=i) for i in range(3)]

header_ecg = widgets.HTML(value='<h2>ECG components</h2>')
header_eog = widgets.HTML(value='<h2>EOG components</h2>')
header_emg = widgets.HTML(value='<h2>EMG components</h2>')

box_ecg = VBox([header_ecg] + [HBox(buttons_ecg)] + [HBox(comp_sel_ecg)])
box_eog = VBox([header_eog] +[HBox(buttons_eog)] + [HBox(comp_sel_eog)])
box_emg = VBox([header_emg] +[HBox(buttons_emg)] + [HBox(comp_sel_emg)])
box_ecg.border_style = 'dotted'
box_ecg.border_radius = '14px'

box_eog.border_style = 'dotted'
box_eog.border_radius = '14px'
box_emg.border_style = 'dotted'
box_emg.border_radius = '14px'
# box_ecg.background_color ='cyan'
box = HBox([box_ecg, box_eog, box_emg])