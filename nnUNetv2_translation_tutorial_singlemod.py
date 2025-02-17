#!/usr/bin/env python
# coding: utf-8

# ## ------- How to : build a nnUNet_translation dataset -------

# In[ ]:


import numpy as np
import nibabel as nib
import shutil, json, glob, os
from tqdm import tqdm 
from concurrent.futures import ThreadPoolExecutor

# Path to datasets
data_dir = '/path_to/mr/' # contains training & validation mr.nii.gz files
target_dir = '/path_to/ct/'  # contains training & validation ct.nii.gz files

os.environ['nnUNet_results'] = '/path_to/nnUNet_translation/results/'
os.environ['nnUNet_raw'] = '/path_to/nnUNet_translation/raw/'
os.environ['nnUNet_preprocessed'] = '/path_to/nnUNet_translation/preprocessed/'

# example with 1 input modality
list_datas = sorted(glob.glob(os.path.join(data_dir, '*.nii.gz')))
list_targets = sorted(glob.glob(os.path.join(target_dir, '*.nii.gz')))

print(len(list_datas), list_datas)
print(len(list_targets), list_targets)


# #### Define dataset ID and make paths

# In[2]:


dataset_id = 1 # /!\ we will use both the dataset_id & the dataset_id + 1 (must be unique!)
dataset_data_name = 'Brain_Sample_MR'    # creates Dataset001_Brain_MR
dataset_target_name = 'Brain_Sample_CT'  # creates Dataset001_Brain_CT

# we will copy the datas
# do not use exist_ok=True, we want an error if the dataset exist already
dataset_data_path = os.path.join(os.environ['nnUNet_raw'], f'Dataset{dataset_id:03d}_{dataset_data_name}') 
os.makedirs(dataset_data_path, exist_ok = True)
os.makedirs(os.path.join(dataset_data_path, 'imagesTr'), exist_ok=True)
os.makedirs(os.path.join(dataset_data_path, 'labelsTr'), exist_ok = True)

dataset_target_path = os.path.join(os.environ['nnUNet_raw'], f'Dataset{dataset_id+1:03d}_{dataset_target_name}') 
os.makedirs(dataset_target_path, exist_ok = True)
os.makedirs(os.path.join(dataset_target_path, 'imagesTr'), exist_ok = True)
os.makedirs(os.path.join(dataset_target_path, 'labelsTr'), exist_ok = True)


# `Dataset001_Brain_MR` & `Dataset002_Brain_CT` will be located in `raw`:
# - `imagesTr` in Dataset001_Brain_MR = input
# - `imagesTr` in Dataset002_Brain_CT = target
# - both `labelsTr` contain dummy masks

# #### Copy files and create dummy masks

# In[3]:


def process_file(data_path, dataset_path, mat):
    curr_nifti = nib.load(data_path)
    filename = os.path.basename(data_path)
    if not filename.endswith('_0000.nii.gz'):
        filename = filename.replace('.nii.gz', '_0000.nii.gz')
    curr_nifti.to_filename(os.path.join(dataset_path, f'imagesTr/{filename}'))

    data = curr_nifti.get_fdata()
    # Adjust the mask as needed for your specific use case. By default, the mask is set to 1 for the entire volume.
    # This will be used for foreground preprocessing, cf https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/explanation_normalization.md
    data = np.ones_like(data)

    filename = filename.replace('_0000', '') #remove _0000 for masks
    nib.Nifti1Image(data, mat).to_filename(os.path.join(dataset_path, f'labelsTr/{filename}'))

mat = nib.load(list_datas[-1]).affine

with ThreadPoolExecutor() as executor:
    list(tqdm(executor.map(lambda data_path: process_file(data_path, dataset_data_path, mat), list_datas), total=len(list_datas)))

with ThreadPoolExecutor() as executor:
    list(tqdm(executor.map(lambda target_path: process_file(target_path, dataset_target_path, mat), list_targets), total=len(list_targets)))

#### without multithreading
# for data_path in tqdm(list_datas, total=len(list_datas)):
#     process_file(data_path, dataset_data_path, mat)

# for target_path in tqdm(list_targets, total=len(list_targets)):
#     process_file(target_path, dataset_target_path, mat)


# #### Create the dataset.json

# In[4]:


# /!\ you will need to edit this with regards to the number of modalities used;
data_dataset_json = {
    "labels": {
        "label_001": "1", 
        "background": 0
    },
    "channel_names": {
        "0": "MR",
    },
    "numTraining": len(list_datas),
    "file_ending": ".nii.gz"
}
dump_data_datasets_path = os.path.join(dataset_data_path, 'dataset.json')
with open(dump_data_datasets_path, 'w') as f:
    json.dump(data_dataset_json, f)

target_dataset_json = {
    "labels": {
        "label_001": "1",
        "background": 0
    },
    "channel_names": {
        "0": "CT",
    },
    "numTraining": len(list_targets),
    "file_ending": ".nii.gz"
}
dump_target_datasets_path = os.path.join(dataset_target_path, 'dataset.json')
with open(dump_target_datasets_path, 'w') as f:
    json.dump(target_dataset_json, f)


# #### Apply preprocessing and unpacking 

# - pip uninstall numpy blosc2
# - pip install numpy==1.24.3 blosc2
# - pip uninstall acvl-utils
# - pip install acvl-utils==0.2

# In[10]:


if 'MPLBACKEND' in os.environ: 
    del os.environ['MPLBACKEND'] # avoid conflicts with matplotlib backend  
    
os.system(f'nnUNetv2_plan_and_preprocess -d {dataset_id} -c 3d_fullres')
os.system(f'nnUNetv2_unpack {dataset_id} 3d_fullres 0')

os.system(f'nnUNetv2_plan_and_preprocess -d {dataset_id + 1} -c 3d_fullres')
os.system(f'nnUNetv2_unpack {dataset_id + 1} 3d_fullres 0')


# #### Define 2nd modality raw data as gt_segmentations of 1st modality
# ##### originally used for computing metrics / postprocessing, not sure if needed

# In[11]:


nnunet_datas_preprocessed_dir = os.path.join(os.environ['nnUNet_preprocessed'], f'Dataset{dataset_id+1:03d}_{dataset_target_name}') 
nnunet_targets_preprocessed_dir = os.path.join(os.environ['nnUNet_preprocessed'], f'Dataset{dataset_id:03d}_{dataset_data_name}') 

list_targets = glob.glob(os.path.join(f"{dataset_target_path}/imagesTr", '*'))
list_targets.sort()
list_gt_segmentations_datas = glob.glob(os.path.join(f"{nnunet_targets_preprocessed_dir}/gt_segmentations", '*'))
list_gt_segmentations_datas.sort()

print(nnunet_targets_preprocessed_dir)

for (preprocessed_path, gt_path) in zip(list_targets, list_gt_segmentations_datas):
    # here, gt_path is the path to the gt_segmentation in nnUNet_preprocessed.
    print(preprocessed_path, "->", gt_path) # ensure correct file pairing; 
    shutil.copy(src = preprocessed_path, dst = gt_path) # we use shutil.copy to ensure safety, but switching to shutil.move would be more efficient


# #### Define 2nd modality preprocessed files as ground truth of 1st modality
# ##### used in training, definitely needed

# In[12]:


list_preprocessed_datas_seg_path = sorted(glob.glob(os.path.join(nnunet_targets_preprocessed_dir, 'nnUNetPlans_3d_fullres/*_seg.npy')))

list_preprocessed_targets_path = sorted(glob.glob(os.path.join(nnunet_datas_preprocessed_dir, 'nnUNetPlans_3d_fullres/*.npy')))
list_preprocessed_targets_path = [name for name in list_preprocessed_targets_path if '_seg' not in name]

for (datas_path, targets_path) in zip(list_preprocessed_datas_seg_path, list_preprocessed_targets_path):
    print(targets_path, "->", datas_path)
    shutil.copy(src = targets_path, dst = datas_path) 


# #### That's it!
# You should be able to start training with : 
# ```
# export nnUNet_raw="/data/alonguefosse/nnUNet/raw"
# export nnUNet_preprocessed="/data/alonguefosse/nnUNet/preprocessed"
# export nnUNet_results="/data/alonguefosse/nnUNet/results"
# 
# nnUNetv2_train 50 3d_fullres 0 -tr nnUNetTrainerMRCT
# ```

# In[ ]:




