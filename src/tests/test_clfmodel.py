import torch
from torch import nn
from ..clf.model import StellarNet

spectra = torch.rand(32, 1, 343)
context = torch.rand(32, 2)

model = StellarNet(input_channels=spectra.shape(2))
output = model(spectra, context)