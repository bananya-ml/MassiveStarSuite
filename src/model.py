from torch.nn import functional as F
import torch.autograd as autograd
from torch import nn
import torch

class StellarNet(nn.Module):
    def __init__(self, input_channels):
        super(StellarNet, self).__init__()
        
       # spectrum convolutional input
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=4, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=4, out_channels=16, kernel_size=5, padding=1)
        self.conv3 = nn.Conv1d(in_channels=16, out_channels=32, kernel_size=8, padding=1)
        self.pool = nn.MaxPool1d(kernel_size=2)
        
        pool_output_shape = self._compute_out_size((1,input_channels), 
                                             nn.Sequential(self.conv1, 
                                                           self.pool,
                                                           self.conv2,
                                                           self.pool,
                                                           self.conv3,
                                                           self.pool))

        self.fc01 = nn.Linear(pool_output_shape[0]*pool_output_shape[1], 128)
        self.fc02 = nn.Linear(128, 64)
        
        # context input
        self.fc11 = nn.Linear(2, 16)
        self.ln1 = nn.LayerNorm(16)
        self.fc12 = nn.Linear(16, 32)
        
        # combine outputs
        self.fc = nn.Linear(64+32, 64)
        self.output = nn.Linear(64, 1)


    def forward(self, x, y):

        # forward pass for spectrum
        x = self.pool(F.leaky_relu(self.conv1(x)))
        x = self.pool(F.leaky_relu(self.conv2(x)))
        x = self.pool(F.leaky_relu(self.conv3(x)))
        x = x.view(x.size(0), -1)
        x = F.leaky_relu(self.fc01(x))
        x = F.leaky_relu(self.fc02(x))
        
        # forward pass for context
        y = self.ln1(F.leaky_relu(self.fc11(y)))
        y = F.leaky_relu(self.fc12(y))

        out = torch.cat((x, y), 1)
        out = F.leaky_relu(self.fc(out))
        out = self.output(out)
        
        return out
    
    def _compute_out_size(self, in_size, mod):
        """
        Compute output size of Module `mod` given an input with size `in_size`.
        """
        
        f = mod.forward(autograd.Variable(torch.Tensor(1, *in_size)))
        return f.size()[1:]