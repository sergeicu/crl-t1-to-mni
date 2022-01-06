# set fixed vars
dd=<full_path_to_crl_pipeline_output_folder> 
t1=$dd/crl/common-processed/anatomical/04-Masked/t1w_ref_masked.nrrd # path to preprocessed (masked) t1 image with crl pipeline
mni=$dd/crl/common-processed/anatomical/05-MNI # output directory name - suggested
mkdir $mni

# register t1 to mni 
python register_to_mni.py --t1 $t1 --outdir $mni