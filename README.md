# nnUNetv2_translation [in progress]
nnUNetv2 adapted for image-to-image translation, based on [MIC-DKFZ/nnUNet](https://github.com/MIC-DKFZ/nnUNet).

Please cite our workshop paper when using nnU-Net_translation :

    Longuefosse, A., Le Bot, E. et al. (2024). ---- to be determined

Along with the original nnUNet paper :

    Isensee, F., Jaeger, P. F., Kohl, S. A., Petersen, J., & Maier-Hein, K. H. (2021). nnU-Net: a self-configuring 
    method for deep learning-based biomedical image segmentation. Nature methods, 18(2), 203-211.

## Tested use cases : 
- Medical cross-modality translation : MR to CT translation
- Medical image inpainting : Inpainting of brain lesions in MR
    
## How to use it : 
```bash
# I recommend creating a dedicated environment
git clone https://github.com/Phyrise/nnUNet_translation 
cd nnUNet_translation
pip install -e .
```
The `pip install` command should install the modified [batchgenerators](https://github.com/Phyrise/batchgenerators_translation) and [dynamic-network-architectures](https://github.com/Phyrise/dynamic-network-architectures_translation) repos.

-> for now, you need to do the preprocessing separately for each modality 
  1. create one dataset for each modality (e.g. Dataset_X and Dataset_Y) put some dummy segmentation (actually not dummy! either a full-mask of 1, or a mask of 1 for your foreground since normalization is based on foreground and not full mask)
  2. apply preprocessing for each dataset (nnUNetv2_plan_and_preprocess)
  3. begin training to unpack datasets in .npy (cancel after unpacking is done)
  4. remove preprocessed/Dataset*/nnUNetPlans_3d_fullres/*_seg.npy
  5. move preprocessed/Dataset_X/nnUNetPlans_3d_fullres/*.npy to preprocessed/Dataset_Y/nnUNetPlans_3d_fullres/*_seg.npy
     which means the preprocessed X volumes are used as the target for the dataset Y (= Y to X translation)
  6. also update the gt_segmentations of dataset_Y (just a copy of the raw/imagesTr of dataset X worked for me)

now you can train using : 
```bash
nnUNetv2_train DatasetY 3d_fullres 0 -tr nnUNetTrainerMRCT_mse
```

inference :
```bash
 nnUNetv2_predict -d DatasetY -i INPUT -o OUTPUT -c 3d_fullres -p nnUNetPlans -tr nnUNetTrainerMRCT_mse -f FOLD [optional : -chk checkpoint_best.pth -step_size 0.5]
```
A smaller step_size (default: 0.5) at inference can reduce some artifacts on images (especially when using perceptual loss with conv_transpose).

## TODO : 
- clean the mess
- disable cropping in preprocessing ?
- add arguments to control :
    - reconstruction mode (mean, median..)
    - network architecture (standard conv_tranpose, upsampling_nearest, up_sampling_trilinear..)
    - output channel size (for now : 1)
- adapt the preprocessing to support (volume, volume) instead of (volume,seg) as inputs
