from functools import partial

import torch
import imageio
import numpy as np

import dphsir.solvers.fns.cs as cs
from dphsir import degrades
from dphsir.denoisers.wrapper import GRUNetDenoiser
from dphsir.solvers import callbacks
from dphsir.solvers.base import ADMMSolver, HQSSolver
from dphsir.solvers.params import admm_log_descent
from dphsir.utils.io import loadmat
from dphsir.metrics import mpsnr

path = 'Lehavim_0910-1717.mat'
data = loadmat(path)
gt = data['gt']

degrade = degrades.cs.CASSI()
low = degrade(gt)
mask = degrade.mask

device = torch.device('cuda:0')
model_path = 'grunet.pth'
denoiser = GRUNetDenoiser(model_path).to(device)

init = partial(cs.init, mask=mask)
prox = cs.Prox(mask).to(device)
denoise = denoiser
solver = ADMMSolver(init, prox, denoise).to(device)

rhos, sigmas = admm_log_descent(sigma=max(0.255/255., 0),
                                iter_num=24,
                                modelSigma1=50, modelSigma2=45,
                                w=1)

int = callbacks.GatherIntermediates(filter=lambda ctx: np.uint8(ctx['x'][0,20,:,:].cpu().numpy()*255))
pbar = callbacks.ProgressBar(24)

pred = solver.restore(low, iter_num=24, rhos=rhos, sigmas=sigmas,
                      callbacks=[pbar, int])

imageio.mimsave('moive.mp4', int.intermediates, fps=5)

print(pred.shape)
print(mpsnr(init(low), gt))
print(mpsnr(pred, gt))
# Expect: 39.18
