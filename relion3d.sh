#!/bin/tcsh
#SBATCH --job-name="dyn3dclass"
#SBATCH -n 4
#SBATCH -p stagg_q
#SBATCH -o run_output.txt
#SBATCH -e run_error.txt

cd /gpfs/research/stagg/scratch/rp18j/dynaminN4particles

mpirun -np 3 `which relion_refine_mpi` --o Class3D/job001/run --i RASTR_particles0602.star --ref RASTR_particlesbin4.mrc --firstiter_cc --ini_high 30 --dont_combine_weights_via_disc --pool 3 --pad 2  --ctf --ctf_corrected_ref --iter 25 --tau2_fudge 4 --particle_diameter 545 --K 8 --flatten_solvent --zero_mask --solvent_mask gauss_sphere_0bin4.mrc --oversampling 1 --healpix_order 2 --offset_range 5 --offset_step 2 --sym C1 --norm --scale  --j 1  --angpix 4.32 --limit_tilt 80
