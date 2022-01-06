import os 
import glob
import shutil
import svtools as sv
import argparse


def load_args():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--t1',type=str,help='t1 path')
    parser.add_argument('--outdir',type=str,help='outdir to save output files and mni parcellated t1')
    args = parser.parse_args()
    
    return args     

def main():
    
    args = load_args()
    
    t1 = args.t1
    outdir = args.outdir + "/"
    assert os.path.exists(t1)
    os.makedirs(outdir, exist_ok=True)
    
    # get paths 
    mni, hammers = get_atlas_paths()
    
    # copy mni and hammers to outdir 
    shutil.copyfile(mni, outdir+os.path.basename(mni))
    shutil.copyfile(hammers, outdir+os.path.basename(hammers))

    # copy t1 to outdir 
    t1_newname=outdir+os.path.basename(t1)
    shutil.copyfile(t1, t1_newname)
    t1 = t1_newname
    assert os.path.exists(t1)
    
    # rename paths after copy 
    mni = outdir + "/"+ os.path.basename(mni)
    hammers = outdir + "/"+ os.path.basename(hammers)
    assert os.path.exists(mni)
    assert os.path.exists(hammers)

    # convert t1 to .nii.gz if necessary 
    if t1.endswith(".nrrd"):
        sv.crl_convert_format(t1, ".nii.gz")
        t1 = t1.replace(".nrrd", ".nii.gz")
        assert os.path.exists(t1)

    # run flirt 
    areg_mat = flirt(t1, mni)

    # run fnirt 
    warp = fnirt(t1, mni, areg_mat)    

    # invert warp 
    warp_inv = invert_warp(warp, t1)    

    # apply transformation to mni and hammers
    mni_tr = apply_warp2(mni,t1, warp_inv, "spline", "_mni.nii.gz")
    hammers_tr = apply_warp2(hammers,t1, warp_inv, "nn", "_hammers.nii.gz")

    # Verbose
    print("\n\n\n\nMNI<>T1 alignment complete. View files:")
    sv.itksnap([t1,mni,mni_tr, hammers, hammers_tr], seg=hammers_tr, remote=True)       

        
def apply_warp2(invol, refvol, warp, interp, suffix):
    
    """
    diff to apply_warp() - renames invol according to refvol basename + suffix
    
    invol(str): volume to warp (e.g. mni or hammers)
    refvol (str): volume reference (t1)
    warp (str): inverted warp file (fnirt output after inversion of the warp)
    interp (str): trilinear, nn, sinc, spline 
    
    """
    assert interp in ["trilinear", "nn", "sinc", "spline"]
    
    in_="--in="+invol
    #outvol=invol.replace(".nii.gz", "_reg.nii.gz")
    outvol=refvol.replace(".nii.gz", suffix)
    out="--out="+outvol
    ref="--ref="+refvol
    warp_="--warp="+warp
    interp_="--interp="+interp
    cmd = ["applywarp", in_, out, ref, warp_, interp_]
    sv.execute(cmd)
    print(f"...finished transformation for {invol}")


    return outvol    

def invert_warp(warp, ref):
    
    """
    
    ref(str): path to t1 file (must be a reference)
    
    """
    
    in_ = "--warp="+warp
    warp_inv = warp.replace(".nii.gz", "_inv.nii.gz")
    out="--out="+warp_inv
    ref_="--ref="+ref
    cmd = ["invwarp", in_, out, ref_]
    sv.execute(cmd)
    
    print("...finished inversion of warp")
    
    return warp_inv 
    
def fnirt(invol, refvol, matout):
    
    """
    invol (str): path to t1
    refvol (str): path to mni
    matout (str): path to affine transformation matrix output from flirt
    """
    
    print("performing fnirt")
    pass

    in_="--in="+invol
    out=invol.replace(".nii.gz", "_nreg.nii.gz")
    ref="--ref="+refvol
    aff="--aff="+matout
    interp="--interp=linear"    
    iout="--iout="+out
    cmd = ["fnirt", in_, ref, aff, interp, iout]
    sv.execute(cmd)
    print("...finished fnirt")
    
    warp = invol.replace(".nii.gz", "_warpcoef.nii.gz")
    assert os.path.exists(warp)
    
    return warp
    
def flirt(invol, refvol):
    
    """
    invol (str): path to input volume (t1)
    refvol (str): path to refrence volume (mni)
    """
    
    print("performing flirt")
    outvol = invol.replace(".nii.gz", "_reg.nii.gz")
    matout = os.path.dirname(invol) + "/"+ "invol2refvol.mat"
    
    cmd = ["flirt", "-in", invol, "-ref", refvol, "-out", outvol, "-omat", matout, "-dof", "6", "-cost", "mutualinfo"]
    
    sv.execute(cmd)
    print("...finished flirt")
    
    return matout
    
def get_atlas_paths():
    
    atlas_dir = "atlases/"
    
    hammers_path = atlas_dir + "Hammers_mith-n30r95-MaxProbMap-full-MNI152-SPM12_resamp.nii.gz"
    mni_path = atlas_dir + "MNI152_T1_1mm_brain.nii.gz"
    
    assert os.path.exists(hammers_path)
    assert os.path.exists(mni_path)
    
    return mni_path, hammers_path

if __name__=='__main__':
    
    main()